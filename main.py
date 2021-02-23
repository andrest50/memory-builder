import sys
import os
import json
import copy
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import db

class User():
    def __init__(self):
        self.num_correct = 0
        self.timer_duration = 3
        self.auto_start = False
        self.show_correct_sentence = False

class SentenceList():
    def __init__(self):
        self.sentences = []
        self.num_sentences = 0

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(400, 240)

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
        if(user.auto_start == True):
            self.auto_start_CB.setChecked(True)
        self.settings_box.addWidget(self.auto_start_CB)

        self.show_correct_CB = QCheckBox("Show Correct Answer")
        if(user.show_correct_sentence == True):
            self.show_correct_CB.setChecked(True)
        self.settings_box.addWidget(self.show_correct_CB)

        self.save_btn = QPushButton("Save")
        self.save_btn.setMaximumWidth(100)
        self.save_btn.clicked.connect(self.SaveSettings)
        self.settings_box.addWidget(self.save_btn)

        self.layout.addLayout(self.settings_box)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)     

    def SaveSettings(self):
        if(self.timer_input.text()):
            user.timer_duration = int(self.timer_input.text())
        if(self.auto_start_CB.isChecked()):
            user.auto_start = True
        else:
            user.auto_start = False
        if(self.show_correct_CB.isChecked()):
            user.show_correct_sentence = True
        else:
            user.show_correct_sentence = False
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if sentence_lists:
            self.current_list = copy.deepcopy(sentence_lists[0])
        else:
            self.current_list = SentenceList()

        self.current_sentence = ""
        self.sentence_active = False

        #self.getDefaultSentences()
        self.CreateMenuBar()

        self.num_correct_label = QLabel("Correct: " + str(user.num_correct))
        self.num_correct_label.setAlignment(Qt.AlignRight)

        self.sentence = QLabel("Open a text file to get started or use the default sentences.")
        self.sentence.setAlignment(Qt.AlignCenter)
        self.sentence.setStyleSheet("font: 15px;")

        self.input_box = QLineEdit("", self)
        self.input_box.returnPressed.connect(self.CheckAnswer)

        self.generate_sentence_btn = QPushButton("Generate Sentence", self)
        self.generate_sentence_btn.clicked.connect(self.GetRandomSentence)

        self.correct_answer_label = QLabel("")
        self.correct_answer_label.setAlignment(Qt.AlignCenter)

        self.correct_or_not_label = QLabel("")
        self.correct_or_not_label.setAlignment(Qt.AlignCenter)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.num_correct_label)
        self.layout.addWidget(self.sentence)
        self.layout.addWidget(self.correct_answer_label)
        self.layout.addWidget(self.correct_or_not_label)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.generate_sentence_btn)
        self.window.setLayout(self.layout)

        self.settings_window = SettingsWindow()

        self.resp_timer = QTimer()
        self.resp_timer.timeout.connect(self.ClearSentence)

        self.answer_timer = QTimer()
        self.answer_timer.timeout.connect(self.ClearAnswer)

    def CreateMenuBar(self):
        self.open_file_act = QAction("Open", self)
        self.open_file_act.setShortcut("Ctrl+O")
        self.open_file_act.setStatusTip("Open a file")
        self.open_file_act.triggered.connect(self.OpenFile)

        self.settings_act = QAction("Settings", self)
        self.settings_act.setShortcut("Ctrl+S")
        self.settings_act.triggered.connect(self.OpenSettings)

        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("File")
        self.file_menu.addAction(self.open_file_act)
        self.menubar.addAction(self.settings_act)

    def closeEvent(self, event):
        db.UpdateUser(connection, [user.num_correct, user.timer_duration, user.auto_start, user.show_correct_sentence])
        duplicate = False
        for sentence_list in sentence_lists:
            if self.current_list.sentences == sentence_list.sentences:
                duplicate = True
                break
        if(duplicate == False and self.current_list.sentences):
            json_string = json.dumps(self.current_list.sentences)
            db.AddSentenceList(connection, json_string)
        connection.close()
        self.close()

    def OpenSettings(self):
        self.settings_window.show()

    def OpenFile(self):
        dialog = QFileDialog()
        fname = QFileDialog().getOpenFileName(self, 'Open file', '/Andres/Text-Files', 
            'Text Files (*.txt)')
        if(fname[0]):
            duplicate = False
            for sentence_list in sentence_lists:
                if self.current_list.sentences == sentence_list.sentences:
                    duplicate = True
                    break
            if(duplicate == False and self.current_list.sentences):
                json_string = json.dumps(self.current_list.sentences)
                db.AddSentenceList(connection, json_string)

            with open(fname[0], 'r') as file:
                self.current_list.sentences = file.readlines()
    
    def GetDefaultSentences(self):
        if(os.path.isfile(os.path.dirname(__file__) + '/default-sentences.txt')):
            with open(os.path.dirname(__file__) + '/default-sentences.txt', 'r') as file:
                self.current_list.sentences = file.readlines()

    def GetRandomSentence(self):
        self.correct_answer_label.setText("")
        if(len(self.current_list.sentences) > 0):
            self.new_sentence = random.choice(self.current_list.sentences).rstrip()
            while(self.new_sentence == self.current_sentence and len(self.current_list.sentences) != 1):
                self.new_sentence = random.choice(self.current_list.sentences).rstrip()
            self.sentence.setText(self.new_sentence)
            self.current_sentence = self.new_sentence
            self.sentence_active = True
            self.input_box.setFocus()
            self.resp_timer.start(user.timer_duration * 1000)
            
    def ClearSentence(self):
        self.sentence.setText("Type the sentence and hit Enter.")
        self.resp_timer.stop()

    def ClearAnswer(self):
        self.correct_or_not_label.setText("")
        self.sentence.setText("Generate a new sentence.")
        self.answer_timer.stop()
        if(user.auto_start == True):
            self.GetRandomSentence()

    def CheckAnswer(self):
        if(self.sentence_active):
            print(self.input_box.text().rstrip())
            print(self.current_sentence.rstrip())

            if(self.input_box.text().rstrip() == self.current_sentence.rstrip() and self.sentence_active == True):
                user.num_correct += 1
                self.num_correct_label.setText("Correct: " + str(user.num_correct))
                self.correct_or_not_label.setText("Correct!")
            else:
                self.correct_or_not_label.setText("Incorrect!")

            if(user.show_correct_sentence):
                self.correct_answer_label.setText(self.current_sentence.rstrip())

            if(self.sentence.text() != "Type the sentence and hit Enter."):
                self.resp_timer.stop()

            self.answer_timer.start(2000)
            self.sentence_active = False
            self.input_box.setText("")

def getDBData(db, user):
    data = db.GetAllUsers(connection)
    sentence_lists = db.GetAllSentenceLists(connection)
    print(f"here: {sentence_lists}")

    if(len(data) == 0):
        db.AddUser(connection, [user.num_correct, user.timer_duration, user.auto_start, user.show_correct_sentence])
    else:
        user.num_correct = data[0][0]
        user.timer_duration = data[0][1]
        user.auto_start = data[0][2]
        user.show_correct_sentence = data[0][3]

    deserialized_lists = [] # List of SentenceList objects
    if not sentence_lists:
        if(os.path.isfile(os.path.dirname(__file__) + '/default-sentences.txt')):
            with open(os.path.dirname(__file__) + '/default-sentences.txt', 'r') as file:
                new_list = SentenceList()
                new_list.sentences = file.readlines()
                deserialized_lists.append(new_list)
                print(json.dumps(deserialized_lists[0].sentences))
                db.AddSentenceList(connection, json.dumps(deserialized_lists[0].sentences))
    else:
        for sentence_list in sentence_lists:
            new_list = SentenceList()
            new_list.sentences = json.loads(''.join(sentence_list))
            deserialized_lists.append(new_list)
            print(deserialized_lists[-1])
    
    return deserialized_lists

if __name__ == "__main__":
    app = QApplication([])
    user = User()
    
    connection = db.CreateConnection('data.db')
    sentence_lists = getDBData(db, user)
    print(len(sentence_lists))

    main = MainWindow()
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.show()
    sys.exit(app.exec_())