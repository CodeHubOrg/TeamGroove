from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings

from spotify.models import Playlist, Track
from room.models import Room
from .models import Vote
from .utils import return_vote_count


@login_required
def show_user_playlist_tracks(request, playlist_id):

    playlist = get_object_or_404(
        Playlist, playlist_id=playlist_id, room=request.user.active_room_id
    )
    tracks = Track.objects.filter(playlist_id=playlist)

    votes = return_vote_count(
        playlist_id=playlist, tracks=tracks, room=request.user.active_room_id
    )

    return render(
        request,
        "vote_track.html",
        {
            "tracks": tracks,
            "playlist": playlist,
            "votes": votes,
        },
    )


@login_required
def up_vote(request, playlist_id, track_id):

    room_id = request.user.active_room_id
    playlist = get_object_or_404(Playlist, playlist_id=playlist_id, room=room_id)
    room = get_object_or_404(Room, id=room_id)
    track = get_object_or_404(Track, playlist_id=playlist.pk, track_id=track_id)

    (vote, _) = Vote.objects.get_or_create(
        playlist=playlist, track=track, created_by=request.user, room=room
    )
    vote.update_vote(vote_type=1)

    return show_user_playlist_tracks(request, playlist_id)


@login_required
def down_vote(request, playlist_id, track_id):

    playlist = get_object_or_404(
        Playlist, playlist_id=playlist_id, room=request.user.active_room_id
    )
    room = get_object_or_404(Room, id=request.user.active_room_id)
    track = get_object_or_404(Track, playlist_id=playlist.pk, track_id=track_id)

    (vote, _) = Vote.objects.get_or_create(
        playlist=playlist, track=track, created_by=request.user, room=room
    )
    vote.update_vote(vote_type=-1)

    return show_user_playlist_tracks(request, playlist_id)
