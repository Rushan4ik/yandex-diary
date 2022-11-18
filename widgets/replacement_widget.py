import sqlite3

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox, QLabel


class ReplacementsWidget(QWidget):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection
        query = 'SELECT replacement_id, lesson_id, subject_id FROM replacements;'
        cursor = self.connection.execute(query)
        self.result = [(int(identifier), int(lesson), int(subject))
                       for identifier, lesson, subject in cursor.fetchall()]
        query = 'select subject_id, subject_name from subjects'
        cursor.execute(query)
        self.subject_id = {}
        self.subject_name = {}
        for identifier, name in cursor.fetchall():
            self.subject_id[name] = int(identifier)
            self.subject_name[int(identifier)] = name
        query = 'select lesson_id, lesson_day, lesson_order, subject_name ' \
                'from lessons left join subjects on lessons.subject_id = subjects.subject_id;'
        cursor.execute(query)
        self.lessons = {int(identifier): (int(day), int(order), name)
                        for identifier, day, order, name in cursor.fetchall()}
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self.insert_replacement)
        grid.addWidget(create_button, 0, 0, 1, 3)
        grid.addWidget(QLabel("Lesson", self), 1, 0)
        grid.addWidget(QLabel("Subject", self), 1, 1)
        index = 2
        for identifier, lesson_id, subject_id in self.result:
            lesson_combo = QComboBox(self)
            lesson_combo.addItems(f"{item[0]}.{item[1]} {item[2]}" for item in self.lessons.values())
            lesson_combo.setCurrentIndex(list(self.lessons.keys()).index(lesson_id))
            lesson_combo.currentIndexChanged.connect(self.create_lesson_handler(identifier))
            grid.addWidget(lesson_combo, index, 0)

            subject_combo = QComboBox(self)
            subject_combo.addItems(self.subject_name.values())
            subject_combo.setCurrentIndex(list(self.subject_name.keys()).index(subject_id))
            subject_combo.currentIndexChanged.connect(self.create_subject_handler(identifier))
            grid.addWidget(subject_combo, index, 1)

            remove_button = QPushButton("Remove", self)
            remove_button.clicked.connect(self.create_remove_handler(identifier))
            grid.addWidget(remove_button, index, 2)

            index += 1

        self.setLayout(grid)

    def create_subject_handler(self, identifier):
        return lambda: self.update_subject_id(identifier)

    def create_lesson_handler(self, identifier):
        return lambda: self.update_lesson_id(identifier)

    def create_remove_handler(self, identifier):
        return lambda: self.remove_replacement(identifier)

    def update_subject_id(self, identifier):
        subject_id = self.subject_id[self.sender().currentText()]
        query = "update replacements set subject_id = ? where replacement_id = ?"
        self.connection.execute(query, (subject_id, identifier))
        self.connection.commit()

    def update_lesson_id(self, identifier):
        lesson_id = 0
        for key, item in self.lessons:
            item = f"{item[0]}.{item[1]} {item[2]}"
            if item == self.sender().currentText():
                lesson_id = key
                return
        query = "update replacements set lesson_id = ? where replacement_id = ?"
        self.connection.execute(query, (lesson_id, identifier))
        self.connection.commit()

    def remove_replacement(self, identifier):
        self.sender().setEnabled(False)
        query = "delete from replacements where replacement_id = ?"
        self.connection.execute(query, (identifier,))
        self.connection.commit()

    def insert_replacement(self):
        subject_key = 0
        lesson_key = 0
        for lesson_key, subject_key in zip(self.lessons.keys(), self.subject_name.keys()):
            break
        query = "insert into replacements(subject_id, lesson_id) values (?, ?) returning lesson_id"
        identifier = int(self.connection.execute(query, (subject_key, lesson_key)).fetchone()[0])
        self.connection.commit()

        grid = self.layout()
        index = grid.rowCount() + 1
        lesson_combo = QComboBox(self)
        lesson_combo.addItems(f"{item[0]}.{item[1]} {item[2]}" for item in self.lessons.values())
        lesson_combo.setCurrentIndex(list(self.lessons.keys()).index(lesson_key))
        lesson_combo.currentIndexChanged.connect(self.create_lesson_handler(identifier))
        grid.addWidget(lesson_combo, index, 0)

        subject_combo = QComboBox(self)
        subject_combo.addItems(self.subject_name.values())
        subject_combo.setCurrentIndex(list(self.subject_name.keys()).index(subject_key))
        subject_combo.currentIndexChanged.connect(self.create_subject_handler(identifier))
        grid.addWidget(subject_combo, index, 1)

        remove_button = QPushButton("Remove", self)
        remove_button.clicked.connect(self.create_remove_handler(identifier))
        grid.addWidget(remove_button, index, 2)

