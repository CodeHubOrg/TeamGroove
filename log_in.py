""" Using authorization code flow so that we can access user information.
To keep secrets out of the code, they should be set as environment variables.
Spotipy uses three environment variables for authentication with authorization code flow:
* SPOTIPY_CLIENT_ID
* SPOTIPY_CLIENT_SECRET
* SPOTIPY_REDIRECT_URI
"""
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def log_in():
    # The permissions we want to request from Spotify
    scopes = (
        "playlist-modify-public"
        "playlist-modify-private"
        "playlist-read-private"
        "playlist-read-collaborative"
    )
    sp_session = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scopes))
    return sp_session
