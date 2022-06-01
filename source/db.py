#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions for handling with database.
"""
import os
from datetime import datetime
from dataclasses import dataclass
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
CONNECTOR = os.getenv("DB_CONNECTOR")
DB_CONNECTION_VALID = False


tweets_link_comments = sqlalchemy.Table(
    "tweets_link_comments",
    Base.metadata,
    sqlalchemy.Column("tweet_id", sqlalchemy.ForeignKey("tweets.id")),
    sqlalchemy.Column("comment_id", sqlalchemy.ForeignKey("comments.id")),
)


class UserNameAtTime(Base):  # pylint: disable=too-few-public-methods
    """Table structure for Twitter username combined with timestamp for history"""

    __tablename__ = "userNameAtTime"
    __table_args__ = {"mariadb_charset": "utf8mb4"}
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("twitterUser.id")
    )
    input_timestamp = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )
    twitter_user_name = sqlalchemy.Column(sqlalchemy.String(500))

    def __repr__(self):
        return f"<Objekt> UserNameAtTime mit Name: {self.twitter_user_name}"


class UserScreenNameAtTime(Base):  # pylint: disable=too-few-public-methods
    """Table structure for Twitter user screen name combined with timestamp for history"""

    __tablename__ = "userScreenNameAtTime"
    __table_args__ = {"mariadb_charset": "utf8mb4"}
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("twitterUser.id")
    )
    input_timestamp = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )
    twitter_user_screen_name = sqlalchemy.Column(sqlalchemy.String(500))

    def __repr__(self):
        return (
            f"<Objekt> UserScreenNameAtTime mit Name: {self.twitter_user_screen_name}"
        )


class TwitterUser(Base):  # pylint: disable=too-few-public-methods
    """Table structure for twitter user with needed information to analyze with NLP"""

    __tablename__ = "twitterUser"
    __table_args__ = {"mariadb_charset": "utf8mb4"}
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    twitter_user_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.String(500))
    tweets = relationship("Tweet", backref="twitterUser")
    user_names = relationship("UserNameAtTime", backref="twitterUser")
    user_screen_names = relationship("UserScreenNameAtTime", backref="twitterUser")

    def __repr__(self):
        return f"<Objekt> TwitterUser mit User-ID {self.twitter_user_id}"


class Tweet(Base):  # pylint: disable=too-few-public-methods
    """Table structure for tweet with needed information to analyze with NLP"""

    __tablename__ = "tweets"
    __table_args__ = {
        "comment": "Table of all recorded tweets to analyze.",
        "mariadb_charset": "utf8mb4",
    }
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("twitterUser.id")
    )
    tweet_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    input_timestamp = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )
    tweet_url = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    tweet_text = sqlalchemy.Column(sqlalchemy.String(281), nullable=False)
    tweet_create_date = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False),
        nullable=False,
        default=datetime.utcnow,
        comment="UTC time when this Tweet was created.",
    )
    comments = relationship(
        "Comment", secondary=tweets_link_comments, back_populates="tweets"
    )

    def __repr__(self):
        return f"<Tweet-ID {self.tweet_id}"


class DeletedTweet(Base):  # pylint: disable=too-few-public-methods
    """Table structure for tweets which were deleted before recording"""

    __tablename__ = "deleted_tweets"
    __table_args__ = {
        "comment": "Table of all tweets which were deleted before recording.",
        "mariadb_charset": "utf8mb4",
    }
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    tweet_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    input_timestamp = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )
    tweet_url = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    twitter_user_screen_name = sqlalchemy.Column(sqlalchemy.String(500))
    comment = sqlalchemy.Column(sqlalchemy.String(500))


class Comment(Base):  # pylint: disable=too-few-public-methods
    """Table structure for comments of tweets"""

    __tablename__ = "comments"
    __table_args__ = {"mariadb_charset": "utf8mb4"}
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    input_timestamp = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )
    comment = sqlalchemy.Column(sqlalchemy.String(500))
    tweets = relationship(
        "Tweet", secondary=tweets_link_comments, back_populates="comments"
    )

    def __repr__(self):
        return f"<Comment-ID {self.id}"


@dataclass
class SQLAlchemyConnectionManager:
    """
    Class to handle data writes with context manager for SQLAlchemy
    """

    connector: str
    engine: sqlalchemy.engine.Engine = None
    session_make: sqlalchemy.orm.session.sessionmaker = None
    session: sqlalchemy.orm.session.Session = None

    def __enter__(self):
        self.engine = create_engine(self.connector)
        Base.metadata.bind = self.engine
        self.session_make = sessionmaker(bind=self.engine)
        self.session = self.session_make()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.session.close()
        self.engine.dispose()

    def add(
        self,
        data: Tweet
        | TwitterUser
        | UserScreenNameAtTime
        | UserNameAtTime
        | DeletedTweet,
    ):
        """
        Write and commit data to database
        :param data: Table class to save
        :return:
        """
        try:
            self.session.add(data)
            self.session.commit()
        except sqlalchemy.exc.OperationalError as err:
            print(f"Fehler beim speichern {data} mit dem Fehler: {err}")


def check_and_update_user_names(data: dict) -> None:
    """

    :param data:
    :return:
    """
    with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        twitter_user = (
            conn.session.query(TwitterUser)
            .filter(TwitterUser.twitter_user_id == data["author_user_id"])
            .first()
        )
        if (
            not twitter_user.user_names
            or twitter_user.user_names[-1].twitter_user_name != data["author_user_name"]
        ):
            twitter_user.user_names.append(
                UserNameAtTime(
                    user_id=data["author_user_id"],
                    twitter_user_name=data["author_user_name"],
                )
            )

        if (
            not twitter_user.user_screen_names
            or twitter_user.user_screen_names[-1].twitter_user_screen_name
            != data["author_user_screen_name"]
        ):
            twitter_user.user_screen_names.append(
                UserScreenNameAtTime(
                    user_id=data["author_user_id"],
                    twitter_user_screen_name=data["author_user_screen_name"],
                )
            )
            conn.session.commit()


def add_deleted_tweet(data: dict, url: str, comment: str) -> None:
    """
    Function to add information of a deleted tweet before recording to database
    :param comment: Comment or reason why this tweet was tagged
    :param url: Complete URL of the deleted tweet
    :param data: Dictionary with information from a tweet-url with user screen name and tweet id
    :return:
    """
    with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        check_tweet = (
            conn.session.query(DeletedTweet)
            .filter(DeletedTweet.tweet_id == data["tweet_id"])
            .first()
        )
        if check_tweet is not None:
            return
        deleted_tweet = DeletedTweet(
            tweet_id=data["tweet_id"],
            tweet_url=url,
            twitter_user_screen_name=data["twitter_user_name"],
            comment=comment,
        )
        conn.add(deleted_tweet)


def add_tweet(data: dict) -> None:
    """
    Function to add tweet and user data to database.
    :param data: information as a dictionary, which must be stored in the database.
    :return: None
    """
    with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        check_tweet = (
            conn.session.query(Tweet).filter(Tweet.tweet_id == data["tweet_id"]).first()
        )
        if check_tweet is not None:
            return
        twitter_user = (
            conn.session.query(TwitterUser)
            .filter(TwitterUser.twitter_user_id == data["author_user_id"])
            .first()
        )
        if twitter_user is None:
            twitter_user = TwitterUser(twitter_user_id=data["author_user_id"])
            conn.add(twitter_user)

        tweet = Tweet(
            tweet_id=data["tweet_id"],
            tweet_url=data["expand_url"],
            tweet_text=data["text"],
            tweet_create_date=data["created_at"],
        )
        lower_case_comment = data["comment"].lower()
        tweet_comment = (
            conn.session.query(Comment)
            .filter(Comment.comment == lower_case_comment)
            .first()
        )
        if tweet_comment is None:
            tweet_comment = Comment(comment=lower_case_comment)
            conn.session.commit()
        tweet.comments.append(tweet_comment)
        twitter_user.tweets.append(tweet)
        conn.session.commit()


def init() -> None:
    """
    Initialization function to create the database if not exists
    :return: None
    """
    global DB_CONNECTION_VALID  # pylint: disable=global-statement
    try:
        engine = create_engine(CONNECTOR)
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)
        engine.dispose()
        DB_CONNECTION_VALID = True

    except sqlalchemy.exc.OperationalError as err:
        print(
            f"ERROR: No connection to the database is possible. Aborted with error: [{err}]. "
            f"Please check DB_CONNECTOR."
        )
        engine.dispose()

    except sqlalchemy.exc.ProgrammingError as err:
        print(f"ERROR: unexpected error: [{err}].")


def main() -> None:
    """
    Main function to run db for tests
    :return: None
    """


if __name__ == "__main__":
    init()
    main()
