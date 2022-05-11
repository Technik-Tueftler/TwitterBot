#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import datetime
import schedule
import tweepy


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
    print("Start Twitter message handler")
    verified_env_data = check_and_verify_env_variables()
    if verified_env_data["all_verified"] is not False:
        main(verified_env_data)
