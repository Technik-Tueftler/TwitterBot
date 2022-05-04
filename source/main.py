#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import tweepy


client = tweepy.Client(bearer_token=os.getenv("bearer_token"),
                       consumer_key=os.getenv("consumer_key"),
                       consumer_secret=os.getenv("consumer_secret"),
                       access_token=os.getenv("access_token"),
                       access_token_secret=os.getenv("access_token_secret")
                       )


def main() -> None:
    # client.create_tweet(text="Ich bin ein Bot, hallo") # Tweet absetzen
    # query_results = client.search_recent_tweets("#knorzen -is:retweet", end_time="2022-04-19T19:00:36Z")
    #query_results = client.search_recent_tweets("#knorzen -is:retweet", expansions="author_id", tweet_fields="author_id")  # Textsuche
    #query_results = client.search_recent_tweets("#knorzen -is:retweet", expansions=["author_id","referenced_tweets.id.author_id"], tweet_fields=["author_id"])  # Textsuche
    """query_results = client.search_recent_tweets(query="#knorzen -is:retweet",
                                                tweet_fields=["author_id",'context_annotations', 'created_at'],
                                                expansions=['author_id'])
    """
    """    query_results = client.search_recent_tweets(query="#knorzen -is:retweet",
                                                tweet_fields=['author_id'])
    print(query_results.data[0].author_id)


    liking_users = client.get_liking_users(id=1516831003897217025)
    print(liking_users)
    user = client.get_user(id=1260876463345188864)
    print(user)

    liked_tweets = client.get_liked_tweets(id=1260876463345188864)
    print(liked_tweets)"""

    tweets = client.get_users_tweets(id=1260876463345188864, max_results=5)
    print(tweets)


if __name__ == "__main__":
    main()
