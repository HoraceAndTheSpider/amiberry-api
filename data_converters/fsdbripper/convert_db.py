import os
import sqlite3
from binascii import hexlify, unhexlify
import zlib
import json

from constants import SOURCE_DB, DESTINATION_DB


def binary_uuid_to_str(data):
    s = hexlify(data).decode("ASCII")
    return "{}-{}-{}-{}-{}".format(
        s[0:8], s[8:12], s[12:16], s[16:20], s[20:32])


source_connection = sqlite3.connect(SOURCE_DB)
source_cursor = source_connection.cursor()

destination_connection = sqlite3.connect(DESTINATION_DB)
destination_cursor = destination_connection.cursor()
destination_cursor.execute('BEGIN TRANSACTION')

for i, row in enumerate(source_cursor.execute('SELECT * FROM game')):
    uuid = binary_uuid_to_str(data=row[1])
    if len(uuid) != 36:
        print("Bad Row ({}): {}".format(i, row))

    try:
        data = zlib.decompress(row[2])
    except TypeError:
        continue

    data = data.decode("UTF-8")
    doc = json.loads(data)

    destination_cursor.execute(
        "INSERT INTO game VALUES (?,?)",
        (uuid, data,)
    )

destination_cursor.execute('COMMIT')

destination_connection.commit()
