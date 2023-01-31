#!/usr/bin/env python3

import sqlite3
import time
import os


def create_database():
    if os.path.exists("messages.db"):
        os.remove("messages.db")
        print("An old database removed.")
    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()
    cursor.execute(""" CREATE TABLE messages_log (
        log text,
        id text
    )""")
    connection.commit()
    connection.close()
    print("The new database created.")


if __name__ == "__main__":
    create_database()
