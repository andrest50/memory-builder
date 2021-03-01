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

        self.resize(250, 150)
        self.setWindowTitle("Settings")

        self.layout = QVBoxLayout()

        self.settings_box = QFormLayout()
        self.settings_box.setAlignment(Qt.AlignHCenter)

        self.settings_label = QLabel("Settings")
        self.settings_label.setAlignment(Qt.AlignCenter)
        self.settings_label.setStyleSheet("font: 12px")
        self.settings_box.addRow(self.settings_label)

        self.path_label = QLabel("Default Path")
        self.path_input = QLineEdit()
        self.path_input.setText(str(user.default_path))
        self.path_input.setMaximumWidth(150)
        self.settings_box.addRow(self.path_label, self.path_input)

        self.timer_label = QLabel("Timer")
        self.timer_input = QLineEdit()
        self.timer_input.setText(str(user.timer_duration))
        self.timer_input.setMaximumWidth(150)
        self.settings_box.addRow(self.timer_label, self.timer_input)

        self.char_based_timer_cb = QCheckBox("Characater length-based Timer")
        if bool(user.char_based_timer) is True:
            self.char_based_timer_cb.setChecked(True)
        self.settings_box.addWidget(self.char_based_timer_cb)

        self.auto_start_cb = QCheckBox("Auto Start")
        if bool(user.auto_start) is True:
            self.auto_start_cb.setChecked(True)
        self.settings_box.addWidget(self.auto_start_cb)

        self.show_correct_cb = QCheckBox("Show Correct Answer")
        if user.show_correct_sentence is True:
            self.show_correct_cb.setChecked(True)
        self.settings_box.addWidget(self.show_correct_cb)

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
        if self.path_input.text():
            self.user.default_path = self.path_input.text()

        if self.timer_input.text():
            self.user.timer_duration = int(self.timer_input.text())

        if self.char_based_timer_cb.isChecked():
            self.user.char_based_timer = True
        else:
            self.user.char_based_timer = False

        if self.auto_start_cb.isChecked():
            self.user.auto_start = True
        else:
            self.user.auto_start = False

        if self.show_correct_cb.isChecked():
            self.user.show_correct_sentence = True
        else:
            self.user.show_correct_sentence = False

        self.close()
