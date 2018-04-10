import os
import sqlite3
import json

from constants import ROOT_DIR, DESTINATION_DB

RETROPLAY_INDEX = os.path.join(ROOT_DIR, 'retroplay_index.json')
DB_CONNECTION = sqlite3.connect(DESTINATION_DB)
DB_CURSOR = DB_CONNECTION.cursor()


def load_retroplay_index(path):
    with open(RETROPLAY_INDEX, 'r') as f:
        data = json.load(f)

    return data


def main():
    with open('report.txt', 'w') as f:
        missed = 0
        retroplay_index_data = load_retroplay_index(RETROPLAY_INDEX)
        for item in sorted(retroplay_index_data, key=lambda x: x['filename']):
            if not item:
                continue
            dh0_sha1 = item['dh0_sha1']

            DB_CURSOR.execute(
                'select uuid from new_game where dh0_sha1=?', (dh0_sha1,))

            result = DB_CURSOR.fetchone()

            if not result:
                missed += 1
                reportline = '{}: {}'.format(item['filename'], dh0_sha1)
                print(reportline)
                f.write(reportline + '\n')

    print('Missed: {}'.format(missed))


if __name__ == '__main__':
    main()
