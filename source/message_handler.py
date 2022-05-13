#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import datetime
import schedule
import tweepy
from source import db
import re

MESSAGE_PATTERN = r"^#?bot\s(.*)\s(https:.*)"
TWEET_URL_PATTERN = r"^(https://twitter.com/)(.+)(/status/)(\d+)$"


def decompose_tweet_url(tweet_url: str) -> dict:
    result_return = {"found_match": False,
                     "twitter_user_name": None,
                     "tweet_id": None}
    result = re.match(TWEET_URL_PATTERN, tweet_url)
    if result is not None:
        result_return["twitter_user_name"] = result.groups()[1]
        result_return["tweet_id"] = result.groups()[3]
        result_return["found_match"] = True
    return result_return


def analyze_message(tweet_text: str) -> dict:
    result_return = {"found_match": False,
                     "message": None,
                     "url": None}
    result = re.match(MESSAGE_PATTERN, tweet_text)
    if result is not None:
        result_return["message"] = result.groups()[0]
        result_return["url"] = result.groups()[1]
        result_return["found_match"] = True
    return result_return


def message_handler(communication_data: dict) -> None:
    auth = tweepy.OAuth1UserHandler(
        os.getenv("consumer_key"),
        os.getenv("consumer_secret"),
        os.getenv("access_token"),
        os.getenv("access_token_secret"))
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
    except tweepy.TooManyRequests:
        print(tweepy.TooManyRequests)
    except tweepy.Unauthorized:
        print("Anmeldedaten nicht korrekt")
    except tweepy.errors.Forbidden as err:
        print(f"Keinen vollen Zugang: {err}")


def check_and_verify_env_variables() -> dict:
    """Function controls the passed env variables and checks if they are valid."""
    environment_data = {"consumer_key": os.getenv("consumer_key"),
                        "consumer_secret": os.getenv("consumer_secret"),
                        "access_token": os.getenv("access_token"),
                        "access_token_secret": os.getenv("access_token_secret"),
                        "all_verified": True}

    if any(True for value in environment_data.values() if value is None):
        environment_data["all_verified"] = False
        print("Not all env variable are defined. Please check the documentation and add all twitter"
              "authentication information.")
    try:
        _ = datetime.datetime.strptime(os.getenv("schedule_time_every_day"), "%H:%M")
        environment_data["schedule_time_every_day"] = os.getenv("schedule_time_every_day")
        environment_data["all_verified"] &= True

    except ValueError:
        environment_data["all_verified"] &= False
        print("Wrong time format for >schedule_time_every_day<. Should be HH:MM")
    except TypeError:
        environment_data["all_verified"] &= False
        print("Env variable >schedule_time_every_day< is not defined.")

    return environment_data


def main(env_data: dict) -> None:
    schedule.every().day.at(env_data["schedule_time_every_day"]).do(message_handler, env_data)
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
            main(verified_env_data)
