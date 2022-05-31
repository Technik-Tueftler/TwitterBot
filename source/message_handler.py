#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main function to filter private messages in twitter by a keyword and then write this information to
the database. The handler becomes active regularly after a set time and reads all messages. The main
function should run later in the docker container.
"""
import os
import time
import datetime
from dataclasses import dataclass
import re
import schedule
import tweepy
from source import db

MESSAGE_PATTERN = r"^#?bot\s(.*)\s(https:.*)"
# MESSAGE_PATTERN = r"^#?tweet\s(.*)\s(https:.*)"
# MESSAGE_PATTERN = r"^#?user\s(.*)\s(https:.*)"
TWEET_URL_PATTERN = r"^(https://twitter.com/)(.+)(/status/)(\d+)$"
MAX_TWEETS_PER_PAGE = 10
MAX_PAGES = 1


@dataclass
class TwitterMessage:
    message_id: str
    message_timestamp: datetime.datetime
    sender_id: str
    message_data: dict


def decompose_tweet_url(tweet_url: str) -> dict:
    """
    Filter and extract the tweet url by name and id
    :param tweet_url: Complete url of the tweet in a str
    :return: Dictionary with information with username, tweet id and if results were found.
    """
    result_return = {"found_match": False, "twitter_user_name": None, "tweet_id": None}
    result = re.match(TWEET_URL_PATTERN, tweet_url)
    if result is not None:
        result_return["twitter_user_name"] = result.groups()[1]
        result_return["tweet_id"] = result.groups()[3]
        result_return["found_match"] = True
    return result_return


def analyze_message(tweet_text: str) -> dict:
    """
    Analyze message and check keyword and extract information.
    :param tweet_text: Complete message in a str
    :return: Dictionary with information with message, url and if results were found.
    """
    result_return = {"found_match": False, "message": None, "short_url": None}
    result = re.match(MESSAGE_PATTERN, tweet_text)
    if result is not None:
        result_return["message"] = result.groups()[0]
        result_return["short_url"] = result.groups()[1]
        result_return["found_match"] = True
    return result_return


def extract_expand_url(tweet_content) -> str:
    """
    Extract the expanded url from the tweet content. Dictionary structure:
    {'text': '#bot das ist richtig neiser schieed https://t.co/rEy33Np1N8',
    'entities': {'hashtags': [{'text': 'bot', 'indices': [0, 4]}],
                 'symbols': [],
                 'user_mentions': [],
                 'urls': [{'url': 'https://t.co/rEy33Np1N8',
                           'expanded_url': 'https://twitter.com/../status/0815',
                           'display_url': 'twitter.com/GroundedTheGam…',
                           'indices': [36, 59]}]}}

    :param tweet_content: content of the tweet as dict
    :return: Expanded url as str
    """
    try:
        return tweet_content["entities"]["urls"][0]["expanded_url"]
    except KeyError:
        return ""


def get_all_matched_messages(api_endpoint: tweepy.API) -> list:
    """
    Get all messages from twitter and check if a match found.
    :param api_endpoint: Twitter api endpoint
    :return: list with messages
    """
    matched_messages = [
        TwitterMessage(message_id=message.id, message_timestamp=message.created_timestamp,sender_id=message.message_create["sender_id"], message_data=message.message_create["message_data"])
        #  message.message_create["message_data"]
        for page in tweepy.Cursor(
            api_endpoint.get_direct_messages, count=MAX_TWEETS_PER_PAGE
        ).pages(MAX_PAGES)
        for message in page
        if analyze_message(message.message_create["message_data"]["text"])[
            "found_match"
        ]
    ]
    return matched_messages


def get_tweet_status(api: tweepy.API, tweet_id: str) -> dict:
    """
    name: Technik_Tueftler, screen_name: TTueftler
    :param api:
    :param tweet_id:
    :return:
    """
    tweet_status_data = {
        "author_user_id": None,
        "author_user_name": None,
        "author_user_screen_name": None,
        "created_at": None,
        "text": None,
    }
    try:
        tweet_status = api.get_status(tweet_id)
        tweet_status_data["author_user_id"] = tweet_status.user.id
        tweet_status_data["author_user_name"] = tweet_status.user.name
        tweet_status_data["author_user_screen_name"] = tweet_status.user.screen_name
        tweet_status_data["created_at"] = tweet_status.created_at
        tweet_status_data["text"] = tweet_status.text

    except tweepy.errors.NotFound as _:
        print(f"Tweet mit der ID: {tweet_id} nicht mehr vorhanden.")
    finally:
        return tweet_status_data  # pylint: disable=lost-exception


def message_handler(communication_data: dict) -> None:
    """
    Called regularly fetch messages and save content
    :param communication_data: Dictionary with app information.
    :return: None
    """
    auth = tweepy.OAuth1UserHandler(
        communication_data["consumer_key"],
        communication_data["consumer_secret"],
        communication_data["access_token"],
        communication_data["access_token_secret"],
    )
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials()
        results_message = get_all_matched_messages(api)
        for message_content in results_message:
            tweet_data = {
                "comment": analyze_message(message_content.message_data["text"])["message"],
                "expand_url": extract_expand_url(message_content.message_data),
            }
            decomposed_url = decompose_tweet_url(tweet_data["expand_url"])
            tweet_data["tweet_id"] = decomposed_url["tweet_id"]
            tweet_data |= get_tweet_status(api, decomposed_url["tweet_id"])
            print(tweet_data)
            if tweet_data["author_user_id"] is not None:
                db.add_tweet(tweet_data)
                db.check_and_update_user_names(tweet_data)
            else:
                db.add_deleted_tweet(
                    decomposed_url, tweet_data["expand_url"], tweet_data["comment"]
                )

    except tweepy.TooManyRequests as err:
        print(err)
    except tweepy.Unauthorized:
        print("Anmeldedaten nicht korrekt")
    except tweepy.errors.Forbidden as err:
        print(f"Keinen vollen Zugang: {err}")


def check_and_verify_env_variables() -> dict:
    """Function controls the passed env variables and checks if they are valid."""
    environment_data = {
        "consumer_key": os.getenv("consumer_key"),
        "consumer_secret": os.getenv("consumer_secret"),
        "access_token": os.getenv("access_token"),
        "access_token_secret": os.getenv("access_token_secret"),
        "all_verified": True,
    }

    if any(True for value in environment_data.values() if value is None):
        environment_data["all_verified"] = False
        print(
            "Not all env variable are defined. Please check the documentation and add all twitter"
            "authentication information."
        )
    try:
        _ = datetime.datetime.strptime(os.getenv("schedule_time_every_day"), "%H:%M")
        environment_data["schedule_time_every_day"] = os.getenv(
            "schedule_time_every_day"
        )
        environment_data["all_verified"] &= True

    except ValueError:
        environment_data["all_verified"] &= False
        print("Wrong time format for >schedule_time_every_day<. Should be HH:MM")
    except TypeError:
        environment_data["all_verified"] &= False
        print("Env variable >schedule_time_every_day< is not defined.")

    return environment_data


def main(env_data: dict) -> None:
    """
    Scheduling function for regular call.
    :param env_data: Dictionary with app information.
    :return: None
    """
    schedule.every().day.at(env_data["schedule_time_every_day"]).do(
        message_handler, env_data
    )
    print("Env data are verified, start job.")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    db.init()
    if db.DB_CONNECTION_VALID is True:
        print("Start Twitter message handler")
        verified_env_data = check_and_verify_env_variables()
        if verified_env_data["all_verified"] is not False:
            # main(verified_env_data)
            message_handler(verified_env_data)
