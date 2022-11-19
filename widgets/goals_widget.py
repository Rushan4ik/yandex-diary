import sqlite3

from PyQt5.QtWidgets import QWidget, QGridLayout, QLineEdit, QComboBox, QPushButton

STATES = {
    0: 'CANCELED',
    1: 'PLANED',
    2: 'IN_PROCESS',
    3: 'IS_DONE'
}


class GoalsWidget(QWidget):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection
        self.init_data()
        self.init_ui()

    def init_data(self):
        query = "select goal_id, goal_description, goal_state from goals"
        self.result = [(int(identifier), description, int(state))
                       for identifier, description, state in self.connection.execute(query).fetchall()]

    def init_ui(self):
        grid = QGridLayout()
        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self.add_goal)
        grid.addWidget(create_button, 0, 0, 1, 2)
        index = 1
        for identifier, description, state in self.result:
            line_edit = QLineEdit(self)
            line_edit.setText(description)
            line_edit.editingFinished.connect(self.create_description_handler(identifier))
            grid.addWidget(line_edit, index, 0)
            combo_box = QComboBox(self)
            combo_box.addItems(STATES.values())
            combo_box.setCurrentIndex(list(STATES.values()).index(STATES[state]))
            combo_box.currentIndexChanged.connect(self.create_state_handler(identifier))
            grid.addWidget(combo_box, index, 1)
            index += 1
        grid.columnCount()
        self.setLayout(grid)

    def create_description_handler(self, identifier):
        return lambda: self.update_description(identifier)

    def create_state_handler(self, identifier):
        return lambda: self.update_state(identifier)

    def update_description(self, identifier):
        description = self.sender().text()
        query = "update goals set goal_description = ? where goal_id = ?"
        self.connection.execute(query, (description, identifier))
        self.connection.commit()

    def update_state(self, identifier):
        text = self.sender().currentText()
        ans = None
        for key, value in STATES.items():
            if value == text:
                ans = key
        query = "update goals set goal_state = ? where goal_id = ?"
        self.connection.execute(query, (ans, identifier))
        self.connection.commit()

    def add_goal(self):
        grid = self.layout()
        row = grid.rowCount()
        description, state = 'DESCRIPTION', 0
        query = "insert into goals(goal_description, goal_state) values (?, ?) returning goal_id"
        identifier = int(self.connection.execute(query, (description, state)).fetchone()[0])
        line_edit = QLineEdit(self)
        line_edit.setText(description)
        line_edit.editingFinished.connect(self.create_description_handler(identifier))
        grid.addWidget(line_edit, row, 0)
        combo_box = QComboBox(self)
        combo_box.addItems(STATES.values())
        combo_box.currentIndexChanged.connect(self.create_state_handler(identifier))
        grid.addWidget(combo_box, row, 1)
        self.connection.commit()

