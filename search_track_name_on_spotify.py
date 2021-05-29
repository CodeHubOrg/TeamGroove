from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import spotipy
import os


from spotify.views import add_track_id_to_playlist


# TO DO: refactor Spotify authorization
TEST_QUERY='Speak'
QUERY=TEST_QUERY


MAX_SEARCH_LIMIT = 10


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path(request):
    return caches_folder + request.user.email

# TODO: QUERY (track name or artist, to be specified) is required to call function
@login_required
def search_track_name_on_spotify(request, QUERY=None, spotify_code=None):
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

    try:
        returned_query = spotify.search(q=QUERY, limit=10, offset=0, type='track', market='GB')

        returned_track_artist = []
        returned_track_name = []
        returned_track_id = []

        # TRACK_NAME and TRACK_ARTIST are intended for view
        # TRACK_ID is used for adding to a playlist 
        index = 0
        while index < MAX_SEARCH_LIMIT:
            try:
                returned_track_artist.append(returned_query['tracks'][index]['artist'])
                returned_track_name.append(returned_query['tracks'][index]['name']) 
                returned_track_id.append(returned_query['tracks'][index]['id'])
                index += 1  
                # import pandas as pd 
                # df_track_id = pd.DataFrame(returned_track_id, columns=['track_id'])
                # df_track_name = pd.DataFrame(returned_track_name, columns=['track_name'])
                # df_artist_name = pd.DataFrame(returned_track_artist, columns=['artist_name'])
                # df_track_properties = pd.concat([df_track_id, df_track_name, df_artist_name], axis=1)
            except IndexError:
                break
            except:
                print("ERROR: Unknown error compiling track ids, artists and names.")    
    except:
        print("ERROR: Unknown error fetching track names.")  

    context = {
        'returned_track_name': returned_track_name,
        'returned_track_artist': returned_track_artist,
        'returned_track_id': returned_track_id
        # 'df_track_properties': df_track_properties
    }

    if len(returned_track_id) == 1:
        # Scenario 1: Add a new track using a valid Spotify track name - Happy Path
        return render(request, 'add_track_id_to_playlist.html', context) 
    elif len(returned_track_id) > 1:
        # Scenario 2a: Search for a new track using an ambiguous Spotify track name - Happy Path
        # Scenario 2b: Search for a new track to add to the playlist - Happy Path
        return render(request, 'search_track_name_on_spotify.html', context)  
    else:
        # Scenario 3: Add a new track using an invalid Spotify track name - Unhappy Path
        print("ERROR: Track was not found.")
        return render(request, 'search_track_name_on_spotify.html', context)  

    # Scenario 4: Add a duplicate track using a Spotify ID - Unhappy Path
    # Handled by add_track_id_to_playlist

