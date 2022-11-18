import sqlite3

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLineEdit, QComboBox, QLabel

STATES = {
    0: 'CANCELED',
    1: 'PLANED',
    2: 'IN_PROCESS',
    3: 'IS_DONE'
}


class HomeworksWidget(QWidget):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection
        query = "SELECT homework_id, subject_name, homework_description, homework_state " \
                "FROM homeworks LEFT JOIN subjects ON homeworks.subject_id = subjects.subject_id;"
        cursor = self.connection.execute(query)
        self.result = [(int(identifier), name, description, int(state))
                       for identifier, name, description, state in cursor.fetchall()]
        query = "select subject_id, subject_name from subjects"
        cursor.execute(query)
        self.subject_id = {}
        self.subject_name = {}
        for identifier, name in cursor.fetchall():
            identifier = int(identifier)
            self.subject_name[identifier] = name
            self.subject_id[name] = identifier
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self.insert_homework)
        grid.addWidget(create_button, 0, 0, 1, 4)
        grid.addWidget(QLabel("Description", self), 1, 0)
        grid.addWidget(QLabel("Subject", self), 1, 1)
        grid.addWidget(QLabel("State", self), 1, 2)
        index = 2
        for identifier, name, description, state in sorted(self.result, key=lambda x: -x[3]):
            line_edit = QLineEdit(description, self)
            line_edit.editingFinished.connect(self.create_description_handler(identifier))
            grid.addWidget(line_edit, index, 0)
            subject_combo = QComboBox(self)
            subject_combo.addItems(self.subject_name.values())
            subject_combo.setCurrentIndex(list(self.subject_name.values()).index(name))
            subject_combo.currentIndexChanged.connect(self.create_subject_handler(identifier))
            subject_combo.currentText()
            grid.addWidget(subject_combo, index, 1)
            state_combo = QComboBox(self)
            state_combo.addItems(STATES.values())
            state_combo.setCurrentIndex(state)
            state_combo.currentIndexChanged.connect(self.create_state_handler(identifier))
            grid.addWidget(state_combo, index, 2)
            remove_button = QPushButton("Remove", self)
            remove_button.clicked.connect(self.create_remover(identifier))
            grid.addWidget(remove_button, index, 3)
            index += 1
        self.setLayout(grid)

    def create_subject_handler(self, identifier):
        return lambda: self.update_subject(identifier)

    def create_description_handler(self, identifier):
        return lambda: self.update_description(identifier)

    def create_state_handler(self, identifier):
        return lambda: self.update_state(identifier)

    def create_remover(self, identifier):
        return lambda: self.remove_homework(identifier)

    def update_subject(self, identifier):
        subject_id = self.subject_id[self.sender().currentText()]
        query = "update homeworks set subject_id = ? " \
                "where homework_id = ?"
        self.connection.execute(query, (subject_id, identifier))
        self.connection.commit()

    def update_description(self, identifier):
        text = self.sender().text()
        print((text, identifier))
        query = "update homeworks set homework_description = ? where homework_id = ?"
        self.connection.execute(query, (text, identifier))
        self.connection.commit()

    def update_state(self, identifier):
        text = self.sender().currentText()
        query = "update homeworks set homework_state = ? " \
                "where homework_id = ?"
        ans = 0
        for key, value in STATES.items():
            if value == text:
                ans = key
        self.connection.execute(query, (ans, identifier))
        self.connection.commit()

    def remove_homework(self, identifier):
        grid = self.layout()
        self.sender().setEnabled(False)
        query = "delete from homeworks where homework_id = ?"
        self.connection.execute(query, (identifier,))
        self.connection.commit()

    def insert_homework(self):
        grid = self.layout()
        index = grid.rowCount() + 1
        description = "DESCRIPTION"
        subject_id = None
        for subject_id in self.subject_id.values():
            break
        state = 0
        query = "insert into homeworks(subject_id, homework_description, " \
                "homework_state) values (?, ?, ?) returning homework_id"
        identifier = self.connection.execute(query, (subject_id, description, state)).fetchone()[0]
        self.connection.commit()
        line_edit = QLineEdit(description, self)
        line_edit.editingFinished.connect(self.create_description_handler(identifier))
        grid.addWidget(line_edit, index, 0)
        subject_combo = QComboBox(self)
        subject_combo.addItems(self.subject_name.values())
        name = self.subject_name[subject_id]
        subject_combo.setCurrentIndex(list(self.subject_name.values()).index(name))
        subject_combo.currentIndexChanged.connect(self.create_subject_handler(identifier))
        grid.addWidget(subject_combo, index, 1)
        state_combo = QComboBox(self)
        state_combo.addItems(STATES.values())
        state_combo.setCurrentIndex(state)
        state_combo.currentIndexChanged.connect(self.create_state_handler(identifier))
        grid.addWidget(state_combo, index, 2)
        remove_button = QPushButton("Remove", self)
        remove_button.clicked.connect(self.create_remover(identifier))
        grid.addWidget(remove_button, index, 3)
