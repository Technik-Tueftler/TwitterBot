import os
from datetime import datetime
from dataclasses import dataclass
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()
CONNECTOR = os.getenv("DB_CONNECTOR")
DB_CONNECTION_VALID = False


class Tweets(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = 'tweets'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    tweet_url = sqlalchemy.Column(sqlalchemy.String(100))
    comment = sqlalchemy.Column(sqlalchemy.String(500))


class TwitterUser(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = 'twitterUser'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    input_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    twitter_user_id = sqlalchemy.Column(sqlalchemy.Integer)
    comment = sqlalchemy.Column(sqlalchemy.String(500))


@dataclass
class SQLAlchemyConnectionManager:
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

    def add(self, data: Tweets | TwitterUser):
        self.session.add(data)
        self.session.commit()


def init() -> None:
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
    with SQLAlchemyConnectionManager(CONNECTOR) as session:
        session.add(Tweets(input_timestamp=datetime.now(),
                           tweet_url="https://blabla",
                           comment="Wir sind geile Hühner"))


if __name__ == "__main__":
    main()
