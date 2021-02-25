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
            sentences String,
            title String,
            num_correct Int
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
    return data

def add_sentence_list(connection, sentences, title, num_correct):
    connection.execute('INSERT INTO sentenceLists(sentences, title, num_correct) VALUES (?, ?, ?)', 
        (sentences, title, num_correct))
    connection.commit()

def update_sentence_list(connection, sentences, title, num_correct):
    cursor = connection.cursor()
    sql = '''UPDATE sentenceLists SET sentences = ?, title = ?, num_correct = ? WHERE sentences = ?'''
    connection.execute(sql, (sentences, title, num_correct, sentences))
    connection.commit()

def delete_sentence_list(connection, sentences):
    cursor = connection.cursor()
    sql = 'DELETE FROM sentenceLists WHERE sentences = ?'
    connection.execute(sql, (sentences,))
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
    return data

def add_user(connection, user):
    sql = '''INSERT INTO users VALUES (?, ?, ?, ?)'''
    connection.execute(sql, user)
    connection.commit()

def update_user(connection, user):
    cursor = connection.cursor()
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
    #drop_sentences_list_table(connection)
    #drop_users_table(connection)
    #create_users_table(connection)
    #add_user(connection, TestUser(3))
    #get_all_users(connection)
    connection.close()