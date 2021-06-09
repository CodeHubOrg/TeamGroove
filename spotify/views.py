from typing import NoReturn
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings

import spotipy
import os

from .models import Playlist
from room.models import Room


# Default parameter value to start while loop
NEXT = 'https://api.spotify.com'


def session_cache_path(request):
    print(settings.CACHES_FOLDER)
    return f'{settings.CACHES_FOLDER}/{request.user.email}'

@login_required
def authorize_with_spotify(request, spotify_code=None):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-read-private',
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
    current_user_playlists = spotify.current_user_playlists()
    
    context = {
        'current_user_playlists': current_user_playlists
    }

    return render(request, 'user_playlists.html', context)

# TO DO: Refactor functions
@login_required
def get_playlist_items(request, auth_manager, PLAYLIST_ID):
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    MAX_ITEMS_LIMIT    = 100
    OFFSET             = 0
    OFFSET_UPPER_LIMIT = 10
    playlist_items     = None

    while ( ( NEXT != 'null' | NEXT != None ) & ( OFFSET <= OFFSET_UPPER_LIMIT ) ):
        try:
            returned_data = spotify.playlist_items(playlist_id=PLAYLIST_ID, 
                                                   fields=None, 
                                                   limit=MAX_ITEMS_LIMIT, 
                                                   offset=OFFSET, 
                                                   market='GB', 
                                                   additional_types='track')
            LIMIT = returned_data['limit']
            NEXT  = returned_data['next']
            TOTAL = returned_data['total']

            if TOTAL > 0:
                playlist_items = append_track_data(returned_data, LIMIT)
            else:
                break
        except:        
            messages.error(request, 'ERROR ' + request['error']['status'] + ': ' + 'Playlist Items ' + request['error']['message'])
        else:
            messages.success(request, 'SUCCESS: Playlist Items Fetched')
        
        OFFSET += 1

        if OFFSET > OFFSET_UPPER_LIMIT:
            messages.error(request, 'ERROR: There are over 1000 songs in your playlist? Let''s stop here!')
            break
        else:
            pass
    
    return playlist_items

# Scenario 1: Add a new track using a valid Spotify track name - Happy Path
# Scenario 2a: Search for a new track using an ambiguous Spotify track name - Happy Path
# Scenario 2b: Search for a new track to add to the playlist - Happy Path
@login_required
def search_track_name_on_spotify(request, auth_manager, QUERY, PLAYLIST_ID):
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    MAX_SEARCH_LIMIT   = 100
    OFFSET             = 0
    OFFSET_UPPER_LIMIT = 1
    search_results     = None

    while ( ( NEXT != 'null' | NEXT != None ) & ( OFFSET <= OFFSET_UPPER_LIMIT ) ):
        try:
            returned_data = spotify.search(q=QUERY, limit=MAX_SEARCH_LIMIT, offset=OFFSET, type='track', market='GB')

            LIMIT = returned_data['limit']
            NEXT  = returned_data['next']
            TOTAL = returned_data['total']
            
            if TOTAL > 0:
                search_results = append_track_data(request, returned_data, LIMIT)
            else:
                messages.info(request, 'INFO: No tracks found.')
                break
        except:
            messages.error(request, 'ERROR: Unknown error fetching track names.')

        OFFSET += 1

        if OFFSET > OFFSET_UPPER_LIMIT:
            messages.error(request, 'ERROR: There are over 100 search results! Let''s stop here!')
            break
        else:
            pass

    return handle_search_results(search_results, PLAYLIST_ID)

@login_required
def handle_search_results(request, search_results, PLAYLIST_ID):
    if len(search_results['track_id']) == 1:
        # Scenario 1: Add a new track using a valid Spotify track name - Happy Path
        TRACK_ID = search_results['track_id']
        add_track_id_to_playlist(request, PLAYLIST_ID, TRACK_ID) 
    elif len(search_results['track_id']) > 1:
        # Scenario 2a: Search for a new track using an ambiguous Spotify track name - Happy Path
        # Scenario 2b: Search for a new track to add to the playlist - Happy Path
        context = search_results
        return render(request, 'handle_search_results.html', context)  
    else:
        messages.info(request, 'INFO: No track available.')
        return redirect('room.html')  
    # Scenario 3: Add a new track using an invalid Spotify track name - Unhappy Path
    # Handled by add_track_id_to_playlist
    # Scenario 4: Add a duplicate track using a Spotify ID - Unhappy Path
    # Handled by add_track_id_to_playlist

@login_required
def add_track_id_to_playlist(request, auth_manager, PLAYLIST_ID, TRACK_ID):
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # TO DO: Do we need to do this again? 
    # Should pass parameter to check how we arrived here, to check when playlist_track_ids were last fetched
    playlist_items = get_playlist_items(PLAYLIST_ID)
    playlist_track_ids = playlist_items['track_id']
    new_playlist_track_ids = playlist_track_ids

    if TRACK_ID not in playlist_track_ids:
        try: 
            # Scenario 1: Add a new track using a valid Spotify ID - Happy Path
            # {
            #         "snapshot_id": "MzgsNjM1NDNkN2I0MGNlNzBjNDc0NGYxODAyOWVhZmEyNjFlZWQxYTZiZg=="
            # }
            snapshot_id = spotify.playlist_add_items(playlist_id=PLAYLIST_ID, items=TRACK_ID, position=None)
        except:
            # Scenario 2: Add a new track using an invalid Spotify ID - Unhappy Path
            # {
            #     "error": {
            #     "status": 400,
            #     "message": "Payload contains a non-existing ID"
            # }
            messages.error(request, 'ERROR ' + request['error']['status'] + ': ' + request['error']['message'])
        else:
            new_playlist_track_ids = get_playlist_items(PLAYLIST_ID)
            messages.success(request, 'SUCCESS? Add track id to playlist attempted.')
    else:
        # Scenario 3: Add a duplicate track using a Spotify ID - Unhappy Path
        messages.error(request, 'ERROR: Track already on playlist')
        return redirect('room.html') 

    context = {
        'PLAYLIST_ID': PLAYLIST_ID,
        'playlist_track_ids': new_playlist_track_ids
    }

    return render(request, 'room.html', context)

@login_required
def append_track_data(request, returned_data, LIMIT):
    # TRACK_ARTIST, TRACK_NAME and TRACK_ALBUM are intended for view
    # TRACK_ID is used for adding to a playlist        
    track_artist = []
    track_name   = []
    track_id     = []
    track_album  = []

    index = 0        
    while index < LIMIT:
        try:
            track_artist.append(returned_data['items'][index]['track']['artists']['name'])
            track_name.append(returned_data['items'][index]['track']['name']) 
            track_id.append(returned_data['items'][index]['track']['id'])
            track_album.append(returned_data['items'][index]['track']['album']['name'])
            index += 1  
        except IndexError:
            break
        except:
            messages.error(request, 'ERROR: Unknown Error compiling track ids, artist names and track names.')
        else:
            context = {
                    'track_artist': track_artist,
                    'track_name':   track_name,
                    'track_id':     track_id,
                    'track_album':  track_album
            }
    
    return context
    
@login_required
def user_playlist_tracks(request, playlist_id, playlist_name):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    user_playlist_tracks = spotify.playlist_items(playlist_id,
                                                    offset=0,
                                                    fields='items.track.id, items.track.name')
    
    list_of_track_ids = []

    for track in user_playlist_tracks['items']:
        list_of_track_ids.append(track['track']['id'])

    results = spotify.tracks(list_of_track_ids)
    
    track_name_artist = []
    for track in results['tracks']:
        track_name_artist.append(track['name'] + ' - ' + track['artists'][0]['name'])              

    context = {
        'playlist_id': playlist_id,
        'playlist_name': playlist_name,
        'track_name_artist': track_name_artist
    }    
    
    return render(request, 'user_playlist_tracks.html', context)

@login_required
def add_playlist_to_room(request, playlist_id, playlist_name):
    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])

    playlist = Playlist.objects.create(room=room, created_by=request.user, playlist_id=playlist_id, playlist_name=playlist_name)
    # Need to add the tracks from the playlist to our db here so we can let people vote on them later?

    messages.info(request, "Your playlist was added to your room.")

    return render(request, 'grooveboard.html')
