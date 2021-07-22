from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings

import spotipy

from .forms import SearchTrackName
from .models import Playlist, Track
from room.models import Room
from .utils import append_track_data


def session_cache_path(request):
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
def user_playlist_tracks(request, playlist_id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    user_playlist_tracks = spotify.playlist_items(playlist_id,
                                                  offset=0,
                                                  fields='items.track.id, items.track.name')
    
    results = spotify.playlist(playlist_id)
    playlist_name = results['name']
    
    list_of_track_ids = []

    for track in user_playlist_tracks['items']:
        list_of_track_ids.append(track['track']['id'])
    
    if not list_of_track_ids:
        messages.info(request, "There are no tracks in your playlist.")
        return redirect('room', room_id=request.user.active_room_id)

    else:
        # Fix for bug where more than 50 tracks in a playlist causes an error.       
        max_tracks_per_call = 50
        track_name_artist = []

        for start in range(0, len(list_of_track_ids), max_tracks_per_call):
            results = spotify.tracks(list_of_track_ids[start: start + max_tracks_per_call])
            for track in results['tracks']:
                track_name_artist.append(track['name'] + ' - ' + track['artists'][0]['name'])

        context = {
            'playlist_id': playlist_id,
            'playlist_name': playlist_name,
            'track_name_artist': track_name_artist
        }    
        
        return render(request, 'user_playlist_tracks.html', context)

@login_required
def add_playlist_to_room(request, playlist_id):
    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
 
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    user_playlist_tracks = spotify.playlist_items(playlist_id,
                                                    offset=0,
                                                    fields='items.track.id, items.track.name')

    results = spotify.playlist(playlist_id)
    playlist_name = results['name']

    if Playlist.objects.filter(room=room).filter(playlist_id=playlist_id).count() == 0:
        playlist = Playlist.objects.create(room=room, created_by=request.user, playlist_id=playlist_id)
        # Need to add the tracks from the playlist to our db here so we can let people vote on them later?
        messages.info(request, "Your playlist was added to your room.")
    else:
        playlist = Playlist.objects.get(room=room, created_by=request.user, playlist_id=playlist_id)
        messages.info(request, "Playlist is already added to your room.")
    
    # for all results (tracks), if not already in database, add to database; else, pass
    for track in results['tracks']:
        if Track.objects.filter(playlist=playlist).filter(track_id=track['id']).count() == 0: 
            Track.objects.create(playlist=playlist, track_id=track['id'], track_name=track['name'], track_artist = track['artists'][0]['name'])
        else:
            pass

    return redirect('room', room_id=request.user.active_room_id)

# Scenario 1: Add a new track using a valid Spotify track name - Happy Path
# Scenario 2a: Search for a new track using an ambiguous Spotify track name - Happy Path
# Scenario 2b: Search for a new track to add to the playlist - Happy Path
@login_required
def search_track_name(request, playlist_id=None):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])
    
    if playlist_id == None:
            playlist = get_object_or_404(Playlist, room=room)
            playlist_id = playlist.playlist_id
    else:
        pass

    MAX_SEARCH_LIMIT   = 2
    NEXT               = 'https://api.spotify.com'
    OFFSET             = 0
    OFFSET_UPPER_LIMIT = MAX_SEARCH_LIMIT*2

    if request.method == 'POST':
        form = SearchTrackName(request.POST)

        if form.is_valid():
            query = request.POST.get('query')

            track_name_artist_album = []
            track_id = []

            while ( ( NEXT != 'null' ) | ( NEXT != None ) ) & ( OFFSET < OFFSET_UPPER_LIMIT ):
                try:
                    returned_data = spotify.search(query, limit=MAX_SEARCH_LIMIT, offset=OFFSET, type='track', market=None)
                    TOTAL = returned_data['tracks']['total']
                    LIMIT = returned_data['tracks']['limit']

                    if TOTAL == 0:
                        messages.info(request, 'INFO: No tracks found.')
                        return redirect('room', room_id=room.id)
                    else:
                        cleaned_search_results = append_track_data(returned_data, track_name_artist_album, track_id, LIMIT)
                        track_name_artist_album = cleaned_search_results['track_name_artist_album']
                        track_id = cleaned_search_results['track_id']
                except:
                    messages.error(request, 'ERROR at search_track_name: Unknown error fetching track names.')
                    return redirect('room', room_id=room.id)

                NEXT  = returned_data['tracks']['next']
                OFFSET += MAX_SEARCH_LIMIT

                tuple_search_results = list(zip(track_name_artist_album, track_id))

            return search_results(request, tuple_search_results, playlist_id)
    else:
        form = SearchTrackName()

    return render(request, 'search_track_name.html', {'form': form})

def search_results(request, cleaned_search_results, playlist_id):
    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])

    if len(cleaned_search_results) == 1:
        # Scenario 1: Add a new track using a valid Spotify track name - Happy Path
        TRACK_ID = cleaned_search_results[1]
        add_track_id_to_playlist(request, playlist_id, TRACK_ID) 
    elif len(cleaned_search_results) > 1:
        # Scenario 2a: Search for a new track using an ambiguous Spotify track name - Happy Path
        # Scenario 2b: Search for a new track to add to the playlist - Happy Path
        context = cleaned_search_results
        return render(request, 'search_results.html', { 'context': context } )  
    else:
        messages.info(request, 'INFO: No tracks available.')
        return redirect('room', room_id=room.id)

@login_required
def add_track_id_to_playlist(request, track_id):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path(request))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    current_user = spotify.current_user()
    user_id = current_user['id']

    room = get_object_or_404(Room, pk=request.user.active_room_id, created_by=request.user, status=Room.ACTIVE, members__in=[request.user])
    playlist = get_object_or_404(Playlist, room=room)
    playlist_id = playlist.playlist_id

    if Track.objects.filter(playlist=playlist).filter(track_id=track_id).count() == 0:
        try: 
            # Scenario 1: Add a new track using a valid Spotify ID - Happy Path
            spotify.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=[track_id], position=None)
            track = spotify.track(track_id=track_id)
            Track.objects.create(playlist=playlist, track_id=track_id, track_name=track['name'], track_artist=track['artists'][0]['name'])
        except:
            # Scenario 2: Add a new track using an invalid Spotify ID - Unhappy Path
            # {
            #     "error": {
            #     "status": 400,
            #     "message": "Payload contains a non-existing ID"
            # }
            messages.error(request, request['error']['status'] + ' ' + request['error']['message'])
            return redirect('room', room_id=room.id)
        else:
            messages.success(request, 'SUCCESS? Add track id to playlist attempted.')
    else:
        # Scenario 3: Add a duplicate track using a Spotify ID - Unhappy Path
        messages.error(request, 'ERROR: Track already on playlist')
        return redirect('room', room_id=room.id) 

    return redirect('room', room_id=request.user.active_room_id)