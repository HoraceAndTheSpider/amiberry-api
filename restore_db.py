from models.game import Game
from models.variant import Variant

GAMES_BACKUP = 'game_backup_1524743933.json'
VARIANT_BACKUP = 'variant_backup_1524743933.json'

print('Restoring backups...')
Game.load(GAMES_BACKUP)
Variant.load(VARIANT_BACKUP)
print('Done...')