from playlist_db import TG_playslists
from log_in import sp
from playlist_db import TG_playslists
from json import dumps

#This is what playlist_search.py returns
hardcode_uri = "spotify:playlist:1PKLQpRkNUDr4pTQSUtvE7"

# playlist info will be stored in db as a json file for each playlist
class Create_tg_pl():

    def __init__(self,playlist_uri):
        self.playlist_uri = playlist_uri

    def get_playlist_json(self):
        pl_json = sp.playlist_items(self.playlist_uri)
        return pl_json




playlist_create = Create_tg_pl(hardcode_uri)

playlist_json = playlist_create.get_playlist_json()
print(dumps(playlist_json,indent=4))

print(playlist_create.parse_relevant_json(playlist_json))




