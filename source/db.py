#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of functions for handling with database.
"""
import os
from dataclasses import dataclass
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
CONNECTOR = os.getenv("DB_CONNECTOR")
DB_CONNECTION_VALID = False


"""class LinkComment(Base):
    __tablename__ = 'link_comment'
    twitter_user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('twitterUser.id'), primary_key=True)
    tweet_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('tweet.id'), primary_key=True)"""


class TwitterUser(Base):  # pylint: disable=too-few-public-methods
    """Table structure for twitter user with needed information to analyze with NLP"""
    __tablename__ = 'twitterUser'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    twitter_user_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.String(500))
    # tweet = relationship("Tweet", backref="twitterUser")
    # tweets = relationship("Tweet", secondary="link_comment", backref=)


class Tweet(Base):  # pylint: disable=too-few-public-methods
    """Table structure for tweet with needed information to analyze with NLP"""
    __tablename__ = 'tweet'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    # user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("twitterUser.id"))
    tweet_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    tweet_url = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.String(500))
    tweet_text = sqlalchemy.Column(sqlalchemy.String(281), nullable=False)
    tweet_create_date = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    mention_counter = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)
    # twitter_user = relationship("TwitterUser", secondary="link_comment")


class Comments(Base):  # pylint: disable=too-few-public-methods
    """Table structure for comments of the messages"""
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    tweet_id = sqlalchemy.Column(sqlalchemy.BIGINT, nullable=False)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.String(500))


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
    with SQLAlchemyConnectionManager(CONNECTOR) as session:
        session.add(TwitterUser(input_timestamp=datetime.now(),
                                twitter_user_id=1234))
    with SQLAlchemyConnectionManager(CONNECTOR) as session:
        session.add(Tweet(user_id=1,
                           input_timestamp=datetime.now(),
                           tweet_url="https://",
                           tweet_text="Hallo",
                           tweet_create_date=datetime.now()))


if __name__ == "__main__":
    init()
    main()
