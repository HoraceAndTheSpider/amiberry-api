import os
import json
import posixpath
import hashlib
import urllib
import lhafile

ROOT_DIR = os.path.dirname(__file__)
JSON_OUTPUT_NAME = 'retroplay_index.json'
JSON_OUTPUT_PATH = os.path.join(ROOT_DIR, JSON_OUTPUT_NAME)
HDD_PREFIX = 'DH0'
VARIANT_PREFIX = ['WHDLoad']
RETROPLAY_ROOT = 'E:\\Emulation\\retroplay\\Games'


def get_file_metadata(archive, file):
    metadata = {}

    if file.comment:
        metadata['comment'] = file.comment

    file_name = file.filename.replace(os.path.sep, posixpath.sep)
    metadata['name'] = posixpath.join(HDD_PREFIX, file_name)

    if not metadata['name'].endswith(posixpath.sep):
        data = archive.read(file.filename)
        metadata['sha1'] = get_sha1(data)
        metadata['size'] = len(data)

    return metadata


def read_archive(file_path):
    files_metadata = []
    archive = lhafile.lhafile.LhaFile(file_path)
    files_to_scan = []
    for archived_file in archive.infolist():
        # Only read the folders in the archive
        if not os.path.sep in archived_file.filename:
            continue

        # Exclude '*.info' files
        if archived_file.filename.lower().endswith('.info'):
            continue

        files_to_scan.append(archived_file)

    for archived_file in files_to_scan:
        file_metadata = get_file_metadata(archive, archived_file)
        files_metadata.append(file_metadata)

    files_metadata = sorted(files_metadata, key=lambda x: x['name'])

    return files_metadata


def get_dh0_sha1(files_metadata):
    json_dumps = json.dumps(files_metadata)
    return get_sha1(json_dumps.encode())


def get_sha1(data):
    return hashlib.sha1(data).hexdigest()


def parse_file(file_path):
    if file_path.lower().endswith('.lha'):
        with open(file_path, 'rb') as archive_file:
            lha_sha1 = get_sha1(archive_file.read())

        files_metadata = read_archive(file_path)
        dh0_sha1 = get_dh0_sha1(files_metadata)

        filename = os.path.basename(file_path)
        _, *variant_parts = os.path.splitext(filename)[0].split('_')
        archive_metadata = {
            'filename': filename,
            'variant_name': ', '.join(VARIANT_PREFIX + variant_parts),
            'sha1': lha_sha1,
            'files': files_metadata,
            'dh0_sha1': dh0_sha1,
        }
        return archive_metadata


def traverse_directory(directory):
    print('Processing Directory: {}'.format(directory))
    lha_files_metadata = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            lha_files_metadata = lha_files_metadata + \
                traverse_directory(item_path)

        if os.path.isfile(item_path):
            parse_result = parse_file(item_path)
            if parse_result:
                lha_files_metadata.append(parse_result)

    return lha_files_metadata


lha_files_metadata = traverse_directory(RETROPLAY_ROOT)
print('Saving data to {}'.format(JSON_OUTPUT_PATH))
with open(JSON_OUTPUT_PATH, 'w') as json_file:
    json.dump(lha_files_metadata, json_file, indent=2)
print('Complete!')