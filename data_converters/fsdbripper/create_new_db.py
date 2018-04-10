import sqlite3

from constants import DESTINATION_DB

destination_connection = sqlite3.connect(DESTINATION_DB)
destination_cursor = destination_connection.cursor()

destination_cursor.execute('CREATE TABLE game(uuid, payload)')
