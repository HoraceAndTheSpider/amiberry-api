import os
import xml

from pprint import pprint

from models.variant import Variant

ROOT_DIR = os.path.dirname(__file__)
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


parse_xml(XML_FILE_PATH)
