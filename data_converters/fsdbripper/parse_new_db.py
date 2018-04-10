import sqlite3
import json

from constants import DESTINATION_DB

destination_connection = sqlite3.connect(DESTINATION_DB)
destination_cursor = destination_connection.cursor()

fields_set = set()
row_count = 0
for row in destination_cursor.execute('SELECT * FROM game'):
    uuid = row[0]
    doc = json.loads(row[1])

    for key in doc.keys():
        fields_set.add(key)
    row_count += 1

fields = ", ".join(fields_set)
fields = "uuid, {}".format(fields)
insert_replace_params = ('?,' * len(fields.split(','))).rstrip(',')

try:
    destination_cursor.execute(
        'CREATE TABLE new_game({})'.format(fields)
    )
except:
    pass

print('Finished Getting Column Names')

update_cursor = destination_connection.cursor()
update_cursor.execute('BEGIN TRANSACTION')

for i, row in enumerate(destination_cursor.execute('SELECT * FROM game')):
    uuid = row[0]
    doc = json.loads(row[1])
    values = []

    for col in fields_set:
        try:
            string_value = doc[col].replace("'", "''")
        except KeyError:
            string_value = ''
        values.append(string_value)

    values = [uuid] + values
    values_tuple = tuple(values)

    update_cursor.execute("INSERT OR IGNORE INTO new_game ({}) VALUES ({})".format(
        fields, insert_replace_params), (values_tuple))

    if i % 100 == 0:
        print('Processed {}/{} records'.format(i, row_count))

update_cursor.execute('COMMIT')

print('Finished writing data to new DB')
