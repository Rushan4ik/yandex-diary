import sqlite3
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton


class MainWidget(QWidget):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection
        self.init_ui()

    def init_ui(self):
        grid_layout = QGridLayout()
        self.subjects_button = QPushButton("Subjects", self)
        grid_layout.addWidget(self.subjects_button, 0, 0)
        self.goals_button = QPushButton("Goals", self)
        grid_layout.addWidget(self.goals_button, 0, 1)
        self.replacements_button = QPushButton("Replacements", self)
        grid_layout.addWidget(self.replacements_button, 1, 0)
        self.lessons_button = QPushButton("Lessons", self)
        self.lessons_button.
        self.setLayout(grid_layout)

