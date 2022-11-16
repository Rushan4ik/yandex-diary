import sqlite3
from sqlite3 import Connection
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QLabel


class SubjectsWidget(QWidget):
    connection: Connection

    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection
        self.init_data()
        self.init_ui()

    def init_data(self):
        cursor = self.connection.execute("select subject_id, subject_name from subjects;")
        self.result = [(int(identifier), name) for identifier, name in cursor.fetchall()]

    def init_ui(self):
        box = QVBoxLayout()
        button = QPushButton("Create", self)
        button.clicked.connect(self.create_create_widget)
        box.addWidget(button)
        for identifier, name in self.result:
            button = QPushButton(name, self)
            button.clicked.connect(self.create_edit_handler(identifier))
            box.addWidget(button)
        self.setLayout(box)

    def create_edit_handler(self, identifier):
        return lambda: self.create_edit_widget(identifier)

    def create_edit_widget(self, identifier):
        self.button = self.sender()
        self.widget = SubjectEditWidget(self, identifier, self.connection)
        self.widget.show()

    def create_create_widget(self):
        self.widget = SubjectCreateWidget(self, self.connection)
        self.widget.show()

    def update_state(self, new_name):
        if new_name == '\0{Deleted}\0':
            self.layout().removeWidget(self.button)
            del self.button
        else:
            self.button.setText(new_name)

    def add_button(self, identifier, name):
        button = QPushButton(name, self)
        button.clicked.connect(self.create_edit_handler(identifier))
        self.layout().addWidget(button)


class SubjectEditWidget(QWidget):
    def __init__(self, parent: SubjectsWidget, identifier, connection: sqlite3.Connection):
        super().__init__()
        self.parent_widget = parent
        self.connection = connection
        query = "select subject_id, subject_name from subjects where subject_id = ?"
        self.subject_id, self.subject_name = self.connection.execute(query, (identifier,)).fetchone()
        self.init_ui()

    def init_ui(self):
        box = QVBoxLayout()
        box.addWidget(QLabel("Name:", self))
        self.line_edit = QLineEdit(self)
        self.line_edit.setText(self.subject_name)
        box.addWidget(self.line_edit)
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save)
        box.addWidget(save_button)
        remove_button = QPushButton("Remove", self)
        remove_button.clicked.connect(self.remove)
        box.addWidget(remove_button)
        self.setLayout(box)

    def save(self):
        query = 'update subjects set subject_name = ? where subject_id = ?'
        cursor = self.connection.execute(query, (self.line_edit.text(), self.subject_id))
        self.parent_widget.update_state(self.line_edit.text())
        self.connection.commit()

    def remove(self):
        query = 'delete from subjects where subject_id = ?'
        cursor = self.connection.execute(query, (self.subject_id,))
        self.parent_widget.update_state("\0{Deleted}\0")
        self.close()
        self.connection.commit()


class SubjectCreateWidget(QWidget):
    def __init__(self, parent: SubjectsWidget, connection: Connection):
        super().__init__()
        self.parent_widget = parent
        self.connection = connection
        self.init_ui()

    def init_ui(self):
        box = QVBoxLayout()
        box.addWidget(QLabel("Name:", self))
        self.line_edit = QLineEdit(self)
        box.addWidget(self.line_edit)
        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self.create_subject)
        box.addWidget(create_button)
        self.setLayout(box)

    def create_subject(self):
        query = 'insert into subjects(subject_name) values (?) returning subject_id'
        identifier = int(self.connection.execute(query, (self.line_edit.text(),)).fetchone()[0])
        self.connection.commit()
        self.parent_widget.add_button(identifier, self.line_edit.text())
