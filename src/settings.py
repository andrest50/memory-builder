"""User settings window"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QWidget,
    QMainWindow,
    QSlider,
    QSpinBox,
    QTabWidget,
    QGridLayout,
)


class SettingsWindow(QMainWindow):
    def __init__(self, mw, user):
        super().__init__()
        self.mw = mw
        self.user = user

        self.resize(260, 150)
        self.setWindowTitle("Settings")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)

        self.settings_label = QLabel("Settings")
        self.settings_label.setAlignment(Qt.AlignCenter)
        self.settings_label.setStyleSheet("font: 12px")
        self.layout.addWidget(self.settings_label)

        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.timer_tab = QWidget()
        self.shortcut_tab = QWidget()
        self.main_tab_content()
        self.timer_tab_content()
        self.shortcut_tab_content()
        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.timer_tab, "Timer")
        self.tabs.addTab(self.shortcut_tab, "Shortcuts")
        self.layout.addWidget(self.tabs)

        self.save_btn = QPushButton("Save")
        self.save_btn.setMaximumWidth(100)
        self.save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_btn)
        self.layout.setAlignment(self.save_btn, Qt.AlignHCenter)

        self.window = QWidget(self)
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)

    def main_tab_content(self):
        """Widgets for the main tab"""
        self.main_settings_box = QFormLayout()
        self.main_settings_box.setAlignment(Qt.AlignHCenter)

        self.path_label = QLabel("Default Path")
        self.path_input = QLineEdit()
        self.path_input.setText(str(self.user.default_path))
        self.path_input.setMaximumWidth(150)
        self.main_settings_box.addRow(self.path_label, self.path_input)

        self.no_typing_cb = QCheckBox("No Typing")
        if bool(self.user.no_typing) is True:
            self.no_typing_cb.setChecked(True)
        self.main_settings_box.addWidget(self.no_typing_cb)

        self.show_correct_cb = QCheckBox("Show Correct Answer")
        if self.user.show_correct_sentence is True:
            self.show_correct_cb.setChecked(True)
        self.main_settings_box.addWidget(self.show_correct_cb)

        self.dark_mode_cb = QCheckBox("Dark Mode")
        if self.user.dark_mode is True:
            self.dark_mode_cb.setChecked(True)
        self.main_settings_box.addWidget(self.dark_mode_cb)

        self.main_tab.setLayout(self.main_settings_box)

    def timer_tab_content(self):
        """Widgets for the timer tab"""
        self.timer_settings_box = QFormLayout()
        self.timer_settings_box.setAlignment(Qt.AlignHCenter)

        self.timer_label = QLabel("Timer")
        self.timer_input = QSpinBox()
        self.timer_input.setValue(self.user.timer_duration)
        self.timer_input.setMaximumWidth(50)
        self.timer_settings_box.addRow(self.timer_label, self.timer_input)

        self.char_timer_label = QLabel(f"ms/character: {self.user.char_timer_value}")
        self.char_timer_slider = QSlider(Qt.Horizontal, self)
        self.char_timer_slider.setValue(self.user.char_timer_value)
        self.char_timer_slider.setRange(10, 150)
        self.char_timer_slider.valueChanged.connect(self.change_slider_value)
        self.timer_settings_box.addRow(self.char_timer_label, self.char_timer_slider)

        self.char_based_timer_cb = QCheckBox("Characater length-based Timer")
        if bool(self.user.char_based_timer) is True:
            self.char_based_timer_cb.setChecked(True)
        self.timer_settings_box.addWidget(self.char_based_timer_cb)

        self.auto_start_cb = QCheckBox("Auto Start")
        if bool(self.user.auto_start) is True:
            self.auto_start_cb.setChecked(True)
        self.timer_settings_box.addWidget(self.auto_start_cb)

        self.timer_tab.setLayout(self.timer_settings_box)

    def shortcut_tab_content(self):
        """Widgets for the shortcuts tab"""
        self.shortcut_grid = QGridLayout()
        # self.generate_sentence_sc = QLabel("<b>Generate:</b> Space")
        self.open_file_sc = QLabel("<b>Open File:</b> Ctrl+O")
        self.settings_sc = QLabel("<b>Settings:</b> Ctrl+S")
        self.list_settings_sc = QLabel("<b>List Settings:</b> Ctrl+L")
        self.show_answer_sc = QLabel("<b>Show Answer:</b> C")
        self.correct_sc = QLabel("<b>Correct:</b> Z")
        self.incorrect_sc = QLabel("<b>Incorrect:</b> X")
        self.shortcut_grid.setColumnStretch(1, 4)
        # self.shortcut_grid.addWidget(self.generate_sentence_sc)
        self.shortcut_grid.addWidget(self.open_file_sc)
        self.shortcut_grid.addWidget(self.settings_sc)
        self.shortcut_grid.addWidget(self.list_settings_sc)
        self.shortcut_grid.addWidget(self.show_answer_sc)
        self.shortcut_grid.addWidget(self.correct_sc)
        self.shortcut_grid.addWidget(self.incorrect_sc)
        self.shortcut_tab.setLayout(self.shortcut_grid)

    def change_slider_value(self, value):
        """Slot function for characters per millisecond slider widget"""
        self.user.char_timer_value = value
        self.char_timer_label.setText(f"ms/character: {str(value)}")

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

        if self.no_typing_cb.isChecked():
            self.user.no_typing = True
        else:
            self.user.no_typing = False

        if self.auto_start_cb.isChecked():
            self.user.auto_start = True
        else:
            self.user.auto_start = False

        if self.show_correct_cb.isChecked():
            self.user.show_correct_sentence = True
        else:
            self.user.show_correct_sentence = False

        if self.dark_mode_cb.isChecked():
            self.mw.set_dark_mode(True)
            self.user.dark_mode = True
        else:
            self.mw.set_dark_mode(False)
            self.user.dark_mode = False

        self.mw.no_typing_mode()
        self.close()
