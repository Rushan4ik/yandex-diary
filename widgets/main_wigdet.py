import sqlite3
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

from widgets.homeworks_widget import HomeworksWidget
from widgets.lesson_widget import LessonsWidget
from widgets.subject_widget import SubjectsWidget
from widgets.goals_widget import GoalsWidget


class MainWidget(QWidget):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection
        self.init_ui()

    def init_ui(self):
        grid_layout = QGridLayout()

        self.subjects_button = QPushButton("Subjects", self)
        self.subjects_button.clicked.connect(self.open_subject_widget)
        grid_layout.addWidget(self.subjects_button, 0, 0)

        self.goals_button = QPushButton("Goals", self)
        self.goals_button.clicked.connect(self.open_goal_widget)
        grid_layout.addWidget(self.goals_button, 0, 1)

        self.replacements_button = QPushButton("Replacements", self)
        grid_layout.addWidget(self.replacements_button, 1, 0)

        self.lessons_button = QPushButton("Lessons", self)
        self.lessons_button.clicked.connect(self.open_lessons_widget)
        grid_layout.addWidget(self.lessons_button, 1, 1)

        self.homeworks_button = QPushButton("Homeworks", self)
        self.homeworks_button.clicked.connect(self.open_homeworks_widget)
        grid_layout.addWidget(self.homeworks_button, 2, 0, 1, 2)

        self.setLayout(grid_layout)

    def open_subject_widget(self):
        self.widget = SubjectsWidget(self.connection)
        self.widget.show()

    def open_goal_widget(self):
        self.widget = GoalsWidget(self.connection)
        self.widget.show()

    def open_lessons_widget(self):
        self.widget = LessonsWidget(self.connection)
        self.widget.show()

    def open_homeworks_widget(self):
        self.widget = HomeworksWidget(self.connection)
        self.widget.show()
