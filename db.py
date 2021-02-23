import os
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        create_users_table(connection)
        create_sentence_lists_table(connection)
    except Error:
        print(Error)

    return connection

def create_sentence_lists_table(connection):
    try:
        sql = '''CREATE TABLE sentenceLists (
            sentences String
        )'''
        connection.execute(sql)
    except:
        print("Table already exists.")

def drop_sentence_lists_table(connection):
    sql = '''DROP TABLE sentenceLists'''
    connection.execute(sql)
    connection.commit()

def get_all_sentence_lists(connection):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM sentenceLists')
    data = cursor.fetchall()
    print(data)
    return data

def add_sentence_list(connection, sentenceList):
    #print(sentenceList)
    #sql = '''INSERT INTO sentenceLists VALUES (?)'''
    connection.execute('INSERT INTO sentenceLists VALUES (?)', (sentenceList,))
    connection.commit()

def create_users_table(connection):
    try:
        sql = '''CREATE TABLE users (
            numCorrect Int,
            timerDuration Int,
            autoStart Bool,
            showCorrectAnswer Bool
        )'''
        connection.execute(sql)
    except:
        print("Table already exists.")

def drop_users_table(connection):
    sql = '''DROP TABLE users'''
    connection.execute(sql)
    connection.commit()

def get_all_users(connection):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    #print(data)
    return data

def add_user(connection, user):
    #print(user)
    sql = '''INSERT INTO users VALUES (?, ?, ?, ?)'''
    connection.execute(sql, user)
    connection.commit()

def update_user(connection, user):
    cursor = connection.cursor()
    print(cursor.lastrowid)
    sql = '''UPDATE users SET numCorrect = ?, timerDuration = ?, autoStart = ?, showCorrectAnswer = ?'''
    connection.execute(sql, user)
    connection.commit()

def test_user(user_num):
    users = {
        "1": (5, 3, True, True),
        "2": (0, 3, False, False),
        "3": (2, 4, True, False),
        "4": (1, 5, False, True)
    }
    return users[str(user_num)]

if __name__ == '__main__':
    connection = create_connection('data.db')
    #drop_sentence_lists_table(connection)
    #drop_users_table(connection)
    #create_users_table(connection)
    #add_user(connection, test_user(3))
    #get_all_users(connection)
    connection.close()