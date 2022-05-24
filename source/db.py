#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions for handling with database.
"""
import os
from dataclasses import dataclass
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    sessionmaker,
    relationship
)
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


class TwitterUser(Base):  # pylint: disable=too-few-public-methods
    """Table structure for twitter user with needed information to analyze with NLP"""
    __tablename__ = 'twitterUser'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    twitter_user_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    twitter_user_name = sqlalchemy.Column(sqlalchemy.String(500))
    comment = sqlalchemy.Column(sqlalchemy.String(500))
    tweets = relationship("Tweet", backref="twitterUser")

    def __repr__(self):
        return f"<User-ID {self.twitter_user_id}"


class Tweet(Base):  # pylint: disable=too-few-public-methods
    """Table structure for tweet with needed information to analyze with NLP"""
    __tablename__ = 'tweets'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("twitterUser.id"))
    tweet_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    tweet_url = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    tweet_text = sqlalchemy.Column(sqlalchemy.String(281), nullable=False)
    tweet_create_date = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    comments = relationship("Comment",
                            secondary=tweets_link_comments,
                            back_populates="tweets")

    def __repr__(self):
        return f"<Tweet-ID {self.tweet_id}"


class Comment(Base):  # pylint: disable=too-few-public-methods
    """Table structure for comments of tweets"""
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.String(500))
    tweets = relationship("Tweet",
                          secondary=tweets_link_comments,
                          back_populates="comments")

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

    def add(self, data: Tweet | TwitterUser):
        """
        Write and commit data to database
        :param data: Tweet or TwitterUser class to save
        :return:
        """
        self.session.add(data)
        self.session.commit()


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
        print(f"ERROR: No connection to the database is possible. Aborted with error: [{err}]. "
              f"Please check DB_CONNECTOR.")
        engine.dispose()

    except sqlalchemy.exc.ProgrammingError as err:
        print(f"ERROR: unexpected error: [{err}].")


def main() -> None:
    """
    Main function to run db for tests
    :return: None
    """
    from datetime import datetime
    """Twitter user hinzufügen"""
    """with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        conn.add(TwitterUser(input_timestamp=datetime.now(),
                             twitter_user_id=1,
                             twitter_user_name="TeTü"))"""

    """Tweet hinzufügen mit Hilfe des TwitterUsers"""
    """with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        tweet1 = Tweet(tweet_id=777,
                       tweet_url="https://test",
                       tweet_text="Hallo",
                       tweet_create_date=datetime.now())
        twitter_user = conn.session.query(TwitterUser).\
            filter(TwitterUser.twitter_user_id == 1234).first()
        print(twitter_user.id)
        twitter_user.tweets.append(
            tweet1
        )
        conn.session.commit()"""

    """Tweet hinzufügen und an TwitterUser knüpfen, Kommentar erzeugen und an Tweet hängen"""
    """with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        tweet1 = Tweet(tweet_id=888,
                       tweet_url="https://test",
                       tweet_text="Hallo",
                       tweet_create_date=datetime.now())
        comment1 = Comment(tweet_id=999,
                           comment="Cool es funzt")
        tweet1.comments.append(
            comment1
        )
        twitter_user = conn.session.query(TwitterUser).\
            filter(TwitterUser.twitter_user_id == 1234).first()
        twitter_user.tweets.append(
            tweet1
        )
        conn.session.commit()"""

    """Kommentare erstellen und an einen Tweet hängen"""
    """with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        comment1 = Comment(tweet_id=66,
                           comment="ein weiteres Kommentar")
        comment2 = Comment(tweet_id=77,
                           comment="und noch ein weiteres Kommentar")
        tweet = conn.session.query(Tweet).filter(Tweet.id == 2).first()
        tweet.comments.append(comment1)
        tweet.comments.append(comment2)
        conn.session.commit()"""

    """Tweet erstellen und an eine Kommentar hängen"""
    """with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        tweet1 = Tweet(tweet_id=222,
                       user_id=1,
                       tweet_url="https://test",
                       tweet_text="Hallo, ist es jetzt many to many?",
                       tweet_create_date=datetime.now())
        comment = conn.session.query(Comment).filter(Comment.id == 1).first()
        comment.tweets.append(tweet1)
        conn.session.commit()"""

    """Suchen aller Kommentaren die an einem Tweet hängen"""
    """with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        tweet = conn.session.query(Tweet).filter(Tweet.id == 2).first()
        print(tweet.tweet_id)
        print(tweet.comments)"""

    """Lösche Verbindung zwischen Tweet und Kommentar"""
    with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        tweet = conn.session.query(Tweet).filter(Tweet.id == 2).first()
        comment = conn.session.query(Comment).filter(Comment.id == 4).first()
        tweet.comments.remove(comment)
        conn.session.commit()


if __name__ == "__main__":
    init()
    main()
