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

"""
To Do:
- When a file is opened, the list should appear in the list settings
- When a list is deleted, it should no longer appear in the list menu dropdown
- When a file is renamed, the stack item's text should change to match the new name
"""

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self, sentence_lists):
        super().__init__()

        self.sentence_lists = sentence_lists
        self.deleted_lists = []

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.menu_actions = []

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
        self.answer_timer.timeout.connect(partial(self.clear_answer, user.auto_start))

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
        self.sentence_settings_act.setShortcut("Ctrl+L")
        self.sentence_settings_act.triggered.connect(self.open_list_settings)
        self.sentence_menu.addAction(self.sentence_settings_act)
        for sentence_list in self.sentence_lists:
            print(sentence_list)
            self.sentence_act = QAction(f"{sentence_list.title}")
            self.sentence_act.triggered.connect(partial(self.use_sentence_list, sentence_list))
            self.menu_actions.append(self.sentence_act)
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
        print(self.current_list)
        all_sentence_lists = db.get_all_sentence_lists(connection)
        duplicates = [self.current_list.sentences == json.loads(''.join(sentence_list[0])) for sentence_list in all_sentence_lists]
        print(duplicates)
        if not True in duplicates and self.current_list.sentences and self.current_list not in self.deleted_lists:
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
        if self.sentence_lists:
            self.current_list = self.sentence_lists[0]
        else:
            self.current_list = SentenceList()

    def print_all_lists(self):
        for sentence_list in self.sentence_lists:
            print(sentence_list.sentences)
            print(sentence_list.title)
            print(sentence_list.num_correct)

    def use_sentence_list(self, sentence_list):
        """Update the current sentence list and related labels"""
        print(f"{self.current_list.title} {self.current_list.num_correct}")
        self.print_all_lists()
        db.update_sentence_list(
                connection,
                json.dumps(self.current_list.sentences),
                self.current_list.title,
                self.current_list.num_correct)
        self.current_list = sentence_list
        self.current_list_label.setText(f"Current List: {self.current_list.title}")
        self.num_list_correct_label.setText(f"List Correct: {self.current_list.num_correct}")
        #time.sleep(0.5)
        self.clear_sentence()
        self.clear_answer(False)

    def open_settings(self):
        """Open settings window"""
        self.settings_window = SettingsWindow(user)
        self.settings_window.show()

    def open_list_settings(self):
        """Open sentence list window"""
        self.sentence_list_window = SentenceListWindow(self)
        self.sentence_list_window.show()

    def open_file(self):
        """Open a text file and extract the lines as sentences"""
        fname = QFileDialog().getOpenFileName(self, 'Open file', '/Andres/Text-Files',
            'Text Files (*.txt)')

        if fname[0]:
            # Add sentence list to database if it's not a duplicate and isn't empty
            all_sentence_lists = db.get_all_sentence_lists(connection)
            duplicates = [self.current_list.sentences == json.loads(''.join(sentence_list[0])) for sentence_list in all_sentence_lists]
            print(duplicates)
            if not True in duplicates and self.current_list.sentences:
                db.add_sentence_list(
                    connection,
                    json.dumps(self.current_list.sentences),
                    self.current_list.title,
                    self.current_list.num_correct)

            with open(fname[0], 'r') as file:
                duplicates = [fname[0] == sentence_list.title for sentence_list in self.sentence_lists]
                if sum(duplicates) <= 1 in duplicates:
                    self.current_list.sentences = file.readlines()
                    self.current_list.title = fname[0]
                else:
                    self.current_list = SentenceList(file.readlines(), fname[0])
                    self.sentence_act = QAction(f"{self.current_list.title}")
                    self.sentence_act.triggered.connect(
                        partial(self.use_sentence_list, self.current_list))
                    self.menu_actions.append(self.sentence_act)
                    self.sentence_menu.addAction(self.sentence_act)
                    self.sentence_lists.append(self.current_list)
                    print(self.current_list.title)

                self.current_list_label.setText(f"Current List: {self.current_list.title}")
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

    def no_lists_available(self):
        self.clear_current_list_label()
        self.sentence.setText("Type the sentence and hit Enter.")
        self.correct_or_not_label.setText("")
        self.sentence.setText("Generate a new sentence.")
        self.num_list_correct_label.setText("List Correct: 0")

    def clear_current_list_label(self):
        """Clear the text for the current list label"""
        self.current_list_label.setText("Current List: ")

    def clear_answer(self, auto_start):
        """Hide the answer label (correct or incorrect)"""
        self.correct_or_not_label.setText("")
        self.sentence.setText("Generate a new sentence.")
        self.answer_timer.stop()
        if auto_start is True:
            self.get_random_sentence()

    def check_answer(self):
        """Check user input against correct answer"""
        if self.sentence_active:

            if self.input_box.text().rstrip() == self.current_sentence.rstrip()\
                    and self.sentence_active is True:
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

        else:
            self.get_random_sentence()

class SentenceListWindow(QMainWindow):
    """Main window for sentence list settings"""
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

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

        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)

    def closeEvent(self, event):
        pass

    def stack_sentence_lists(self):
        """Set up sentence list stack and associated settings"""
        self.stack = []

        for index, sentence_list in enumerate(sentence_lists):
            self.stack_item = SentenceListStackItem(self, sentence_list, index)
            print(self.stack_item.list_name_label.text())
            self.list_stack_info.insertItem(index, f"{sentence_list.title}")
            self.stack.append(self.stack_item)
            self.stack[index].setLayout(self.stack_item.info_layout)
            self.list_stack.addWidget(self.stack[index])

    def display_list_settings(self, index):
        """Display the current stack item's settings"""
        self.list_stack.setCurrentIndex(index)

    def update_list_label(self, title):
        #self.list_stack_info.currentRow.setText(f"{title}")
        pass

class SentenceListStackItem(QWidget):
    """List widget item for each sentence list"""
    def __init__(self, parent, sentence_list, index):
        super().__init__()

        self.parent = parent
        self.sentence_list = sentence_list
        self.index = index

        self.info_layout = QFormLayout()

        self.list_name_label = QLabel(f"{sentence_list.title}")
        self.info_layout.addRow(self.list_name_label)

        self.rename_line = QLineEdit()
        self.info_layout.addRow("Rename: ", self.rename_line)

        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_changes)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_list)
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.delete_btn)
        self.button_layout.setContentsMargins(0, 50, 0, 0)
        self.info_layout.addRow(self.button_layout)

    def save_changes(self):
        """Save changes made to sentence list settings"""
        if self.rename_line:
            print(self.rename_line.text())
            self.sentence_list.title = self.rename_line.text()
            action_idx = sentence_lists.index(self.sentence_list)
            if action_idx:
                self.parent.parent.menu_actions[action_idx].setText(self.sentence_list.title)
            self.list_name_label.setText(self.rename_line.text())
            self.parent.list_stack_info.item(action_idx).setText(self.rename_line.text())
            self.rename_line.setText("")
            db.update_sentence_list(
                connection,
                json.dumps(self.sentence_list.sentences),
                self.sentence_list.title,
                self.sentence_list.num_correct)
 
    def delete_list(self):
        """Delete a sentence_list, which deletes it from the database"""
        if not self.sentence_list:
            return
        db.delete_sentence_list(
            connection,
            json.dumps(self.sentence_list.sentences))
        action_idx = sentence_lists.index(self.sentence_list)
        self.parent.parent.deleted_lists.append(self.sentence_list)
        try:
            self.parent.parent.sentence_menu.removeAction(self.parent.parent.menu_actions[action_idx])
        except ValueError:
            print("Not found")
        sentence_lists.remove(self.sentence_list)
        if self.parent.parent.current_list == self.sentence_list:
            if sentence_lists:
                self.parent.parent.use_sentence_list(sentence_lists[0])
            else:
                self.parent.parent.no_lists_available()
        self.sentence_list = None
        self.parent.list_stack_info.takeItem(self.index)

class SentenceList():
    """For lists of sentences imported from a text file and stored in the database"""
    def __init__(self, sentences=None, title="Default", num_correct=0):
        self.sentences = sentences
        self.title = title
        self.num_correct = num_correct

    def __eq__(self, other):
        return self.sentences == other.sentences

class User():
    """For user-specific statistics and settings"""
    def __init__(self, num_correct = 0, timer_duration = 1,
                auto_start = False, show_correct_sentence = False):
        self.num_correct = num_correct
        self.timer_duration = timer_duration
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
            current_user.timer_duration,
            current_user.auto_start,
            current_user.show_correct_sentence])
    else:
        # Get the first user (only one user is supported right now)
        current_user = User(users[0][0], users[0][1], users[0][2], users[0][3])

    return current_user

def get_lists_from_db(db):
    """Get sentence lists from database"""
    all_sentence_lists = db.get_all_sentence_lists(connection)

    deserialized_lists = []
    print(all_sentence_lists)
    if not all_sentence_lists:
        print("here")
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
        for sentence_list in all_sentence_lists:
            sentences = json.loads(''.join(sentence_list[0]))
            new_list = SentenceList(sentences, sentence_list[1], sentence_list[2])
            deserialized_lists.append(new_list)

    print(deserialized_lists)
    return deserialized_lists

if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet("QLabel{font-size: 8pt;}")

    connection = db.create_connection('data.db')
    user = get_user_from_db(db)
    sentence_lists = get_lists_from_db(db)

    main = MainWindow(sentence_lists)
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.show()
    sys.exit(app.exec_())
