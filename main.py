import sys
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

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

        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.sentence)
        self.layout.addWidget(self.inputBox)
        self.layout.addWidget(self.generateSenBtn)
        self.window.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.clearSentence)

        self.data = []
        self.currentSentence = ""
        self.correctAnswers = 0
        self.active = False

    def createMenuBar(self):
        self.openFileAct = QAction("Open", self)
        self.openFileAct.setShortcut("Ctrl+O")
        self.openFileAct.setStatusTip("Open a file")
        self.openFileAct.triggered.connect(self.openFile)

        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openFileAct)
        self.settingsMenu = self.menubar.addMenu("Settings")

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
            self.currentSentence = random.choice(self.data)
            while(self.currentSentence == self.sentence.text() and len(self.data) != 1):
                self.currentSentence = random.choice(self.data)
            self.sentence.setText(self.currentSentence)
            self.active = True
            self.inputBox.setFocus()
            self.timer.start(3000)
            
    def clearSentence(self):
        self.sentence.setText("Type the sentence and hit Enter.")

    def checkAnswer(self):
        print(self.inputBox.text().rstrip())
        print(self.currentSentence.rstrip())
        if(self.inputBox.text().rstrip() == self.currentSentence.rstrip() and self.active == True):
            self.correctAnswers += 1
        self.active = False
        self.inputBox.setText("")
        print(self.correctAnswers)

if __name__ == "__main__":
    app = QApplication([])

    main = Window()
    main.setWindowTitle("Memory Builder")
    main.resize(480, 320)
    main.show()
    sys.exit(app.exec_())