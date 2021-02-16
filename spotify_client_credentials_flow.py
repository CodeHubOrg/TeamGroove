""" Client Credentials Flow

The Client Credentials flow is used in server-to-server authentication. Only endpoints that do not
access user information can be accessed. The advantage here in comparison with requests to the Web
API made without an access token, is that a higher rate limit is applied.
https://spotipy.readthedocs.io/en/2.16.1/#client-credentials-flow"""

from dotenv import load_dotenv

load_dotenv()

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = sp.user_playlists("spotify")
while playlists:
    for i, playlist in enumerate(playlists["items"]):
        print(
            "%4d %s %s"
            % (i + 1 + playlists["offset"], playlist["uri"], playlist["name"])
        )
    if playlists["next"]:
        playlists = sp.next(playlists)
    else:
        playlists = None
