import datetime
import re

import pynamodb.exceptions
from pynamodb.attributes import (JSONAttribute, NumberAttribute,
                                 UnicodeAttribute, UnicodeSetAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.models import Model

from models.constants import REGION_NAME, VARIANTS_TABLE_NAME
from models.game import Game


class Variant(Model):
    class Meta:
        table_name = VARIANTS_TABLE_NAME
        region = REGION_NAME
    sha1 = UnicodeAttribute(hash_key=True)
    dh0_sha1 = UnicodeAttribute(null=True)
    game_name = UnicodeAttribute(null=True)
    openretro_uuid = UnicodeAttribute(null=True)
    parent_uuid = UnicodeAttribute(null=True)
    filename = UnicodeAttribute()
    modified_time = UTCDateTimeAttribute(default=datetime.datetime.utcnow())
    slave_count = NumberAttribute(default=1)
    slave_default = UnicodeAttribute(null=True)
    hardware = JSONAttribute(null=True)
    custom_controls = JSONAttribute(null=True)
    variant_tags = UnicodeSetAttribute(null=True)

    @property
    def parent(self):
        if not self.parent_uuid:
            return None

        try:
            parent_game = Game.get(hash_key=self.parent_uuid)
        except pynamodb.exceptions.DoesNotExist:
            return None

        return parent_game

    @property
    def variant_display_tags(self):
        tags = self.variant_tags
        if not tags:
            return None

        tags = ' '.join([t.lower() for t in tags])
        display_tags = []

        source_match = re.search(r'whdload', tags)
        if source_match:
            display_tags.append('WHDLoad')

        platform_match = re.search(r'\b(aga|cd32)\b', tags)
        if platform_match:
            display_tags.append(platform_match.group().upper())

        disk_match = re.search(r'\b(\d)(disk|disc)\b', tags)
        if disk_match:
            display_tags.append('{}Disk'.format(platform_match.group()))

        return ', '.join(display_tags) if display_tags else None

    @property
    def variant_name(self):
        game_name = self.game_name if self.game_name else self.filename.split('_')[
            0]

        tags = self.variant_display_tags

        if not tags:
            return game_name

        return '{} ({})'.format(game_name, tags)

    def to_dict(self):
        return {
            'sha1': self.sha1,
            'game_name': self.game_name,
            'variant_name': self.variant_name,
            'dh0_sha1': self.dh0_sha1,
            'openretro_uuid': self.openretro_uuid,
            'parent_uuid': self.parent_uuid,
            'filename': self.filename,
            'modified_time': self.modified_time.isoformat(),
            'slave_count': self.slave_count,
            'slave_default': self.slave_default,
            'hardware': self.hardware,
            'custom_controls': self.custom_controls,
            'tags': list(self.variant_tags) if self.variant_tags else None,
        }

    def to_detailed_dict(self):
        return {
            **self.to_dict(),
            'parent': self.parent.to_dict() if self.parent else None
        }
