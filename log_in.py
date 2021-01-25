import spotipy
from spotipy.oauth2 import SpotifyOAuth
from CLIENT_SECRET import CLIENT_SECRET

scopes = "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"

def get_Oauth(scope):
    redirect_url = "http://127.0.0.1:9090"
    # client
    Spotify_Oauth = SpotifyOAuth(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=redirect_url,scope=scope)
    return Spotify_Oauth

sp = spotipy.Spotify(auth_manager=get_Oauth(scope=scopes))

