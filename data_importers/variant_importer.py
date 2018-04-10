"""Requires a retroplay-index JSON and Unpacked OpenRetro DB"""

import json
import os
import sqlite3

from time import sleep

import pynamodb.exceptions

from models.variant import Variant
from models.game import Game

ROOT_DIR = os.path.dirname(__file__)
OPENRETRO_DB_PATH = os.path.join(ROOT_DIR, 'Amiga_Ripped.sqlite')
OPENRETRO_TABLE_NAME = 'new_game'
RETROPLAY_INDEX_JSON_PATH = os.path.join(ROOT_DIR, 'retroplay_index.json')


with open(RETROPLAY_INDEX_JSON_PATH, 'r') as f:
    retroplay_index = json.load(f)

sql_connection = sqlite3.connect(OPENRETRO_DB_PATH)
sql_cursor = sql_connection.cursor()

variants = []
game_updates = []


for item in sorted(retroplay_index, key=lambda x: x['filename']):
    dh0_sha1 = item['dh0_sha1']

    sql_cursor.execute(
        'select uuid, parent_uuid from new_game where dh0_sha1=?', (dh0_sha1,))

    sql_result = sql_cursor.fetchone()

    variant = Variant()

    variant.sha1 = item['sha1']
    variant.dh0_sha1 = item['dh0_sha1']
    variant.filename = item['filename']
    variant.variant_tags = item['variant_name'].split(', ')

    if sql_result:
        variant.openretro_uuid = sql_result[0]
        variant.parent_uuid = sql_result[1]
        if variant.parent_uuid:
            sql_cursor.execute(
                'select game_name from new_game where uuid=?', (variant.parent_uuid,))
            parent_sql_result = sql_cursor.fetchone()
            if parent_sql_result:
                variant.game_name = parent_sql_result[0]

    variants.append(variant)

    # update the parent
    if variant.parent:
        parent = variant.parent
        if not parent.variants or variant.sha1 not in parent.variants:
            actions = [
                Game.variants.add({variant.sha1})
            ]
            try:
                parent.update(actions=actions)
            except pynamodb.exceptions.UpdateError as e:
                print('Update Error: {}'.format(e))
                sleep(2)
                print('Retrying...')
                parent.update(actions=actions)
                print('Success!')


print('Update Variants Table')
with Variant.batch_write() as batch:
    for i, entry in enumerate(variants):
        print('Saving Variant Entry {}/{}'.format(i + 1, len(variants)))
        try:
            batch.save(entry)
        except pynamodb.exceptions.PutError:
            print('Throttled, sleeping for 60secs')
            sleep(60)
            batch.save(entry)
