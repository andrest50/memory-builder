"""Managing the sqlite3 database"""
import sqlite3


def create_connection(db_file):
    """Create a connection and create necessary tables if nonexistent"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        create_users_table(conn)
        create_sentence_lists_table(conn)
    except sqlite3.Error as err:
        print(err)

    return conn


def create_sentence_lists_table(conn):
    """Create table for sentence lists"""
    try:
        sql = """CREATE TABLE sentenceLists (
            sentences String,
            title String,
            numCompleted Int,
            numCorrect Int
        )"""
        conn.execute(sql)
    except sqlite3.Error as err:
        print(err)


def drop_sentence_lists_table(conn):
    """Delete table for sentence lists"""
    sql = """DROP TABLE sentenceLists"""
    conn.execute(sql)
    conn.commit()


def get_all_sentence_lists(conn):
    """Get all sentence lists from table"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sentenceLists")
    data = cursor.fetchall()
    return data


def add_sentence_list(conn, sentences, title, num_completed, num_correct):
    """Add new sentence list row to table"""
    conn.execute(
        "INSERT INTO sentenceLists(sentences, title, numCompleted, numCorrect) VALUES (?, ?, ?, ?)",
        (sentences, title, num_completed, num_correct),
    )
    conn.commit()


def update_sentence_list(conn, sentences, title, num_completed, num_correct):
    """Update sentence list within table"""
    sql = """UPDATE sentenceLists SET sentences = ?, title = ?,
        numCompleted = ?, numCorrect = ? WHERE sentences = ?"""
    conn.execute(sql, (sentences, title, num_completed, num_correct, sentences))
    conn.commit()


def delete_sentence_list(conn, sentences):
    """Delete a sentence list within table"""
    sql = "DELETE FROM sentenceLists WHERE sentences = ?"
    conn.execute(sql, (sentences,))
    conn.commit()


def create_users_table(conn):
    """Create table for users"""
    try:
        sql = """CREATE TABLE users (
            numCorrect Int,
            defaultPath String,
            timerDuration Int,
            charTimerValue Int,
            charBasedTimer Bool,
            noTyping Bool,
            autoStart Bool,
            showCorrectAnswer Bool,
            darkMode Bool
        )"""
        conn.execute(sql)
    except sqlite3.Error as err:
        print(err)


def drop_users_table(conn):
    """Delete all users in table"""
    sql = """DROP TABLE users"""
    conn.execute(sql)
    conn.commit()


def get_all_users(conn):
    """Get all users from table"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    return data


def add_user(conn, user):
    """Add a new user row in table"""
    sql = """INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    conn.execute(sql, user)
    conn.commit()


def update_user(conn, user):
    """Update a user within table"""
    sql = """UPDATE users SET numCorrect = ?, defaultPath = ?, timerDuration = ?,
        charTimerValue = ?, charBasedTimer = ?, noTyping = ?, autoStart = ?,
        showCorrectAnswer = ?, darkMode = ?"""
    conn.execute(sql, user)
    conn.commit()


def test_user(user_num):
    """Pre-defined user variables for testing purposes"""
    users = {
        "1": (5, "", 3, True, True, True, True, True),
        "2": (0, "", 3, False, False, False, False, False),
        "3": (2, "", 4, True, True, False, False, True),
        "4": (1, "", 5, False, False, True, True, False),
    }
    return users[str(user_num)]


if __name__ == "__main__":
    connection = create_connection("data.db")
    # drop_sentences_list_table(connection)
    # drop_users_table(connection)
    # create_users_table(connection)
    # add_user(connection, test_user(3))
    # get_all_users(connection)
    connection.close()
