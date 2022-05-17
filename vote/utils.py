from django.db.models import Sum

from .models import Vote


def return_vote_count(playlist_id, tracks, room):

    votes = {}
    for track in tracks:
        # Return the votes for each of the tracks in the playlist for the room.
        total_votes_track = (
            Vote.objects.filter(playlist_id=playlist_id)
            .filter(track_id=track)
            .filter(room_id=room)
            .aggregate(Sum("track_vote"))
        )
        votes[track.track_name] = total_votes_track["track_vote__sum"]

    return votes