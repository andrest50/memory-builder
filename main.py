import sys
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class User():
    def __init__(self):
        self.autoStart = False
        self.timerLength = 3

class Settings(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(400, 240)

        self.settingsBox = QFormLayout()

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setAlignment(Qt.AlignCenter)
        self.settingsLabel.setStyleSheet("font: 12px")
        self.settingsBox.addRow(self.settingsLabel)

        self.timerLabel = QLabel("Timer")
        self.timerInput = QLineEdit()
        self.timerInput.setMaximumWidth(100)
        self.settingsBox.addRow(self.timerLabel, self.timerInput)

        self.autoStartResp = QCheckBox("Auto Start")
        #self.autoStartResp.toggled.connect()
        self.settingsBox.addWidget(self.autoStartResp)

        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.saveSettings)
        self.settingsBox.addWidget(self.saveBtn)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.window.setLayout(self.settingsBox)     

    def saveSettings(self):
        if(self.timerInput.text()):
            print(str(self.timerInput.text()))
            user.timerLength = int(self.timerInput.text())
        if(self.autoStartResp.isChecked()):
            print(str(self.autoStartResp.isChecked()))
            user.autoStart = True
        self.close()
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.createMenuBar()

        self.sentence = QLabel("Open a text file to get started.")
        self.sentence.setAlignment(Qt.AlignCenter)
        self.sentence.setStyleSheet("font: 15px;")

        self.inputBox = QLineEdit("", self)
        self.inputBox.returnPressed.connect(self.checkAnswer)

        self.generateSenBtn = QPushButton("Generate Sentence", self)
        self.generateSenBtn.clicked.connect(self.getRandomSentence)

        self.answerResp = QLabel("")
        self.answerResp.setAlignment(Qt.AlignCenter)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.sentence)
        self.layout.addWidget(self.answerResp)
        self.layout.addWidget(self.inputBox)
        self.layout.addWidget(self.generateSenBtn)
        self.window.setLayout(self.layout)

        self.settingsWindow = Settings()

        self.respTimer = QTimer()
        self.respTimer.timeout.connect(self.clearSentence)

        self.answerTimer = QTimer()
        self.answerTimer.timeout.connect(self.clearAnswer)

        self.data = []
        self.currentSentence = ""
        self.correctAnswers = 0
        self.active = False

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

    def openSettings(self):
        self.settingsWindow.show()

    def openFile(self):
        dialog = QFileDialog()
        fname = QFileDialog().getOpenFileName(self, 'Open file', '/Andres/Text-Files', 
            'Text Files (*.txt)')
        print(fname[0])
        if(fname[0]):
            with open(fname[0], 'r') as file:
                self.data = file.readlines()
    
    def getRandomSentence(self):
        if(len(self.data) > 0):
            self.newSentence = random.choice(self.data)
            while(self.newSentence == self.currentSentence and len(self.data) != 1):
                self.newSentence = random.choice(self.data)
            self.sentence.setText(self.newSentence)
            self.currentSentence = self.newSentence
            self.active = True
            self.inputBox.setFocus()
            self.respTimer.start(user.timerLength * 1000)
            
    def clearSentence(self):
        self.sentence.setText("Type the sentence and hit Enter.")
        self.respTimer.stop()

    def clearAnswer(self):
        self.answerResp.setText("")
        self.sentence.setText("Generate a new sentence.")
        self.answerTimer.stop()

    def checkAnswer(self):
        print(self.inputBox.text().rstrip())
        print(self.currentSentence.rstrip())

        if(self.inputBox.text().rstrip() == self.currentSentence.rstrip() and self.active == True):
            self.correctAnswers += 1
            self.answerResp.setText("Correct!")
        else:
            self.answerResp.setText("Incorrect!")

        self.answerTimer.start(2000)
        self.active = False
        self.inputBox.setText("")

        print(self.correctAnswers)

if __name__ == "__main__":
    app = QApplication([])

    user = User()

    main = Window()
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.show()
    sys.exit(app.exec_())