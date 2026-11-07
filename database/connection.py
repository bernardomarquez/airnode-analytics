

import sqlite3

from config.settings import DATABASE_FILE


# CONEXION CON LA BASE DE DATOS SQL

def get_connection():

    connection = sqlite3.connect(DATABASE_FILE)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
