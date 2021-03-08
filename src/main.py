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
- Customize sentences that are valid when generating a sentence (e.g. <50 characters)
- Fix switching from dark mode to light mode
- Fix switching between lists when in no-typing mode and no answer inputted
"""

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self, user=None, controller=None):
        super().__init__()

        self.user = user
        self.controller = controller

        self.set_dark_mode(self.user.dark_mode)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.menu_actions = []

        self.create_menu_bar() # Set up menu bar
        self.create_info_line() # Set up info line

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

        self.show_answer_layout = QHBoxLayout()
        self.show_answer_layout.setAlignment(Qt.AlignCenter)
        self.show_answer_btn = QPushButton("Show Answer", self)
        self.show_answer_btn.setMaximumWidth(100)
        self.show_answer_btn.clicked.connect(self.show_answer)
        self.show_answer_btn.hide()
        self.show_answer_layout.addWidget(self.show_answer_btn)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.info_layout)
        self.layout.addWidget(self.sentence_label)
        self.layout.addWidget(self.correct_answer_label)
        self.layout.addWidget(self.correct_or_not_label)
        self.layout.addLayout(self.show_answer_layout)
        self.init_button_layout()
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.generate_sentence_btn)
        self.window.setLayout(self.layout)

        self.init_shortcuts()

        self.no_typing_mode()

        self.resp_timer = QTimer()
        self.resp_timer.timeout.connect(self.clear_sentence)

        self.answer_timer = QTimer()
        self.answer_timer.timeout.connect(self.clear_answer)

    def create_menu_bar(self):
        """Create the MainWindow menu bar with all associated submenus and actions."""
        self.menubar = self.menuBar()

        # Sentence List Menu
        self.sentence_menu = self.menubar.addMenu("List")

        self.open_file_act = QAction("Open", self)
        self.open_file_act.setStatusTip("Open a file")
        self.open_file_act.triggered.connect(self.open_file)
        self.sentence_menu.addAction(self.open_file_act)

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
        """Create layout for information about current list and number of correct answers."""

        # Label for current list name
        self.current_list_label = QLabel(f"Current List: {self.controller.current_list.title}")
        self.current_list_label.setAlignment(Qt.AlignLeft)

        # Label for number of correct answers in list
        self.num_list_correct_label = QLabel(f"List Correct: {str(self.controller.current_list.num_correct)}")
        self.num_list_correct_label.setAlignment(Qt.AlignRight)

        # Main info layout that contains the single label and inner layout
        self.info_layout = QHBoxLayout()
        self.info_layout.addWidget(self.current_list_label)
        self.info_layout.addWidget(self.num_list_correct_label)

    def init_shortcuts(self):
        """Set up the application shortcuts"""
        action_shortcuts = [
            ("Ctrl+O", self.open_file_act),
            ("Ctrl+L", self.sentence_settings_act),
            ("Ctrl+S", self.settings_act),
            ("Z", self.correct_btn),
            ("X", self.incorrect_btn),
            ("C", self.show_answer_btn)
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
                self.user.char_timer_value,
                self.user.char_based_timer,
                self.user.no_typing,
                self.user.auto_start,
                self.user.show_correct_sentence,
                self.user.dark_mode])

        # Add sentence list to database if it's not a duplicate and isn't empty
        if self.controller.current_list:
            all_sentence_lists = db.get_all_sentence_lists(connection)
            duplicates = [self.controller.current_list.sentences == json.loads(''.join(sentence_list[0])) 
                for sentence_list in all_sentence_lists]
            if not True in duplicates and self.controller.current_list.sentences and \
                    self.controller.current_list not in self.controller.deleted_lists:
                db.add_sentence_list(
                    connection,
                    json.dumps(self.controller.current_list.sentences),
                    self.controller.current_list.title,
                    self.controller.current_list.num_completed,
                    self.controller.current_list.num_correct)
            else:
                db.update_sentence_list(
                    connection,
                    json.dumps(self.controller.current_list.sentences),
                    self.controller.current_list.title,
                    self.controller.current_list.num_completed,
                    self.controller.current_list.num_correct)

        connection.close()
        self.close()

    def use_sentence_list(self, sentence_list):
        """Update the current sentence list and related labels"""
        db.update_sentence_list(
                connection,
                json.dumps(self.controller.current_list.sentences),
                self.controller.current_list.title,
                self.controller.current_list.num_completed,
                self.controller.current_list.num_correct)
        self.controller.current_list = sentence_list
        self.current_list_label.setText(f"Current List: {self.controller.current_list.title}")
        self.num_list_correct_label.setText(f"List Correct: {self.controller.current_list.num_correct}")
        self.clear_sentence()
        self.clear_answer(False)

    def open_settings(self):
        """Open settings window"""
        self.settings_window = SettingsWindow(self, self.user)
        self.settings_window.show()

    def open_list_settings(self):
        """Open sentence list window"""
        self.sentence_list_window = SentenceListWindow(self)
        self.sentence_list_window.show()

    def add_sentence_list(self):
        self.sentence_act = QAction(f"{self.controller.current_list.title}")
        self.sentence_act.triggered.connect(
            partial(self.use_sentence_list, self.controller.current_list))
        self.menu_actions.append(self.sentence_act)
        self.sentence_menu.addAction(self.sentence_act)
        self.controller.sentence_lists.append(self.controller.current_list)

    def open_file(self):
        """Open a text file and extract the lines as sentences"""
        fname = QFileDialog().getOpenFileName(self, 'Open file', self.user.default_path,
            'Text Files (*.txt)')

        if fname[0]:
            # Add sentence list to database if it's not a duplicate and isn't empty
            all_sentence_lists = db.get_all_sentence_lists(connection)
            duplicates = [self.controller.current_list.sentences == json.loads(''.join(sentence_list[0])) 
                for sentence_list in all_sentence_lists]
            if not True in duplicates and self.controller.current_list:
                db.add_sentence_list(
                    connection,
                    json.dumps(self.controller.current_list.sentences),
                    self.controller.current_list.title,
                    self.controller.current_list.num_completed,
                    self.controller.current_list.num_correct)

            with open(fname[0], 'r') as file:
                duplicates = [os.path.basename(fname[0]) == sentence_list.title
                    for sentence_list in self.controller.sentence_lists]
                if sum(duplicates) <= 1 in duplicates:
                    self.controller.current_list = next((sentence_list for sentence_list in self.controller.sentence_lists
                        if os.path.basename(fname[0]) == sentence_list.title), None)
                else:
                    self.controller.current_list = SentenceList(file.readlines(), os.path.basename(fname[0]))
                    self.add_sentence_list()

                self.current_list_label.setText(f"Current List: {self.controller.current_list.title}")
                self.num_list_correct_label.setText(f"List Correct: {self.controller.current_list.num_correct}")
                self.clear_answer(False)

    def prep_display_sentence(self):
        """Setting up main window to display sentence"""
        self.correct_answer_label.setText("")
        self.correct_or_not_label.setText("")
        self.answer_timer.stop()
        self.resp_timer.stop()

    def get_random_sentence(self):
        """Generate a random sentence from the current sentence list."""
        self.prep_display_sentence()
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
                self.resp_timer.start(len(self.new_sentence) * self.user.char_timer_value)
            else:
                self.resp_timer.start(self.user.timer_duration * 1000)

    def clear_sentence(self):
        """Hide the current sentence"""
        if user.no_typing:
            self.show_answer_btn.show()
            self.sentence_label.setText("Was your answer correct or incorrect?")
        else:
            self.sentence_label.setText("Type the sentence and hit Enter.")
        self.resp_timer.stop()

    def show_answer(self):
        """Show the sentence answer to the user"""
        if self.correct_answer_label.text() == "":
            self.correct_answer_label.setText(self.controller.current_sentence.rstrip())
        else:
            self.correct_answer_label.setText("")

    def init_button_layout(self):
        """Set up the buttons for no typing mode"""
        self.correct_btn = QPushButton("Correct")
        self.correct_btn.clicked.connect(self.correct_btn_click)
        self.incorrect_btn = QPushButton("Incorrect")
        self.incorrect_btn.clicked.connect(self.incorrect_btn_click)
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setAlignment(Qt.AlignHCenter)
        self.btn_layout.addWidget(self.correct_btn)
        self.btn_layout.addWidget(self.incorrect_btn)
        self.layout.addLayout(self.btn_layout)

    def correct_btn_click(self):
        """Slot function for clicking on correct button"""
        if self.sentence_label.text() != "Was your answer correct or incorrect?":
            return

        self.show_answer_btn.hide()
        if self.controller.sentence_active:
            self.controller.current_list.num_completed += 1
            self.correct_answer()
            self.sentence_complete()

    def incorrect_btn_click(self):
        """Slot function for clicking on incorrect button"""
        if self.sentence_label.text() != "Was your answer correct or incorrect?":
            return

        self.show_answer_btn.hide()
        if self.controller.sentence_active:
            self.controller.current_list.num_completed += 1
            self.correct_or_not_label.setText("Incorrect!")
            self.sentence_complete()

    def no_typing_mode(self):
        """Adjust widgets depending on if no typing mode is on"""
        if self.controller.sentence_active:
            self.clear_answer()

        if self.user.no_typing:
            self.input_box.hide()
            self.correct_btn.show()
            self.incorrect_btn.show()
        else:
            self.show_answer_btn.hide()
            self.correct_btn.hide()
            self.incorrect_btn.hide()
            self.input_box.show()

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
        if user.no_typing:
            self.show_answer_btn.hide()
        self.correct_or_not_label.setText("")
        self.sentence_label.setText("Generate a new sentence.")
        self.answer_timer.stop()
        if bool(auto_start) is True:
            self.get_random_sentence()

    def correct_answer(self):
        """Update variables and text when an answer is correct"""
        self.user.num_correct += 1
        self.controller.current_list.num_correct += 1
        self.num_list_correct_label.setText(f"List Correct: {self.controller.current_list.num_correct}")
        self.correct_or_not_label.setText("Correct!")

    def sentence_complete(self):
        """For after the user has given an answer"""
        if self.user.show_correct_sentence:
            self.correct_answer_label.setText(self.controller.current_sentence.rstrip())

        if not self.user.no_typing and self.sentence_label.text() != "Type the sentence and hit Enter.":
            self.resp_timer.stop()

        self.answer_timer.start(2000)
        self.controller.sentence_active = False
        self.input_box.setText("")

    def check_answer(self):
        """Check user input against correct answer"""
        if self.controller.sentence_active:

            self.controller.current_list.num_completed += 1
            if self.input_box.text().rstrip() == self.controller.current_sentence.rstrip():
                self.correct_answer()
            else:
                self.correct_or_not_label.setText("Incorrect!")

            if self.sentence_label.text() != "Type the sentence and hit Enter.":
                self.resp_timer.stop()

            self.sentence_complete()

        else:
            self.get_random_sentence()

    def set_dark_mode(self, dark_mode_bool):
        """Set the application palette"""
        if dark_mode_bool:
            app.setStyle('Fusion')
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53,53,53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(15,15,15))
            palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53,53,53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
                
            palette.setColor(QPalette.Highlight, QColor(78, 118, 206).lighter())
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
        else:
            app.setPalette(default_palette)
            pass

class User():
    """For user-specific statistics and settings"""
    def __init__(self, num_correct=0, default_path="", timer_duration=1, char_timer_value=60,
                char_based_timer=True, no_typing=False, auto_start=False, 
                show_correct_sentence=False, dark_mode=False):
        self.num_correct = num_correct
        self.default_path = default_path
        self.timer_duration = timer_duration
        self.char_timer_value = char_timer_value
        self.char_based_timer = char_based_timer
        self.no_typing = no_typing
        self.auto_start = auto_start
        self.show_correct_sentence = show_correct_sentence
        self.dark_mode = dark_mode

    def __repr__(self):
        print(f"Number correct: {self.num_correct}")
        print(f"Default path: {self.default_path}")
        print(f"Timer duration: {self.timer_duration}")
        print(f"Character timer value: {self.char_timer_value}")
        print(f"Character-based timer: {self.char_based_timer}")
        print(f"No typing: {self.no_typing}")
        print(f"Auto start: {self.auto_start}")
        print(f"Show correct sentence: {self.show_correct_sentence}")
        print(f"Dark mode: {self.dark_mode}")

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
            current_user.char_timer_value,
            current_user.char_based_timer,
            current_user.no_typing,
            current_user.auto_start,
            current_user.show_correct_sentence,
            current_user.dark_mode])
    else:
        # Get the first user (only one user is supported right now)
        current_user = User(users[0][0], users[0][1], users[0][2],
            users[0][3], users[0][4], users[0][5], users[0][6],
            bool(users[0][7]), bool(users[0][8]))

    return current_user

def get_lists_from_db(db):
    """Get sentence lists from database"""
    all_sentence_lists = db.get_all_sentence_lists(connection)

    deserialized_lists = []
    if not all_sentence_lists:
        if os.path.exists('../default_sentences.txt'):
            with open('../default_sentences.txt', 'r') as file:
                new_list = SentenceList(file.readlines())
                deserialized_lists.append(new_list)
                db.add_sentence_list(
                    connection,
                    json.dumps(new_list.sentences),
                    new_list.title,
                    new_list.num_completed,
                    new_list.num_correct)
    else:
        for sentence_list in all_sentence_lists:
            new_list = SentenceList(json.loads(''.join(sentence_list[0])),
                sentence_list[1], sentence_list[2], sentence_list[3])
            deserialized_lists.append(new_list)

    return deserialized_lists

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet("QLabel{font-size: 8pt;}")
    default_palette = QGuiApplication.palette()

    connection = db.create_connection('data.db')
    user = get_user_from_db(db)
    sentence_lists = get_lists_from_db(db)

    controller = Controller(sentence_lists)

    main = MainWindow(user, controller)
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.setMaximumSize(640, 480)
    main.show()
    sys.exit(app.exec_())
