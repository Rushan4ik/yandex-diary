import sqlite3
import sys
from PyQt5.QtWidgets import QApplication
from widgets import MainWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWidget(sqlite3.connect("diary_database.sqlite"))
    ex.show()
    sys.exit(app.exec())
