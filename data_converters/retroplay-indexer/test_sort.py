import json

test_string = """{"files":[{
    "name": "DH0/CaliforniaGames2/data/c5.lbm",
    "sha1": "3d0d1af8f8a32e09d32d295fefcacf911aa3a809",
    "size": 2498
  }, {
    "name": "DH0/CaliforniaGames2/data/c/more",
    "sha1": "bd5649e17fa1e56be19aa6cc5294c8824c23d843",
    "size": 191
  }, {
    "name": "DH0/CaliforniaGames2/data/c/run",
    "sha1": "17595bda7a1aa8f89304b9711252494ed677c0a5",
    "size": 1636
  }]}"""

data = json.loads(test_string)
files = data['files']
from pprint import pprint
pprint(files)
pprint(sorted(files, key=lambda x: x['name']))
