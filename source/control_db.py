#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console application to run database query's depends on user input
"""

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import print as print_rich
from source import db


def close() -> None:
    """
    Dummy function to close the console app
    :return: None
    """


def user_summary() -> None:
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
            count_name = str(len(user.user_names)-1)
            count_screen_name = str(len(user.user_screen_names)-1)
            table.add_row(name, count_tweets, count_name, count_screen_name)

        console = Console()
        console.print(table, justify="center")


def data_summary() -> None:
    """
    Print general information and statistics
    :return: None
    """
    print()
    with db.SQLAlchemyConnectionManager(db.CONNECTOR) as conn:
        project_tree = Tree("Allgemeine Daten")
        count_user = str(conn.session.query(db.TwitterUser).count())
        count_comments = str(conn.session.query(db.Comment).count())
        count_del_tweets = str(conn.session.query(db.DeletedTweet).count())
        count_tweets = str(conn.session.query(db.Tweet).count())
        users = conn.session.query(db.TwitterUser).all()
        sum_all_renames = -(len(users))
        sum_all_screen_renames = -(len(users))
        for user in users:
            sum_all_renames += len(user.user_names)
            sum_all_screen_renames += len(user.user_screen_names)
        project_tree.add(f"User: {count_user}")
        project_tree.add(f"Kommentare: {count_comments}")
        project_tree.add(f"Tweets: {count_tweets}")
        project_tree.add(f"Gelöschte Tweets: {count_del_tweets}")
        project_tree.add(f"Namenswechsel: {sum_all_renames}")
        project_tree.add(f"Anzeigenamenswechsel: {sum_all_screen_renames}")
        print_rich(project_tree)
    print()


def print_menu(menu: dict) -> None:
    """
    Print app menu
    :param menu: dictionary of registered menu
    :return: None
    """
    for key, value in menu.items():
        print(f"{key:>2}: {value[0]}")


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
    menu = {1: ["Datenübersicht", data_summary],
            2: ["Benutzerübersicht", user_summary],
            3: ["Tweet löschen", delete_tweet],
            0: ["Beende", close]}
    while True:
        print_menu(menu)
        option = int(input("Option wählen: "))
        command = menu.get(option)[1]
        if command is close:
            break
        command()


if __name__ == "__main__":
    main()
