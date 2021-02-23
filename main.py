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
        self.numCorrect = 0
        self.timerDuration = 3
        self.autoStart = False
        self.showCorrectSentence = False

class SentenceList():
    def __init__(self):
        self.sentences = []
        self.numSentences = 0

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(400, 240)

        self.layout = QVBoxLayout()

        self.settingsBox = QFormLayout()
        self.settingsBox.setAlignment(Qt.AlignHCenter)

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setAlignment(Qt.AlignCenter)
        self.settingsLabel.setStyleSheet("font: 12px")
        self.settingsBox.addRow(self.settingsLabel)

        self.timerLabel = QLabel("Timer")
        self.timerInput = QLineEdit()
        self.timerInput.setText(str(user.timerDuration))
        self.timerInput.setMaximumWidth(100)
        self.settingsBox.addRow(self.timerLabel, self.timerInput)

        self.autoStartCB = QCheckBox("Auto Start")
        if(user.autoStart == True):
            self.autoStartCB.setChecked(True)
        self.settingsBox.addWidget(self.autoStartCB)

        self.showCorrectCB = QCheckBox("Show Correct Answer")
        if(user.showCorrectSentence == True):
            self.showCorrectCB.setChecked(True)
        self.settingsBox.addWidget(self.showCorrectCB)

        self.saveBtn = QPushButton("Save")
        self.saveBtn.setMaximumWidth(100)
        self.saveBtn.clicked.connect(self.saveSettings)
        self.settingsBox.addWidget(self.saveBtn)

        self.layout.addLayout(self.settingsBox)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)     

    def saveSettings(self):
        if(self.timerInput.text()):
            user.timerDuration = int(self.timerInput.text())
        if(self.autoStartCB.isChecked()):
            user.autoStart = True
        else:
            user.autoStart = False
        if(self.showCorrectCB.isChecked()):
            user.showCorrectSentence = True
        else:
            user.showCorrectSentence = False
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if sentenceLists:
            self.currentList = copy.deepcopy(sentenceLists[0])
        else:
            self.currentList = SentenceList()

        self.currentSentence = ""
        self.sentenceActive = False

        #self.getDefaultSentences()
        self.createMenuBar()

        self.numCorrectLabel = QLabel("Correct: " + str(user.numCorrect))
        self.numCorrectLabel.setAlignment(Qt.AlignRight)

        self.sentence = QLabel("Open a text file to get started or use the default sentences.")
        self.sentence.setAlignment(Qt.AlignCenter)
        self.sentence.setStyleSheet("font: 15px;")

        self.inputBox = QLineEdit("", self)
        self.inputBox.returnPressed.connect(self.checkAnswer)

        self.generateSenBtn = QPushButton("Generate Sentence", self)
        self.generateSenBtn.clicked.connect(self.getRandomSentence)

        self.correctAnsLabel = QLabel("")
        self.correctAnsLabel.setAlignment(Qt.AlignCenter)

        self.correctOrNotLabel = QLabel("")
        self.correctOrNotLabel.setAlignment(Qt.AlignCenter)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.numCorrectLabel)
        self.layout.addWidget(self.sentence)
        self.layout.addWidget(self.correctAnsLabel)
        self.layout.addWidget(self.correctOrNotLabel)
        self.layout.addWidget(self.inputBox)
        self.layout.addWidget(self.generateSenBtn)
        self.window.setLayout(self.layout)

        self.settingsWindow = SettingsWindow()

        self.respTimer = QTimer()
        self.respTimer.timeout.connect(self.clearSentence)

        self.answerTimer = QTimer()
        self.answerTimer.timeout.connect(self.clearAnswer)

    def createMenuBar(self):
        self.openFileAct = QAction("Open", self)
        self.openFileAct.setShortcut("Ctrl+O")
        self.openFileAct.setStatusTip("Open a file")
        self.openFileAct.triggered.connect(self.openFile)

        self.settingsAct = QAction("Settings", self)
        self.settingsAct.setShortcut("Ctrl+S")
        self.settingsAct.triggered.connect(self.openSettings)

        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openFileAct)
        self.menubar.addAction(self.settingsAct)

    def closeEvent(self, event):
        db.update_user(connection, [user.numCorrect, user.timerDuration, user.autoStart, user.showCorrectSentence])
        duplicate = False
        for sentenceList in sentenceLists:
            if self.currentList.sentences == sentenceList.sentences:
                duplicate = True
                break
        if(duplicate == False and self.currentList.sentences):
            json_string = json.dumps(self.currentList.sentences)
            db.add_sentence_list(connection, json_string)
        connection.close()
        self.close()

    def openSettings(self):
        self.settingsWindow.show()

    def openFile(self):
        dialog = QFileDialog()
        fname = QFileDialog().getOpenFileName(self, 'Open file', '/Andres/Text-Files', 
            'Text Files (*.txt)')
        if(fname[0]):
            duplicate = False
            for sentenceList in sentenceLists:
                if self.currentList.sentences == sentenceList.sentences:
                    duplicate = True
                    break
            if(duplicate == False and self.currentList.sentences):
                json_string = json.dumps(self.currentList.sentences)
                db.add_sentence_list(connection, json_string)

            with open(fname[0], 'r') as file:
                self.currentList.sentences = file.readlines()
    
    def getDefaultSentences(self):
        if(os.path.isfile(os.path.dirname(__file__) + '/default-sentences.txt')):
            with open(os.path.dirname(__file__) + '/default-sentences.txt', 'r') as file:
                self.currentList.sentences = file.readlines()

    def getRandomSentence(self):
        self.correctAnsLabel.setText("")
        if(len(self.currentList.sentences) > 0):
            self.newSentence = random.choice(self.currentList.sentences).rstrip()
            while(self.newSentence == self.currentSentence and len(self.currentList.sentences) != 1):
                self.newSentence = random.choice(self.currentList.sentences).rstrip()
            self.sentence.setText(self.newSentence)
            self.currentSentence = self.newSentence
            self.sentenceActive = True
            self.inputBox.setFocus()
            self.respTimer.start(user.timerDuration * 1000)
            
    def clearSentence(self):
        self.sentence.setText("Type the sentence and hit Enter.")
        self.respTimer.stop()

    def clearAnswer(self):
        self.correctOrNotLabel.setText("")
        self.sentence.setText("Generate a new sentence.")
        self.answerTimer.stop()
        if(user.autoStart == True):
            self.getRandomSentence()

    def checkAnswer(self):
        if(self.sentenceActive):
            print(self.inputBox.text().rstrip())
            print(self.currentSentence.rstrip())

            if(self.inputBox.text().rstrip() == self.currentSentence.rstrip() and self.sentenceActive == True):
                user.numCorrect += 1
                self.numCorrectLabel.setText("Correct: " + str(user.numCorrect))
                self.correctOrNotLabel.setText("Correct!")
            else:
                self.correctOrNotLabel.setText("Incorrect!")

            if(user.showCorrectSentence):
                self.correctAnsLabel.setText(self.currentSentence.rstrip())

            if(self.sentence.text() != "Type the sentence and hit Enter."):
                self.respTimer.stop()

            self.answerTimer.start(2000)
            self.sentenceActive = False
            self.inputBox.setText("")

def getDBData(db, user):
    data = db.get_all_users(connection)
    sentenceLists = db.get_all_sentence_lists(connection)
    print(f"here: {sentenceLists}")

    if(len(data) == 0):
        db.add_user(connection, [user.numCorrect, user.timerDuration, user.autoStart, user.showCorrectSentence])
    else:
        user.numCorrect = data[0][0]
        user.timerDuration = data[0][1]
        user.autoStart = data[0][2]
        user.showCorrectSentence = data[0][3]

    deserializedLists = [] # List of SentenceList objects
    if not sentenceLists:
        if(os.path.isfile(os.path.dirname(__file__) + '/default-sentences.txt')):
            with open(os.path.dirname(__file__) + '/default-sentences.txt', 'r') as file:
                newList = SentenceList()
                newList.sentences = file.readlines()
                deserializedLists.append(newList)
                print(json.dumps(deserializedLists[0].sentences))
                db.add_sentence_list(connection, json.dumps(deserializedLists[0].sentences))
    else:
        for sentenceList in sentenceLists:
            newList = SentenceList()
            newList.sentences = json.loads(''.join(sentenceList))
            deserializedLists.append(newList)
            print(deserializedLists[-1])
    
    return deserializedLists

if __name__ == "__main__":
    app = QApplication([])
    user = User()
    
    connection = db.create_connection('data.db')
    sentenceLists = getDBData(db, user)
    print(len(sentenceLists))

    main = MainWindow()
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.show()
    sys.exit(app.exec_())