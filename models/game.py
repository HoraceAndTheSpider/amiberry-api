import uuid

from pynamodb.attributes import (JSONAttribute, NumberAttribute,
                                 UnicodeAttribute, UnicodeSetAttribute,
                                 UTCDateTimeAttribute, BooleanAttribute)
from pynamodb.models import Model

from models.constants import GAMES_TABLE_NAME, REGION_NAME


class Game(Model):
    class Meta:
        table_name = GAMES_TABLE_NAME
        region = REGION_NAME

    uuid = UnicodeAttribute(hash_key=True, default=str(uuid.uuid4()))
    game_name = UnicodeAttribute()
    search_name = UnicodeAttribute()
    openretro_url = UnicodeAttribute(null=True)
    whdload_url = UnicodeAttribute(null=True)
    hardware = JSONAttribute(null=True)
    custom_controls = JSONAttribute(null=True)
    variants = UnicodeSetAttribute(null=True)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'game_name': self.game_name,
            'search_name': self.search_name,
            'openretro_url': self.openretro_url,
            'whdload_url': self.whdload_url,
            'hardware': self.hardware,
            'custom_controls': self.custom_controls,
            'variants': list(self.variants) if self.variants else None,
        }
