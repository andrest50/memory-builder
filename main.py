"""Application starting point with main window and fetching data from database"""
import sys
import os
import json
import copy
import random
from functools import partial
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import db

class User():
    """Class for users"""
    def __init__(self, num_correct = 0, timer_duration = 3,
                auto_start = False, show_correct_sentence = False):
        self.num_correct = num_correct
        self.timer_duration = timer_duration
        self.auto_start = auto_start
        self.show_correct_sentence = show_correct_sentence

class SentenceList():
    """Class for lists of sentences imported from a text file"""
    def __init__(self, sentences = None, title = "Default", num_correct = 0):
        self.sentences = sentences
        self.title = title
        self.num_correct = num_correct

    def __eq__(self, other):
        return self.sentences == other.sentences

    def SentenceAction(self):
        self.sentence_act = QAction(f"{self.title}")
        return self.sentence_act

class SentenceListStackItem(QWidget):
    def __init__(self, sentence_list):
        super().__init__()

        self.info_layout = QFormLayout()

        self.list_name_label = QLabel(f"{sentence_list.title}")
        self.info_layout.addRow(self.list_name_label)

        self.info_layout.addRow("Rename: ", QLineEdit())

        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Delete")
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.delete_btn)
        self.button_layout.setContentsMargins(0, 50, 0, 0)
        self.info_layout.addRow(self.button_layout)

class SentenceListWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(400, 240)

        self.layout = QHBoxLayout()

        self.select_layout = QHBoxLayout()

        self.list_stack_info = QListWidget()
        self.list_stack = QStackedWidget(self)

        self.stack_sentence_lists()

        self.select_layout.addWidget(self.list_stack_info)
        self.select_layout.addWidget(self.list_stack)

        self.layout.addLayout(self.select_layout)

        self.list_stack_info.currentRowChanged.connect(self.display_list_settings)

        #self.settings_label = QLabel("Sentence Lists")
        #self.settings_label.setStyleSheet("font: 12px")
        #self.layout.addWidget(self.settings_label)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)

    def stack_sentence_lists(self):
        self.stack = []

        for index, sentence_list in enumerate(sentence_lists):
            self.stack_item = SentenceListStackItem(sentence_list)
            print(self.stack_item.list_name_label.text())
            self.list_stack_info.insertItem(index, f"{sentence_list.title}")
            self.stack.append(self.stack_item)
            self.stack[index].setLayout(self.stack_item.info_layout)
            self.list_stack.addWidget(self.stack[index])

    def display_list_settings(self, index):
        self.list_stack.setCurrentIndex(index)

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(200, 150)

        self.layout = QVBoxLayout()

        self.settings_box = QFormLayout()
        self.settings_box.setAlignment(Qt.AlignHCenter)

        self.settings_label = QLabel("Settings")
        self.settings_label.setAlignment(Qt.AlignCenter)
        self.settings_label.setStyleSheet("font: 12px")
        self.settings_box.addRow(self.settings_label)

        self.timer_label = QLabel("Timer")
        self.timer_input = QLineEdit()
        self.timer_input.setText(str(user.timer_duration))
        self.timer_input.setMaximumWidth(100)
        self.settings_box.addRow(self.timer_label, self.timer_input)

        self.auto_start_CB = QCheckBox("Auto Start")
        if user.auto_start == True:
            self.auto_start_CB.setChecked(True)
        self.settings_box.addWidget(self.auto_start_CB)

        self.show_correct_CB = QCheckBox("Show Correct Answer")
        if user.show_correct_sentence == True:
            self.show_correct_CB.setChecked(True)
        self.settings_box.addWidget(self.show_correct_CB)

        self.save_btn = QPushButton("Save")
        self.save_btn.setMaximumWidth(100)
        self.save_btn.clicked.connect(self.save_settings)
        self.settings_box.addWidget(self.save_btn)

        self.layout.addLayout(self.settings_box)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)

    def save_settings(self):
        """Set user settings into user object."""
        if self.timer_input.text():
            user.timer_duration = int(self.timer_input.text())

        if self.auto_start_CB.isChecked():
            user.auto_start = True
        else:
            user.auto_start = False

        if self.show_correct_CB.isChecked():
            user.show_correct_sentence = True
        else:
            user.show_correct_sentence = False

        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.settings_window = SettingsWindow()
        self.sentence_list_window = SentenceListWindow()

        self.get_start_list() # Get initial sentence list
        self.create_menu_bar() # Set up menu bar

        self.current_sentence = ""
        self.sentence_active = False

        self.create_info_line()

        self.sentence = QLabel("Open a text file to get started or use the default sentences.")
        self.sentence.setAlignment(Qt.AlignCenter)
        self.sentence.setStyleSheet("font: 15px;")

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
        self.layout.addWidget(self.sentence)
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
        self.open_file_act.setShortcut("Ctrl+O")
        self.open_file_act.setStatusTip("Open a file")
        self.open_file_act.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_file_act)

        # Sentence List Menu
        self.sentence_menu = self.menubar.addMenu("List")
        self.sentence_settings_act = QAction("Settings", self)
        self.sentence_settings_act.triggered.connect(self.open_list_settings)
        self.sentence_menu.addAction(self.sentence_settings_act)
        for sentence_list in sentence_lists:
            print(sentence_list)
            self.sentence_act = sentence_list.SentenceAction()
            self.sentence_act.triggered.connect(partial(self.use_sentence_list, sentence_list))
            self.sentence_menu.addAction(self.sentence_act)

        # Settings Menu
        self.settings_act = QAction("Settings", self)
        self.settings_act.setShortcut("Ctrl+S")
        self.settings_act.triggered.connect(self.open_settings)
        self.menubar.addAction(self.settings_act)

    def create_info_line(self):
        """
        Create layout for information about current list and number of correct answers.
        """
        # Single label for current list
        self.current_list_label = QLabel(f"Current List: {self.current_list.title}")
        self.current_list_label.setAlignment(Qt.AlignLeft)

        # Two labels in a vertical box layout for number of correct answers
        self.num_correct_label = QLabel(f"Total Correct: {str(user.num_correct)}")
        self.num_correct_label.setAlignment(Qt.AlignRight)

        self.num_list_correct_label = QLabel(f"List Correct: {str(self.current_list.num_correct)}")
        self.num_list_correct_label.setAlignment(Qt.AlignRight)

        self.num_correct_layout = QVBoxLayout()
        #self.num_correct_layout.setContentsMargins(0, 0, 0, 0)
        #self.num_correct_layout.setSpacing(0)
        self.num_correct_layout.addWidget(self.num_correct_label)
        self.num_correct_layout.addWidget(self.num_list_correct_label)

        # Main info layout that contains the single label and inner layout
        self.info_layout = QHBoxLayout()
        self.info_layout.addWidget(self.current_list_label)
        self.info_layout.addLayout(self.num_correct_layout)

    def closeEvent(self, event):
        """
        Override the closeEvent PyQt function to update the database before closing application.
        """
        db.update_user(connection, [
                user.num_correct,
                user.timer_duration,
                user.auto_start,
                user.show_correct_sentence])

        # Add sentence list to database if it's not a duplicate and isn't empty
        duplicates = [self.current_list == sentence_list for sentence_list in sentence_lists]
        if not True in duplicates and self.current_list.sentences:
            db.add_sentence_list(
                connection,
                json.dumps(self.current_list.sentences),
                self.current_list.title,
                self.current_list.num_correct)
        else:
            db.update_sentence_list(
                connection,
                json.dumps(self.current_list.sentences),
                self.current_list.title,
                self.current_list.num_correct)

        connection.close() # Close database connection
        self.close() # Close application

    def get_start_list(self):
        """Get first sentence list"""
        if sentence_lists:
            self.current_list = copy.deepcopy(sentence_lists[0])
        else:
            self.current_list = SentenceList()

    def use_sentence_list(self, sentence_list):
        """Update the current sentence list and related labels"""
        self.current_list = sentence_list
        self.current_list_label.setText(f"Current File: {self.current_list.title}")
        self.num_list_correct_label.setText(f"List Correct: {self.current_list.num_correct}")

    def open_settings(self):
        """Open settings window"""
        self.settings_window.show()

    def open_list_settings(self):
        """Open sentence list window"""
        self.sentence_list_window.show()

    def open_file(self):
        """Open a text file and extract the lines as sentences"""
        dialog = QFileDialog()
        fname = QFileDialog().getOpenFileName(self, 'Open file', '/Andres/Text-Files',
            'Text Files (*.txt)')

        if fname[0]:
            # Add sentence list to database if it's not a duplicate and isn't empty
            duplicates = [self.current_list == sentence_list for sentence_list in sentence_lists]
            if not True in duplicates and self.current_list.sentences:
                db.add_sentence_list(
                    connection,
                    json.dumps(self.current_list.sentences),
                    self.current_list.title,
                    self.current_list.num_correct)

            with open(fname[0], 'r') as file:
                duplicates = [fname[0] == sentence_list.title for sentence_list in sentence_lists]
                if True in duplicates:
                    self.current_list.sentences = file.readlines()
                    self.current_list.title = fname[0]
                else:
                    self.current_list = SentenceList(file.readlines(), fname[0])
                    self.sentence_act = self.current_list.sentence_action()
                    self.sentence_act.triggered.connect(
                        partial(self.use_sentence_list, self.current_list))
                    self.sentence_menu.addAction(self.sentence_act)

                self.current_list_label.setText(f"Current File: {self.current_list.title}")
                self.num_list_correct_label.setText(f"List Correct: {self.current_list.num_correct}")

    def get_random_sentence(self):
        """Generate a random sentence from the current sentence list."""
        self.correct_answer_label.setText("")
        if self.current_list.sentences:
            self.new_sentence = random.choice(self.current_list.sentences).rstrip()

            # Generate a new sentence until it is different than the previous (unless size is 1)
            while(self.new_sentence == self.current_sentence
                and len(self.current_list.sentences) != 1):
                self.new_sentence = random.choice(self.current_list.sentences).rstrip()

            self.sentence.setText(self.new_sentence)
            self.current_sentence = self.new_sentence
            self.sentence_active = True
            self.input_box.setFocus()
            self.resp_timer.start(user.timer_duration * 1000)

    def clear_sentence(self):
        """Hide the current sentence"""
        self.sentence.setText("Type the sentence and hit Enter.")
        self.resp_timer.stop()

    def clear_answer(self):
        """Hide the answer label (correct or incorrect)"""
        self.correct_or_not_label.setText("")
        self.sentence.setText("Generate a new sentence.")
        self.answer_timer.stop()
        if user.auto_start == True:
            self.get_random_sentence()

    def check_answer(self):
        """Check user input against correct answer"""
        if self.sentence_active:

            if self.input_box.text().rstrip() == self.current_sentence.rstrip()\
                and self.sentence_active == True:
                user.num_correct += 1
                self.current_list.num_correct += 1
                self.num_correct_label.setText("Correct: " + str(user.num_correct))
                self.num_list_correct_label.setText(f"List Correct: {self.current_list.num_correct}")
                self.correct_or_not_label.setText("Correct!")
            else:
                self.correct_or_not_label.setText("Incorrect!")

            if user.show_correct_sentence:
                self.correct_answer_label.setText(self.current_sentence.rstrip())

            if self.sentence.text() != "Type the sentence and hit Enter.":
                self.resp_timer.stop()

            self.answer_timer.start(2000)
            self.sentence_active = False
            self.input_box.setText("")

def get_user_from_db(db):
    users = db.get_all_users(connection)
    user = None

    if not users:
        user = User()
        db.add_user(connection, [
            user.num_correct,
            user.timer_duration,
            user.auto_start,
            user.show_correct_sentence])
    else:
        # Get the first user (only one user is supported right now)
        user = User(users[0][0], users[0][1], users[0][2], users[0][3])

    return user

def get_lists_from_db(db):
    sentence_lists = db.get_all_sentence_lists(connection)

    deserialized_lists = []
    if not sentence_lists:
        if os.path.exists('default_sentences.txt'):
            with open('default_sentences.txt', 'r') as file:
                sentences = file.readlines()
                new_list = SentenceList(sentences)
                deserialized_lists.append(new_list)
                db.add_sentence_list(
                    connection,
                    json.dumps(new_list.sentences),
                    new_list.title,
                    new_list.num_correct)
    else:
        for sentence_list in sentence_lists:
            sentences = json.loads(''.join(sentence_list[0]))
            new_list = SentenceList(sentences, sentence_list[1], sentence_list[2])
            deserialized_lists.append(new_list)

    return deserialized_lists

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet("QLabel{font-size: 8pt;}")

    connection = db.create_connection('data.db')
    user = get_user_from_db(db)
    sentence_lists = get_lists_from_db(db)
    #print(user)
    #print(len(sentence_lists))

    main = MainWindow()
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.show()
    sys.exit(app.exec_())
