#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tweepy
import os
from message_handler import analyze_message, decompose_tweet_url

# re für "bot" --> ^#?bot\s(.*)
# codeschmiede --> ^(#bot)\s*(.*)$
# Luni --> ^(#bot)($|\s)(.*)$ oder ^(?<tag>#[\w\d]+)($|\s+)(?<msg>.*)$
# MESSAGE_PATTERN = r"^(#bot)($|\s)(.*)$"


def message_handler():
    auth = tweepy.OAuth1UserHandler(
        os.getenv("consumer_key"),
        os.getenv("consumer_secret"),
        os.getenv("access_token"),
        os.getenv("access_token_secret"))
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        for page in tweepy.Cursor(api.get_direct_messages, count=5).pages(1):
            for message in page:
                # print(message.created_timestamp)
                # print(message.id)
                print(message.message_create["message_data"])
                # print(message.message_create["message_data"]["text"])
                # print(message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"])
                # print(message.message_create["message_data"]["entities"]["urls"])
                results = analyze_message(message.message_create["message_data"]["text"])
                if results["found_match"]:
                    print(results)
                    print(message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"])
                    # print(api.get_status(1102566050158333952).user.id)
                    print(decompose_tweet_url(message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"]))

    except tweepy.TooManyRequests:
        print(tweepy.TooManyRequests)
    except tweepy.Unauthorized:
        print("Anmeldedaten nicht korrekt")
    except tweepy.errors.Forbidden as err:
        print(f"Keinen vollen Zugang: {err}")


if __name__ == "__main__":
    import db
    db.init()
    message_handler()
