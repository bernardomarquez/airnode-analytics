
import sqlite3

from config.settings import DATABASE_FILE


def get_connection():
    """Abre una conexión con la base de datos SQLite."""

    connection = sqlite3.connect(DATABASE_FILE)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
