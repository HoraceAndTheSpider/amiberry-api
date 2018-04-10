import sqlite3
from binascii import hexlify, unhexlify
import zlib
import json
from pprint import pprint
import re

from constants import SOURCE_DB


def binary_uuid_to_str(data):
    s = hexlify(data).decode("ASCII")
    return "{}-{}-{}-{}-{}".format(
        s[0:8], s[8:12], s[12:16], s[16:20], s[20:32])


def get_game_values(cursor, game_id=None, *, game_uuid=None, recursive=True):
    if game_uuid is not None:
        cursor.execute(
            "SELECT uuid, data FROM game WHERE uuid = ?",
            (sqlite3.Binary(unhexlify(game_uuid.replace("-", ""))),))
        row = cursor.fetchone()
        if not row:
            raise LookupError("Cannot find game uuid {}".format(game_uuid))

        data = zlib.decompress(row[1])
        data = data.decode("UTF-8")

        doc = json.loads(data)

        doc["__publish_hack__"] = doc.get("publish", "")

        next_parent_uuid = doc.get("parent_uuid", "")
        while next_parent_uuid and recursive:
            # Treat game_uuid special, it will be the first parent_uuid
            # in the chain.
            doc["game_uuid"] = next_parent_uuid
            cursor.execute(
                "SELECT data FROM game WHERE uuid = ?",
                (sqlite3.Binary(
                    unhexlify(next_parent_uuid.replace("-", ""))),))
            row = cursor.fetchone()
            if not row:
                raise ValueError(
                    "Could not find parent {0} of game {1}".format(
                        next_parent_uuid, game_uuid))
            data = zlib.decompress(row[0])
            data = data.decode("UTF-8")
            next_doc = json.loads(data)
            next_parent_uuid = next_doc.get("parent_uuid", "")
            # Let child doc overwrite and append values to parent doc.
            next_doc.update(doc)
            doc = next_doc
        return doc


connection = sqlite3.connect(SOURCE_DB)
c = connection.cursor()
other_cursor = connection.cursor()

for row in c.execute('SELECT * FROM game'):
    uuid = binary_uuid_to_str(data=row[1])
    try:
        data = zlib.decompress(row[2])
    except TypeError:
        continue

    data = data.decode("UTF-8")
    doc = json.loads(data)

    try:
        if re.match("^.*whdload.*$", doc["variant_name"].lower()):

            doc = get_game_values(cursor=other_cursor, game_uuid=uuid)
            try:
                game_name = doc['game_name']
            except KeyError:
                continue

            print("UUID: {}".format(uuid))
            pprint(doc)
            print("\n")
    except KeyError:
        continue
