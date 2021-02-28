import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import db

class SentenceListWindow(QMainWindow):
    """Main window for sentence list settings"""
    def __init__(self, mw):
        super().__init__()

        self.mw = mw

        self.connection = db.create_connection('data.db')

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
        self.connection.close() # Close database connection

    def stack_sentence_lists(self):
        """Set up sentence list stack and associated settings"""
        for index, sentence_list in enumerate(self.mw.controller.sentence_lists):
            self.stack_item = SentenceListStackItem(self, self.mw, sentence_list, index)
            self.list_stack_info.insertItem(index, f"{sentence_list.title}")
            self.stack_item.setLayout(self.stack_item.info_layout)
            self.list_stack.addWidget(self.stack_item)

    def display_list_settings(self, index):
        """Display the current stack item's settings"""
        self.list_stack.setCurrentIndex(index)

class SentenceListStackItem(QWidget):
    """List widget item for each sentence list"""
    def __init__(self, parent, mw, sentence_list, index):
        super().__init__()

        self.parent = parent
        self.mw = mw
        self.controller = self.mw.controller
        self.connection = parent.connection
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
            old_title = self.sentence_list.title
            self.sentence_list.title = self.rename_line.text()
            action_idx = self.controller.sentence_lists.index(self.sentence_list)
          
            try:
                self.mw.menu_actions[action_idx].setText(self.sentence_list.title)
            except ValueError:
                print("Not found")
           
            self.list_name_label.setText(self.rename_line.text())
            self.parent.list_stack_info.item(action_idx).setText(self.rename_line.text())
            if old_title in self.mw.current_list_label.text():
                self.mw.current_list_label.setText(f"Current List: {self.rename_line.text()}")
            self.rename_line.setText("")
          
            db.update_sentence_list(
                self.connection,
                json.dumps(self.sentence_list.sentences),
                self.sentence_list.title,
                self.sentence_list.num_correct)

    def delete_list(self):
        """Delete a sentence_list, which deletes it from the database"""
        if not self.sentence_list:
            return

        db.delete_sentence_list(self.connection, json.dumps(self.sentence_list.sentences))
        self.controller.deleted_lists.append(self.sentence_list)
        action_idx = self.controller.sentence_lists.index(self.sentence_list)
     
        try:
            self.mw.sentence_menu.removeAction(self.mw.menu_actions[action_idx])
            self.mw.menu_actions.pop(action_idx)
        except ValueError:
            print("Not found")
      
        self.controller.sentence_lists.remove(self.sentence_list)
        if self.controller.current_list == self.sentence_list:
            if self.controller.sentence_lists:
                self.mw.use_sentence_list(self.controller.sentence_lists[0])
            else:
                self.mw.no_lists_available()

        #self.sentence_list = None
        self.parent.list_stack_info.takeItem(self.index)

class SentenceList():
    """For lists of sentences imported from a text file and stored in the database"""
    def __init__(self, sentences=None, title="Default", num_correct=0):
        self.sentences = sentences
        self.title = title
        self.num_correct = num_correct

    def __eq__(self, other):
        return self.sentences == other.sentences