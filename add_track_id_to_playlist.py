from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import spotipy
import os


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path(request):
    return caches_folder + request.user.email

# TODO: TRACK_ID required to call function
# TODO: PLAYLIST_ID required to call function
@login_required
def add_track_id_to_playlist(request, TRACK_ID=None, PLAYLIST_ID=None, spotify_code=None):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager  = spotipy.oauth2.SpotifyOAuth(scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private',
                                                cache_handler=cache_handler,
                                                show_dialog=True)

    # If we have a code from Spotify then grab the autho token and refresh token and bung in .spotify_caches directory.
    if spotify_code:        
        auth_manager.get_access_token(spotify_code)
        # once we have a token we can then do stuff
        spotify = spotipy.Spotify(auth_manager=auth_manager)        
    
    # Do we have an autho token? No - then off we go to Spotify to get a code so we can get one.
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)

# %% TEST
    TEST_PLAYLIST_ID='3k8Cmr6OWfGqbEUvjAiTbS'
    TEST_SEED_ARTIST='6HKDgcx3TeJ3FYL3NOXkV7?'
    TEST_SEED_GENRE='Rock'
    TEST_SEED_TRACK='0urjOvNJIBLAg2UY4defWQ'
    TEST_NO_LIMIT=2

    TEST_RETURNED_TRACKS = spotify.recommendations(seed_artists=TEST_SEED_ARTIST, 
                                                   seed_genres=TEST_SEED_GENRE, 
                                                   seed_tracks=TEST_SEED_TRACK, 
                                                   limit=TEST_NO_LIMIT)

    TEST_TRACK_ID = [TEST_RETURNED_TRACKS['tracks'][0]['id']]

    PLAYLIST_ID = TEST_PLAYLIST_ID
    TRACK_ID = TEST_TRACK_ID

# %% POST TEST
    
    add_track_id_to_playlist = spotify.playlist_add_items(playlist_id=PLAYLIST_ID, 
                                                          items=TRACK_ID, 
                                                          position=None)
    
    # if track has been added to playlist, get updated playlist items and return
    if add_track_id_to_playlist:
        playlist_items = spotify.playlist_tracks(playlist_id=PLAYLIST_ID, 
                                                 fields=None, 
                                                 limit=100, 
                                                 offset=None, 
                                                 market=None)

    context = {
        'playlist_items': playlist_items
    }

    return render(request, 'room.html', context)
