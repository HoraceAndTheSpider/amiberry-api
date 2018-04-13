import os
import xml
import sqlite3
import sys
from pprint import pprint

ROOT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(ROOT_DIR, ".."))

from models.variant import Variant

XML_FILE_PATH = os.path.join(ROOT_DIR, 'whdload_db.xml')


def parse_xml(xml_file_path):
    xml_data = xml.etree.ElementTree.parse(xml_file_path).getroot()

    for element in xml_data:
        sha1 = element.attrib['sha1']
        slave_count = 1
        hardware = {}

        for child_element in element.getchildren():
            if child_element.tag == 'slave_count':
                slave_count = child_element.text
            if child_element.tag == 'hardware':
                hardware_raw = [x.strip()
                                for x in child_element.text.strip().split('\n')]
                for hardware_item in hardware_raw:
                    key, value = hardware_item.split('=')
                    hardware[key] = value
        lha_meta = {
            'sha1': sha1,
            'slave_count': slave_count,
            'hardware': hardware
        }
        pprint(lha_meta)


A1200 = {'CHIPSET': 'AGA', 'FASTRAM': '8'}
A4000 = {**A1200, 'CPU': '68040'}

MODEL_MAPPING = {
    'A!1200': A1200,
    'A1200': A1200,
    'A1200/020': A1200,
    'A4000': A4000
}

ROOT_DIR = os.path.dirname(__file__)
OPENRETRO_DB_PATH = os.path.join(ROOT_DIR, '..', 'data_converters', 'fsdbripper', 'Amiga_Ripped.sqlite')
OPENRETRO_TABLE_NAME = 'new_game'

def get_hardware():
    sql_connection = sqlite3.connect(OPENRETRO_DB_PATH)
    sql_cursor = sql_connection.cursor()
    for variant in Variant.scan():
        sql_cursor.execute(
        'select x_name, amiga_model, model, chipset, chip_memory, fast_memory, slow_memory from new_game where dh0_sha1=?', (variant.dh0_sha1,))

        sql_result = sql_cursor.fetchone()
        if sql_result:
            x_name = sql_result[0]
            model = sql_result[1] or sql_result[2]
            chipset = sql_result[3]
            chipmem = sql_result[4]
            fastmem = sql_result[5]

            hardware = MODEL_MAPPING.get(model, {})
            if not hardware:
                if chipset == 'AGA':
                    hardware = A1200
                else:
                    hardware = {'CHIPSET': 'ECS', 'FASTRAM': '4'}
            
            if chipmem:
                chipmem = int(chipmem.replace('+', ''))
                if chipmem == 2:
                    chipmem = 2048
                hardware = {**hardware, 'CHIPMEM': chipmem // 1024}
            
            if fastmem and int(fastmem) > 8192:
                hardware['Z3RAM'] = int(fastmem) // 1024
                hardware.pop('FASTRAM', None)

            

            

get_hardware()
