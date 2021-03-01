"""Application starting point with main window and fetching data from database"""
import sys
import os
import json
import random
from functools import partial
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import db
from settings import SettingsWindow
from sentence_list import SentenceListWindow, SentenceListStackItem, SentenceList
from controller import Controller

"""
To Do:
- Refactor code + organize
"""

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self, user=None, controller=None):
        super().__init__()

        self.user = user
        self.controller = controller

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.menu_actions = []

        self.create_menu_bar() # Set up menu bar
        self.create_info_line() # Set up info line
        self.init_shortcuts()

        self.sentence_label = QLabel("Open a text file to get started or use the default sentences.")
        self.sentence_label.setAlignment(Qt.AlignCenter)
        self.sentence_label.setStyleSheet("font: 15px;")

        self.input_box = QLineEdit("", self)
        self.input_box.returnPressed.connect(self.check_answer)

        self.generate_sentence_btn = QPushButton("Generate Sentence", self)
        self.generate_sentence_btn.clicked.connect(self.get_random_sentence)

        self.correct_answer_label = QLabel("")
        self.correct_answer_label.setAlignment(Qt.AlignCenter)

        self.correct_or_not_label = QLabel("")
        self.correct_or_not_label.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.info_layout)
        self.layout.addWidget(self.sentence_label)
        self.layout.addWidget(self.correct_answer_label)
        self.layout.addWidget(self.correct_or_not_label)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.generate_sentence_btn)
        self.window.setLayout(self.layout)

        self.resp_timer = QTimer()
        self.resp_timer.timeout.connect(self.clear_sentence)

        self.answer_timer = QTimer()
        self.answer_timer.timeout.connect(self.clear_answer)

    def create_menu_bar(self):
        """
        Create the MainWindow menu bar with all associated submenus and actions.
        """
        self.menubar = self.menuBar()

        # File Menu
        self.file_menu = self.menubar.addMenu("File")
        self.open_file_act = QAction("Open", self)
        self.open_file_act.setStatusTip("Open a file")
        self.open_file_act.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_file_act)

        # Sentence List Menu
        self.sentence_menu = self.menubar.addMenu("List")
        self.sentence_settings_act = QAction("Settings", self)
        self.sentence_settings_act.triggered.connect(self.open_list_settings)
        self.sentence_menu.addAction(self.sentence_settings_act)
        for sentence_list in self.controller.sentence_lists:
            self.sentence_act = QAction(f"{sentence_list.title}")
            self.sentence_act.triggered.connect(partial(self.use_sentence_list, sentence_list))
            self.menu_actions.append(self.sentence_act)
            self.sentence_menu.addAction(self.sentence_act)

        # Settings Menu
        self.settings_act = QAction("Settings", self)
        self.settings_act.triggered.connect(self.open_settings)
        self.menubar.addAction(self.settings_act)

    def create_info_line(self):
        """
        Create layout for information about current list and number of correct answers.
        """
        # Single label for current list
        self.current_list_label = QLabel(f"Current List: {self.controller.current_list.title}")
        self.current_list_label.setAlignment(Qt.AlignLeft)

        # Two labels in a vertical box layout for number of correct answers
        self.num_correct_label = QLabel(f"Total Correct: {str(self.user.num_correct)}")
        self.num_correct_label.setAlignment(Qt.AlignRight)

        self.num_list_correct_label = QLabel(f"List Correct: {str(self.controller.current_list.num_correct)}")
        self.num_list_correct_label.setAlignment(Qt.AlignRight)

        self.num_correct_layout = QVBoxLayout()
        self.num_correct_layout.addWidget(self.num_correct_label)
        self.num_correct_layout.addWidget(self.num_list_correct_label)

        # Main info layout that contains the single label and inner layout
        self.info_layout = QHBoxLayout()
        self.info_layout.addWidget(self.current_list_label)
        self.info_layout.addLayout(self.num_correct_layout)

    def init_shortcuts(self):
        action_shortcuts = [
            ("Ctrl+O", self.open_file_act),
            ("Ctrl+L", self.sentence_settings_act),
            ("Ctrl+S", self.settings_act)
        ]
        for shortcut in action_shortcuts:
            if len(shortcut) == 2:
                key, widget = shortcut
            widget.setShortcut(key)

    def closeEvent(self, event):
        """
        Override the closeEvent PyQt function to update the database before closing application.
        """
        db.update_user(connection, [
                self.user.num_correct,
                self.user.default_path,
                self.user.timer_duration,
                self.user.char_based_timer,
                self.user.auto_start,
                self.user.show_correct_sentence])

        # Add sentence list to database if it's not a duplicate and isn't empty
        all_sentence_lists = db.get_all_sentence_lists(connection)
        duplicates = [self.controller.current_list.sentences == json.loads(''.join(sentence_list[0])) 
            for sentence_list in all_sentence_lists]
        if not True in duplicates and self.controller.current_list.sentences and \
                self.controller.current_list not in self.controller.deleted_lists:
            db.add_sentence_list(
                connection,
                json.dumps(self.controller.current_list.sentences),
                self.controller.current_list.title,
                self.controller.current_list.num_correct)
        else:
            db.update_sentence_list(
                connection,
                json.dumps(self.controller.current_list.sentences),
                self.controller.current_list.title,
                self.controller.current_list.num_correct)

        connection.close() # Close database connection
        self.close() # Close application

    def use_sentence_list(self, sentence_list):
        """Update the current sentence list and related labels"""
        self.controller.print_all_lists()
        db.update_sentence_list(
                connection,
                json.dumps(self.controller.current_list.sentences),
                self.controller.current_list.title,
                self.controller.current_list.num_correct)
        self.controller.current_list = sentence_list
        self.current_list_label.setText(f"Current List: {self.controller.current_list.title}")
        self.num_list_correct_label.setText(f"List Correct: {self.controller.current_list.num_correct}")
        self.clear_sentence()
        self.clear_answer(False)

    def open_settings(self):
        """Open settings window"""
        self.settings_window = SettingsWindow(self.user)
        self.settings_window.show()

    def open_list_settings(self):
        """Open sentence list window"""
        self.sentence_list_window = SentenceListWindow(self)
        self.sentence_list_window.show()

    def open_file(self):
        """Open a text file and extract the lines as sentences"""
        fname = QFileDialog().getOpenFileName(self, 'Open file', self.user.default_path,
            'Text Files (*.txt)')

        if fname[0]:
            # Add sentence list to database if it's not a duplicate and isn't empty
            all_sentence_lists = db.get_all_sentence_lists(connection)
            duplicates = [self.controller.current_list.sentences == json.loads(''.join(sentence_list[0])) for sentence_list in all_sentence_lists]
            if not True in duplicates and self.controller.current_list:
                db.add_sentence_list(
                    connection,
                    json.dumps(self.controller.current_list.sentences),
                    self.controller.current_list.title,
                    self.controller.current_list.num_correct)

            with open(fname[0], 'r') as file:
                duplicates = [fname[0] == sentence_list.title for sentence_list in self.controller.sentence_lists]
                if sum(duplicates) <= 1 in duplicates:
                    self.controller.current_list.sentences = file.readlines()
                    self.controller.current_list.title = fname[0]
                else:
                    self.controller.current_list = SentenceList(file.readlines(), fname[0])
                    self.sentence_act = QAction(f"{self.controller.current_list.title}")
                    self.sentence_act.triggered.connect(
                        partial(self.use_sentence_list, self.controller.current_list))
                    self.menu_actions.append(self.sentence_act)
                    self.sentence_menu.addAction(self.sentence_act)
                    self.controller.sentence_lists.append(self.controller.current_list)

                self.current_list_label.setText(f"Current List: {self.controller.current_list.title}")
                self.num_list_correct_label.setText(f"List Correct: {self.controller.current_list.num_correct}")

    def get_random_sentence(self):
        """Generate a random sentence from the current sentence list."""
        self.correct_answer_label.setText("")
        if self.controller.current_list:
            self.new_sentence = random.choice(self.controller.current_list.sentences).rstrip()

            # Generate a new sentence until it is different than the previous (unless size is 1)
            while(self.new_sentence == self.controller.current_sentence
                    and len(self.controller.current_list.sentences) != 1):
                self.new_sentence = random.choice(self.controller.current_list.sentences).rstrip()

            self.sentence_label.setText(self.new_sentence)
            self.controller.current_sentence = self.new_sentence
            self.controller.sentence_active = True
            self.input_box.setFocus()
            if self.user.char_based_timer:
                print(len(self.new_sentence) * 100)
                self.resp_timer.start(len(self.new_sentence) * 100)
            else:
                self.resp_timer.start(self.user.timer_duration * 1000)

    def clear_sentence(self):
        """Hide the current sentence"""
        self.sentence_label.setText("Type the sentence and hit Enter.")
        self.resp_timer.stop()

    def no_lists_available(self):
        """For when there are no sentence lists to use"""
        self.clear_current_list_label()
        self.sentence_label.setText("Type the sentence and hit Enter.")
        self.correct_or_not_label.setText("")
        self.sentence_label.setText("Generate a new sentence.")
        self.num_list_correct_label.setText("List Correct: 0")
        self.controller.current_list = None

    def clear_current_list_label(self):
        """Clear the text for the current list label"""
        self.current_list_label.setText("Current List: ")

    def clear_answer(self, auto_start=None):
        """Hide the answer label (correct or incorrect)"""
        if auto_start is None:
            auto_start = self.user.auto_start
        self.correct_or_not_label.setText("")
        self.sentence_label.setText("Generate a new sentence.")
        self.answer_timer.stop()
        if bool(auto_start) is True:
            self.get_random_sentence()

    def check_answer(self):
        """Check user input against correct answer"""
        if self.controller.sentence_active:

            if self.input_box.text().rstrip() == self.controller.current_sentence.rstrip():
                self.user.num_correct += 1
                self.controller.current_list.num_correct += 1
                self.num_correct_label.setText("Correct: " + str(self.user.num_correct))
                self.num_list_correct_label.setText(f"List Correct: {self.controller.current_list.num_correct}")
                self.correct_or_not_label.setText("Correct!")
            else:
                self.correct_or_not_label.setText("Incorrect!")

            if self.user.show_correct_sentence:
                self.correct_answer_label.setText(self.controller.current_sentence.rstrip())

            if self.sentence_label.text() != "Type the sentence and hit Enter.":
                self.resp_timer.stop()

            self.answer_timer.start(2000)
            self.controller.sentence_active = False
            self.input_box.setText("")

        else:
            self.get_random_sentence()

class User():
    """For user-specific statistics and settings"""
    def __init__(self, num_correct=0, default_path="", timer_duration=1,
                char_based_timer=False, auto_start=False, show_correct_sentence=False):
        self.num_correct = num_correct
        self.default_path = default_path
        self.timer_duration = timer_duration
        self.char_based_timer = char_based_timer
        self.auto_start = auto_start
        self.show_correct_sentence = show_correct_sentence

def get_user_from_db(db):
    """Get main user settings and statistics from database"""
    users = db.get_all_users(connection)
    current_user = None

    if not users:
        current_user = User()
        db.add_user(connection, [
            current_user.num_correct,
            current_user.default_path,
            current_user.timer_duration,
            current_user.char_based_timer,
            current_user.auto_start,
            current_user.show_correct_sentence])
    else:
        # Get the first user (only one user is supported right now)
        current_user = User(users[0][0], users[0][1], users[0][2], users[0][3], users[0][4], bool(users[0][5]))
        print(current_user.show_correct_sentence)

    return current_user

def get_lists_from_db(db):
    """Get sentence lists from database"""
    all_sentence_lists = db.get_all_sentence_lists(connection)

    deserialized_lists = []
    if not all_sentence_lists:
        if os.path.exists('default_sentences.txt'):
            with open('default_sentences.txt', 'r') as file:
                new_list = SentenceList(file.readlines())
                deserialized_lists.append(new_list)
                db.add_sentence_list(
                    connection,
                    json.dumps(new_list.sentences),
                    new_list.title,
                    new_list.num_correct)
    else:
        for sentence_list in all_sentence_lists:
            new_list = SentenceList(json.loads(''.join(sentence_list[0])),
                sentence_list[1], sentence_list[2])
            deserialized_lists.append(new_list)

    return deserialized_lists

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet("QLabel{font-size: 8pt;}")

    connection = db.create_connection('data.db')
    user = get_user_from_db(db)
    sentence_lists = get_lists_from_db(db)

    controller = Controller(sentence_lists)

    main = MainWindow(user, controller)
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.show()
    sys.exit(app.exec_())
