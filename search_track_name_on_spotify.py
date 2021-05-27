from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import spotipy
import os

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path(request):
    return caches_folder + request.user.email

# TODO: QUERY (track name or artist, to be specified) is required to call function
@login_required
def add_track_id_to_playlist(request, QUERY=None, spotify_code=None):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private',
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
    TEST_QUERY='Speak'
    QUERY=TEST_QUERY

# %% POST TEST

    returned_query = spotify.search(q=QUERY, limit=10, offset=0, type='track', market='GB')

    returned_track_artist = []
    returned_track_name = []
    returned_track_id = []

    # TRACK_NAME and TRACK_ARTIST are intended for view
    # TRACK_ID is used for adding to a playlist 
    for x in range(10):
        returned_track_artist.append(returned_query['tracks'[x]]['artist'])
        returned_track_name.append(returned_query['tracks'[x]]['name']) 
        returned_track_id.append(returned_query['tracks'[x]]['name'])  
    
    #import pandas as pd 
    # df_track_id = pd.DataFrame(returned_track_id, columns=['track_id'])
    # df_track_name = pd.DataFrame(returned_track_name, columns=['track_name'])
    # df_artist_name = pd.DataFrame(returned_track_artist, columns=['artist_name'])
    # df_track_properties = pd.concat([df_track_id, df_track_name, df_artist_name], axis=1)

    context = {
        'returned_track_name': returned_track_name,
        'returned_track_artist': returned_track_artist,
        'returned_track_id': returned_track_id
    }

    return render(request, 'room.html', context)
