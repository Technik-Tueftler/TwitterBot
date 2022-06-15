#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console application to run database query's depends on user input
"""

from rich.console import Console
from rich.table import Table
from source import db


def close() -> None:
    """
    Dummy function to close the console app
    :return: None
    """


def count_all_tweets_from_user() -> None:
    """
    Print numbers of tweets for each registered Twitter user and number of renaming.
    :return: None
    """
    with db.SQLAlchemyConnectionManager(db.CONNECTOR) as conn:
        users = conn.session.query(db.TwitterUser).all()
        table = Table(title="Übersicht Anzahl von Tweets")

        table.add_column("Name", style="magenta")
        table.add_column("Tweets", justify="right", style="green")
        table.add_column("Namensänderung", justify="right", style="green")
        table.add_column("Anzeigenamensänderung", justify="right", style="green")
        for user in users:
            name = str(user.user_screen_names[-1].twitter_user_screen_name)
            count_tweets = str(len(user.tweets))
            count_name = str(len(user.user_names))
            count_screen_name = str(len(user.user_screen_names))
            table.add_row(name, count_tweets, count_name, count_screen_name)

        console = Console()
        console.print(table, justify="center")


def print_menu(menu: dict) -> None:
    """
    Print app menu
    :param menu: dictionary of registered menu
    :return: None
    """
    for key, value in menu.items():
        print(f"{key:>2}: {value}")


def delete_tweet() -> None:
    """
    Start new user context and delete Tweet based on ID and comment if this is requested.
    :return: None
    """
    input_tweet_id = int(input("Tweet-ID die gelöscht werden soll: "))
    with db.SQLAlchemyConnectionManager(db.CONNECTOR) as conn:
        input_delete_comments = input("Kommentar auch löschen? (j,n): ")
        tweet = (
            conn.session.query(db.Tweet).filter(db.Tweet.id == input_tweet_id).first()
        )
        if input_delete_comments == "j":
            comment_ids_from_tweet = [
                comment.id for comment in tweet.comments if len(comment.tweets) == 1
            ]
        tweet.comments = []
        conn.session.query(db.Tweet).filter(db.Tweet.id == input_tweet_id).delete(
            synchronize_session=False
        )
        if input_delete_comments == "j":
            for comment_id in comment_ids_from_tweet:
                conn.session.query(db.Comment).filter(
                    db.Comment.id == comment_id
                ).delete(synchronize_session=False)
        conn.session.commit()


def main() -> None:
    """
    Main function to run the console app
    :return:
    """
    menu = {1: "Zähle alle Tweets", 2: "Tweet löschen", 10: "Beende"}
    commands = {1: count_all_tweets_from_user, 2: delete_tweet, 10: close}
    while True:
        print_menu(menu)
        option = int(input("Option wählen: "))
        command = commands.get(option)
        if command is close:
            break
        command()


if __name__ == "__main__":
    main()
