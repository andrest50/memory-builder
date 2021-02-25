import os
import sqlite3
from sqlite3 import Error

def CreateConnection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        CreateUsersTable(connection)
        CreateSentenceListsTable(connection)
    except Error:
        print(Error)

    return connection

def CreateSentenceListsTable(connection):
    try:
        sql = '''CREATE TABLE sentenceLists (
            sentences String,
            title String,
            num_correct Int
        )'''
        connection.execute(sql)
    except:
        print("Table already exists.")

def DropSentenceListsTable(connection):
    sql = '''DROP TABLE sentenceLists'''
    connection.execute(sql)
    connection.commit()

def GetAllSentenceLists(connection):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM sentenceLists')
    data = cursor.fetchall()
    print(data)
    return data

def AddSentenceList(connection, sentences, title, num_correct):
    #print(sentence_list)
    #sql = '''INSERT INTO sentenceLists VALUES (?)'''
    connection.execute('INSERT INTO sentenceLists(sentences, title, num_correct) VALUES (?, ?, ?)', 
        (sentences, title, num_correct))
    connection.commit()

def UpdateSentenceList(connection, sentences, title, num_correct):
    cursor = connection.cursor()
    #print(cursor.lastrowid)
    sql = '''UPDATE sentenceLists SET sentences = ?, title = ?, num_correct = ? WHERE sentences = ?'''
    connection.execute(sql, (sentences, title, num_correct, sentences))
    connection.commit()

def CreateUsersTable(connection):
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

def DropUsersTable(connection):
    sql = '''DROP TABLE users'''
    connection.execute(sql)
    connection.commit()

def GetAllUsers(connection):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    #print(data)
    return data

def AddUser(connection, user):
    #print(user)
    sql = '''INSERT INTO users VALUES (?, ?, ?, ?)'''
    connection.execute(sql, user)
    connection.commit()

def UpdateUser(connection, user):
    cursor = connection.cursor()
    print(cursor.lastrowid)
    sql = '''UPDATE users SET numCorrect = ?, timerDuration = ?, autoStart = ?, showCorrectAnswer = ?'''
    connection.execute(sql, user)
    connection.commit()

def TestUser(user_num):
    users = {
        "1": (5, 3, True, True),
        "2": (0, 3, False, False),
        "3": (2, 4, True, False),
        "4": (1, 5, False, True)
    }
    return users[str(user_num)]

if __name__ == '__main__':
    connection = CreateConnection('data.db')
    #DropSentenceListsTable(connection)
    #DropUsersTable(connection)
    #CreateUsersTable(connection)
    #AddUser(connection, TestUser(3))
    #GetAllUsers(connection)
    connection.close()