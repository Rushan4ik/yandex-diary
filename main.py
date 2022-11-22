import sqlite3
import sys
from PyQt5.QtWidgets import QApplication
from widgets import MainWidget

queries = [
    "CREATE TABLE IF NOT EXISTS subjects(subject_id INTEGER PRIMARY KEY AUTOINCREMENT, subject_name TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS goals( goal_id INTEGER PRIMARY KEY AUTOINCREMENT, goal_description TEXT NOT NULL "
    "DEFAULT ('Description'), goal_state INTEGER NOT NULL DEFAULT (0)); ",
    "CREATE TABLE IF NOT EXISTS homeworks(homework_id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id INTEGER "
    "REFERENCES subjects (subject_id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL, homework_description TEXT NOT "
    "NULL, homework_state INTEGER NOT NULL DEFAULT (0)); ",
    "CREATE TABLE IF NOT EXISTS lessons(lesson_id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id INTEGER REFERENCES "
    "subjects (subject_id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL, lesson_day INTEGER NOT NULL, lesson_order "
    "INTEGER NOT NULL); ",
    "CREATE TABLE IF NOT EXISTS replacements(replacement_id INTEGER PRIMARY KEY AUTOINCREMENT, lesson_id INTEGER "
    "REFERENCES lessons (lesson_id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL, subject_id INTEGER REFERENCES "
    "subjects (subject_id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL) "
]


if __name__ == '__main__':
    connection = sqlite3.connect("diary_database.sqlite")
    for query in queries:
        connection.execute(query)
    connection.commit()
    app = QApplication(sys.argv)
    ex = MainWidget(connection)
    ex.show()
    sys.exit(app.exec())
