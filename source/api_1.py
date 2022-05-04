import tweepy
import os

auth = tweepy.OAuth1UserHandler(
    os.getenv("consumer_key"),
    os.getenv("consumer_secret"),
    os.getenv("access_token"),
    os.getenv("access_token_secret"))
api = tweepy.API(auth)

try:
    api.verify_credentials()
    """messages = api.get_direct_messages(count=5)
    print(messages)"""
    for page in tweepy.Cursor(api.get_direct_messages, count=20).pages(1):
        for message in page:
            print(message.created_timestamp)
            print(message.id)
            print(message.message_create["message_data"])
            print(message.message_create["message_data"]["text"])
            print(message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"])

            # re für "bot" --> ^#?bot\s(.*)
            # codeschmiede --> ^(#bot)\s*(.*)$
            # Luni --> ^(#bot)($|\s)(.*)$ oder ^(?<tag>#[\w\d]+)($|\s+)(?<msg>.*)$

except tweepy.TooManyRequests:
    print(tweepy.TooManyRequests.response)
except tweepy.Unauthorized:
    print("Anmeldedaten nicht korrekt")
except tweepy.errors.Forbidden as err:
    print(f"Keinen vollen Zugang: {err}")
