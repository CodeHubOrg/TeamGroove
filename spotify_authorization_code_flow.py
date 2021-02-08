""" Authorization Code Flow

This flow is suitable for long-running applications in which the user grants permission only once.
It provides an access token that can be refreshed. Since the token exchange involves sending your
secret key, perform this on a secure location, like a backend service, and not from a client such
as a browser or from a mobile app.
https://spotipy.readthedocs.io/en/2.16.1/#authorization-code-flow"""

from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results["items"]):
    track = item["track"]
    print(idx, track["artists"][0]["name"], " – ", track["name"])
