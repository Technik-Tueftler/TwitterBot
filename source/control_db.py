#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from source import db
from rich.console import Console
from rich.table import Table


def close() -> None:
    pass


def count_all_tweets_from_user() -> None:
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
    for key, value in menu.items():
        print(f"{key:2}: {value}")


"""def delete_tweet() -> None:
    option = int(input('Tweet-ID die gelöscht werden soll: '))
    with db.SQLAlchemyConnectionManager(db.CONNECTOR) as conn:
        conn.session.query()"""


def main() -> None:
    menu = {1: "Zähle alle Tweets",
            2: "Beende"}
    commands = {1: count_all_tweets_from_user,
                2: close}
    while True:
        print_menu(menu)
        option = int(input('Option wählen: '))
        command = commands.get(option)
        if command is close:
            break
        command()


if __name__ == "__main__":
    main()
