from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings

import spotipy

from .models import Playlist
from room.models import Room


def session_cache_path(request):
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

    playlist = Playlist.objects.create(room=room, created_by=request.user, playlist_id=playlist_id, playlist_name=playlist_name)
    # Need to add the tracks from the playlist to our db here so we can let people vote on them later?

    messages.info(request, "Your playlist was added to your room.")

    return redirect('room', room_id=request.user.active_room_id)