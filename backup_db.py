from datetime import datetime

from models.game import Game
from models.variant import Variant

now = str(int(datetime.utcnow().timestamp()))

Game.dump('game_backup_{}.json'.format(now))
Variant.dump('variant_backup_{}.json'.format(now))
