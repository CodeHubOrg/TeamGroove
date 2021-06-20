from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings

import spotipy
import os

from .models import Playlist, Track
from room.models import Room
from .utils import append_track_data

from .forms import SearchTrackName

def session_cache_path(request):
    print(settings.CACHES_FOLDER)
    return f'{settings.CACHES_FOLDER}/{request.user.email}'

@login_required
def authorize_with_spotify(request, spotify_code=None):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-read-private playlist-modify-private playlist-modify-public playlist-read-collaborative',
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
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])

    if Playlist.objects.filter(room=room).filter(playlist_name=playlist_name).count() == 0:
        playlist = Playlist.objects.create(room=room, created_by=request.user, playlist_id=playlist_id, playlist_name=playlist_name)
        # Need to add the tracks from the playlist to our db here so we can let people vote on them later?
        messages.info(request, "Your playlist was added to your room.")
    else:
        playlist = Playlist.objects.get(room=room, created_by=request.user, playlist_id=playlist_id, playlist_name=playlist_name)
        messages.info(request, "Playlist is already added to your room.")

    # TO DO: re-factor from def user_playlist_tracks
    # TO DO: place in .utils file
    user_playlist_tracks = spotify.playlist_items(playlist_id,
                                                  offset=0,
                                                  fields='items.track.id, items.track.name')
    list_of_track_ids = []

    for track in user_playlist_tracks['items']:
        list_of_track_ids.append(track['track']['id'])

    results = spotify.tracks(list_of_track_ids)

    # for all results (tracks), if not already in database, add to database; else, pass
    for track in results['tracks']:
        if Track.objects.filter(playlist=playlist).filter(track_id=track['id']).count() == 0: 
            Track.objects.create(playlist=playlist, track_id=track['id'], track_name=track['name'], track_artist = track['artists'][0]['name'])
        else:
            pass
   
    print(Playlist.objects.all())
    print(Track.objects.all())

    return render(request, 'grooveboard.html')

# Scenario 1: Add a new track using a valid Spotify track name - Happy Path
# Scenario 2a: Search for a new track using an ambiguous Spotify track name - Happy Path
# Scenario 2b: Search for a new track to add to the playlist - Happy Path
@login_required
def search_track_name(request, playlist_id=None):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    MAX_SEARCH_LIMIT   = 100
    NEXT               = 'https://api.spotify.com'
    OFFSET             = 0
    OFFSET_UPPER_LIMIT = 1

    if request.method == 'POST':
        form = SearchTrackName(request.POST)
    
        if form.is_valid():
            query = request.POST.get('query')

            while ( ( NEXT != 'null' ) | ( NEXT != None ) ) & ( OFFSET <= OFFSET_UPPER_LIMIT ):
                try:
                    returned_data = spotify.search(query, limit=MAX_SEARCH_LIMIT, offset=OFFSET, type='track', market='GB')

                    LIMIT = returned_data['limit']
                    NEXT  = returned_data['next']
                    TOTAL = returned_data['total']
                    
                    if TOTAL > 0:
                        search_results = append_track_data(request, returned_data, LIMIT)
                        add_search_result_to_room(search_results, playlist_id)
                    else:
                        messages.info(request, 'INFO: No tracks found.')
                        return redirect('room.html')
                except:
                    messages.error(request, 'ERROR at search_track_name: Unknown error fetching track names.')
                    return redirect('room.html')

                OFFSET += 1

                if OFFSET > OFFSET_UPPER_LIMIT:
                    messages.info(request, 'INFO: There are over 100 search results! Let''s stop here!')
                    return redirect('room.html')
    else:
        form = SearchTrackName()

    return render(request, 'search_track_name.html', {'form': form})

@login_required
def add_search_result_to_room(request, search_results, playlist_id):
    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])
    playlist = get_object_or_404(Playlist, room=room)
    playlist_name = playlist.playlist_name

    if len(search_results['track_id']) == 1:
        # Scenario 1: Add a new track using a valid Spotify track name - Happy Path
        TRACK_ID = search_results['track_id']
        add_track_id_to_playlist(request, playlist_id, playlist_name, TRACK_ID) 
    elif len(search_results['track_id']) > 1:
        # Scenario 2a: Search for a new track using an ambiguous Spotify track name - Happy Path
        # Scenario 2b: Search for a new track to add to the playlist - Happy Path
        context = search_results
        return render(request, 'search_track_name.html', context)  
    else:
        messages.info(request, 'INFO: No tracks available.')
        return redirect('room.html')
    # Scenario 3: Add a new track using an invalid Spotify track name - Unhappy Path
    # Handled by add_track_id_to_playlist
    # Scenario 4: Add a duplicate track using a Spotify ID - Unhappy Path
    # Handled by add_track_id_to_playlist

@login_required
def add_track_id_to_playlist(request, auth_manager, playlist_id, playlist_name, track_id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])

    # TO DO: Tracks are stored in database at user_playlist_tracks function
    if Track.objects.filter(track_id=track_id).count() == 0:
        try: 
            # Scenario 1: Add a new track using a valid Spotify ID - Happy Path
            # {
            #         "snapshot_id": "MzgsNjM1NDNkN2I0MGNlNzBjNDc0NGYxODAyOWVhZmEyNjFlZWQxYTZiZg=="
            # }
            snapshot_id = spotify.playlist_add_items(playlist_id=playlist_id, items=track_id, position=None)
        except:
            # Scenario 2: Add a new track using an invalid Spotify ID - Unhappy Path
            # {
            #     "error": {
            #     "status": 400,
            #     "message": "Payload contains a non-existing ID"
            # }
            messages.error(request, 'ERROR ' + request['error']['status'] + ': ' + request['error']['message'])
            return redirect('room.html')
        else:
            messages.success(request, 'SUCCESS? Add track id to playlist attempted.')
    else:
        # Scenario 3: Add a duplicate track using a Spotify ID - Unhappy Path
        messages.error(request, 'ERROR: Track already on playlist')
        return redirect('room.html') 

    user_playlist_tracks(request, playlist_id, playlist_name)

