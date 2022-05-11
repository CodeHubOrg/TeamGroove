from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings

from django.db.models import Sum

from playlist.models import Playlist, Track
from room.models import Room
from .models import Vote


@login_required
def show_user_playlist_tracks(request, playlist_id):

    playlist = get_object_or_404(
        Playlist, playlist_id=playlist_id, room=request.user.active_room_id
    )
    room = get_object_or_404(Room, id=request.user.active_room_id)
    tracks = Track.objects.filter(playlist_id=playlist)

    votes = {}
    for track in tracks:
        # Return the total votes for each of the tracks in the playlist for the active room
        total_votes_track = (
            Vote.objects.filter(playlist_id=playlist.pk)
            .filter(track_id=track)
            .filter(room_id=request.user.active_room_id)
            .aggregate(Sum("track_vote"))
        )
        votes[track.track_name] = total_votes_track["track_vote__sum"]

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
def spotify_up_vote(request, playlist_id, track_id):

    playlist = get_object_or_404(
        Playlist, playlist_id=playlist_id, room=request.user.active_room_id
    )
    room = get_object_or_404(Room, id=request.user.active_room_id)

    track = get_object_or_404(Track, playlist_id=playlist.pk, track_id=track_id)

    tracks = Track.objects.filter(playlist_id=playlist)
    # If the track hasn't been voted on before by the user then create a vote for it.
    # call vote_for_track function passing 1 or -1
    votes = vote_for_track(request, playlist, tracks, track, room, 1)

    return render(
        request,
        "vote_track.html",
        {"tracks": tracks, "playlist": playlist, "votes": votes},
    )


@login_required
def spotify_down_vote(request, playlist_id, track_id):

    playlist = get_object_or_404(
        Playlist, playlist_id=playlist_id, room=request.user.active_room_id
    )

    track = get_object_or_404(Track, playlist_id=playlist.pk, track_id=track_id)
    room = get_object_or_404(Room, id=request.user.active_room_id)

    tracks = Track.objects.filter(playlist_id=playlist)
    # call vote_for_track function passing an upvote or downvote (1 or -1)
    votes = vote_for_track(request, playlist, tracks, track, room, -1)

    return render(
        request,
        "vote_track.html",
        {"tracks": tracks, "playlist": playlist, "votes": votes},
    )


def vote_for_track(request, playlist, tracks, track, room, vote_type):
    # If the track in a playlist in a room hasn't
    # been voted on before by the user then create a vote for it.
    if (
        Vote.objects.filter(playlist=playlist)
        .filter(track=track)
        .filter(created_by=request.user)
        .count()
        == 0
    ):
        Vote.objects.create(
            playlist=playlist, track=track, created_by=request.user, room=room
        )
        vote = get_object_or_404(
            Vote, playlist_id=playlist.pk, track_id=track.pk, created_by=request.user
        )
        if vote_type == 1:
            vote.track_vote += 1
            vote.save()
        else:
            vote.track_vote -= 1
            vote.save()
    else:
        messages.info(request, "You have already voted for this track.")

    votes = {}
    for track in tracks:
        # Return the votes for each of the tracks in the playlist for the room.
        total_votes_track = (
            Vote.objects.filter(playlist_id=playlist.pk)
            .filter(track_id=track)
            .filter(room_id=request.user.active_room_id)
            .aggregate(Sum("track_vote"))
        )
        votes[track.track_name] = total_votes_track["track_vote__sum"]

    return votes
