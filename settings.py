from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout, QFormLayout, 
    QLabel, QLineEdit, 
    QCheckBox, QPushButton, 
    QWidget, QMainWindow)

class SettingsWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user

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

    def save_settings(self, user):
        """Set user settings into user object."""
        if self.timer_input.text():
            self.user.timer_duration = int(self.timer_input.text())

        if self.auto_start_CB.isChecked():
            self.user.auto_start = True
        else:
            self.user.auto_start = False

        if self.show_correct_CB.isChecked():
            self.user.show_correct_sentence = True
        else:
            self.user.show_correct_sentence = False

        self.close()