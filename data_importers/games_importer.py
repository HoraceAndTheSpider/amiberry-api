"""Requires CSV Export from OpenRetro DB with uuid, game_name cols"""

import csv
import os
from time import sleep

import pynamodb.exceptions

from models.game import Game

ROOT_DIR = os.path.dirname(__file__)
CSV_FILE = os.path.join(ROOT_DIR, 'games.csv')


OPENRETRO_URL = 'https://openretro.org'
OPENRETRO_GAME_BASE_URL = '{}/game'.format(OPENRETRO_URL)

games = []


with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        game = Game()
        game.uuid = row['uuid']
        game.game_name = row['game_name']
        game.search_name = row['game_name'].lower()
        game.openretro_url = '{}/{}'.format(
            OPENRETRO_GAME_BASE_URL, row['uuid'])
        games.append(game)

print('Update Games Table')
with Game.batch_write() as batch:
    for i, entry in enumerate(games):
        if entry.game_name is None:
            continue
        print('Saving Game Entry {}/{}'.format(i + 1, len(games)))
        try:
            batch.save(entry)
        except pynamodb.exceptions.PutError:
            print('Throttled, sleeping for 60secs')
            sleep(60)
            batch.save(entry)
