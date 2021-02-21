import os
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        create_users_table(connection)
    except Error:
        print(Error)

    return connection

def create_users_table(connection):
    connection.execute('''CREATE TABLE users (
        timerLength Int,
        autoStart Bool
    )''')

def add_user(connection, user):
    sql = ''' INSERT INTO users(timerLength, autoStart) VALUES (?, ?)'''
    cursor = connection.cursor()
    cursor.execute(sql, user)

if __name__ == '__main__':
    connection = create_connection('data.db')
    connection.close()