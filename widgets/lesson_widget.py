import sqlite3

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QComboBox, QSpinBox


class LessonsWidget(QWidget):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection
        query = "SELECT lesson_id, subject_name, lesson_day, lesson_order " \
                "FROM lessons LEFT JOIN subjects " \
                "ON lessons.subject_id = subjects.subject_id;"
        cursor = self.connection.execute(query)
        self.result = [(int(identifier), subject_name, int(day), int(order))
                       for identifier, subject_name, day, order in cursor.fetchall()]
        cursor.execute("select subject_name from subjects")
        self.subjects = [subject_name[0] for subject_name in cursor.fetchall()]
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self.create_create_widget)
        grid.addWidget(create_button, 0, 0)

        for identifier, name, day, order in self.result:
            button = QPushButton(name, self)
            button.clicked.connect(self.create_edit_handler(identifier))
            grid.addWidget(button, order, day)
        for i in range(grid.columnCount() - 1):
            grid.addWidget(QLabel(str(i + 1), self), 0, i + 1)
        for i in range(grid.rowCount() - 1):
            grid.addWidget(QLabel(str(i + 1), self), i + 1, 0)
        self.setLayout(grid)

    def create_edit_handler(self, identifier):
        return lambda: self.create_edit_widget(identifier)

    def create_edit_widget(self, identifier):
        self.button = self.sender()
        self.widget = LessonEditWidget(self, identifier, self.connection)
        self.widget.show()

    def create_create_widget(self):
        self.widget = LessonCreateWidget(self, self.connection)
        self.widget.show()

    def move_button(self, day, order, subject_name):
        grid = self.layout()
        grid.removeWidget(self.button)
        self.button.setText(subject_name)
        new_x, new_y = order, day
        for i in range(grid.rowCount(), new_x + 1):
            grid.addWidget(QLabel(str(i), self), i, 0)
        for i in range(grid.columnCount(), new_y + 1):
            grid.addWidget(QLabel(str(i), self), 0, i)
        grid.addWidget(self.button, new_x, new_y)

    def create_lesson(self, day, order, subject):
        button = QPushButton(subject, self)
        self.layout().addWidget(button, order, day)

    def remove_button(self):
        self.layout().removeWidget(self.button)


class LessonEditWidget(QWidget):
    def __init__(self, parent: LessonsWidget, identifier, connection: sqlite3.Connection):
        super().__init__()
        self.parent_widget = parent
        self.identifier = identifier
        self.connection = connection
        query = 'select subject_id, subject_name from subjects order by subject_id'
        cursor = connection.execute(query)
        self.subjects = {subject_id: subject_name for subject_id, subject_name in cursor.fetchall()}
        query = "SELECT lessons.subject_id, subject_name, lesson_day, lesson_order " \
                "FROM lessons LEFT JOIN subjects ON lessons.subject_id = subjects.subject_id " \
                "WHERE lesson_id = ?"
        self.subject_id, self.subject_name, self.day, self.order = cursor.execute(query, (identifier,)).fetchone()
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()

        grid.addWidget(QLabel("Day:", self), 0, 0)
        self.day_spin = QSpinBox(self)
        self.day_spin.setMinimum(1)
        self.day_spin.setValue(self.day)
        self.day_spin.setMaximum(7)
        grid.addWidget(self.day_spin, 0, 1)

        grid.addWidget(QLabel("Order:", self))
        self.order_spin = QSpinBox(self)
        self.order_spin.setMaximum(20)
        self.order_spin.setValue(self.order)
        self.order_spin.setMinimum(1)
        grid.addWidget(self.order_spin, 1, 1)

        grid.addWidget(QLabel("Subject:", self), 2, 0)
        self.subjects_combo = QComboBox(self)
        self.subjects_combo.addItems(self.subjects.values())
        self.subjects_combo.setCurrentIndex(list(self.subjects.values()).index(self.subject_name))
        grid.addWidget(self.subjects_combo, 2, 1)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_state)
        grid.addWidget(save_button, 3, 0)
        remove_button = QPushButton("Remove", self)
        remove_button.clicked.connect(self.remove_state)
        grid.addWidget(remove_button, 3, 1)

        self.setLayout(grid)

    def save_state(self):
        query = 'update lessons ' \
                'set subject_id = ?, lesson_day = ?, lesson_order = ? ' \
                'where lesson_id = ?'
        ans = 0
        for key, value in self.subjects.items():
            if value == self.subjects_combo.currentText():
                ans = key
                break
        self.connection.execute(query, (ans, self.day_spin.value(), self.order_spin.value(), self.identifier))
        self.connection.commit()
        self.parent_widget.move_button(self.day_spin.value(), self.order_spin.value(),
                                       self.subjects_combo.currentText())

    def remove_state(self):
        query = 'delete from lessons where lesson_id = ?'
        self.connection.execute(query, (self.identifier,))
        self.connection.commit()
        self.parent_widget.remove_button()
        self.close()


class LessonCreateWidget(QWidget):
    def __init__(self, parent: LessonsWidget, connection: sqlite3.Connection):
        super().__init__()
        self.parent_widget = parent
        self.connection = connection
        cursor = self.connection.execute("select subject_id, subject_name from subjects")
        self.subject_names = {}
        self.subject_id = {}
        for subject in cursor:
            self.subject_id[subject[1]] = int(subject[0])
            self.subject_names[int(subject[0])] = subject[1]
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()

        grid.addWidget(QLabel("Subject:", self), 0, 0)
        self.subject_combo = QComboBox(self)
        self.subject_combo.addItems(self.subject_names.values())
        grid.addWidget(self.subject_combo, 0, 1)

        grid.addWidget(QLabel("Day:", self), 1, 0)
        self.day_spin = QSpinBox(self)
        self.day_spin.setMinimum(1)
        self.day_spin.setValue(1)
        self.day_spin.setMaximum(7)
        grid.addWidget(self.day_spin, 1, 1)

        grid.addWidget(QLabel("Order:", self), 2, 0)
        self.order_spin = QSpinBox(self)
        self.order_spin.setMaximum(20)
        self.order_spin.setValue(1)
        self.order_spin.setMinimum(1)
        grid.addWidget(self.order_spin, 2, 1)

        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self.create_lesson)
        grid.addWidget(create_button, 3, 1, 1, 2)

        self.setLayout(grid)

    def create_lesson(self):
        query = "insert into lessons(subject_id, lesson_day, lesson_order) values(?, ?, ?)"
        subject_id = self.subject_id[self.subject_combo.currentText()]
        self.connection.execute(query, (subject_id, self.day_spin.value(), self.order_spin.value()))
        self.connection.commit()
        self.parent_widget.create_lesson(self.day_spin.value(), self.order_spin.value(),
                                         self.subject_combo.currentText())
        self.close()
