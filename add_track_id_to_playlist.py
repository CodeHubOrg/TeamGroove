from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import spotipy
import os


# TO DO: refactor Spotify authorization
TEST_PLAYLIST_ID='3k8Cmr6OWfGqbEUvjAiTbS'
TEST_SEED_ARTIST='6HKDgcx3TeJ3FYL3NOXkV7?'
TEST_SEED_GENRE='Rock'
TEST_SEED_TRACK='0urjOvNJIBLAg2UY4defWQ'
TEST_NO_LIMIT=2
PLAYLIST_ID = TEST_PLAYLIST_ID


MAX_ITEMS_LIMIT          = 100


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path(request):
    return caches_folder + request.user.email

# get current track ids on playlist to compare with track id to be added
@login_required
def get_playlist_items(request, PLAYLIST_ID=None, spotify_code=None):
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

    try:
        fetched_playlist_track_ids = spotify.playlist_items(playlist_id=PLAYLIST_ID, 
                                                            fields=None, 
                                                            limit=MAX_ITEMS_LIMIT, 
                                                            offset=0, 
                                                            market='GB', 
                                                            additional_types='track')
        index = 0
        while index < MAX_ITEMS_LIMIT: 
            try:
                playlist_track_ids.append(fetched_playlist_track_ids['tracks'][index]['id'])
                index += 1
            except IndexError:
                break
            except:
                playlist_track_ids = []
                print("ERROR: Unknown error compiling track ids.")
    except:
        print("ERROR: Could not get playlist track ids. Risk of duplicated tracks.")
    else:
        print("SUCCESS: Playlist track ids successfully fetched.")
        return playlist_track_ids

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


    TEST_RETURNED_TRACKS = spotify.recommendations(seed_artists=TEST_SEED_ARTIST, 
                                                   seed_genres=TEST_SEED_GENRE, 
                                                   seed_tracks=TEST_SEED_TRACK, 
                                                   limit=TEST_NO_LIMIT)
    TEST_TRACK_ID = [TEST_RETURNED_TRACKS['tracks'][0]['id']]
    TRACK_ID = TEST_TRACK_ID
    

    playlist_track_ids = get_playlist_items(PLAYLIST_ID)

    try: 
        if PLAYLIST_ID not in playlist_track_ids:
            # Scenario 1: Add a new track using a valid Spotify ID - Happy Path
            response_data = spotify.playlist_add_items(playlist_id=PLAYLIST_ID, items=TRACK_ID, position=None)
            # Spotify returns "snapshot id"
        else:
            # Scenario 3: Add a duplicate track using a Spotify ID - Unhappy Path
            response_data = None
            print("Track already on playlist.")
    except:
        # Scenario 2: Add a new track using an invalid Spotify ID - Unhappy Path
        
        # Spotify returns
        # {
        #     "error": {
        #     "status": 400,
        #     "message": "Payload contains a non-existing ID"
        # }
        if response_data['error']['message']:
            error_message = "ERROR: " + response_data['error']['message']
        else:
            error_message = "ERROR: Unknown error"
        
        new_playlist_track_ids = playlist_track_ids
        print(error_message)
        
    else:
        new_playlist_track_ids = get_playlist_items(PLAYLIST_ID)
        print("SUCCESS? Adding track id to playlist attempted.")
        return new_playlist_track_ids

    context = {
        'PLAYLIST_ID': PLAYLIST_ID,
        'playlist_track_ids': new_playlist_track_ids
    }

    return render(request, 'add_track_id_to_playlist.html', context)
