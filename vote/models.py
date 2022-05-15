from django.db import models
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from room.models import Room
from users.models import CustomUser
from spotify.models import Track, Playlist


class Vote(models.Model):
    track = models.ForeignKey(Track, related_name="tracks", on_delete=models.CASCADE)
    playlist = models.ForeignKey(
        Playlist, related_name="playlists", on_delete=models.CASCADE
    )
    room = models.ForeignKey(Room, related_name="rooms", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        CustomUser, related_name="created_by", on_delete=models.CASCADE
    )
    # Not sure how we are going to handle voting? 0-5 or 0-10, etc. Do we check for the same person voting
    # multiple times and trying to rig the playlist for their favourite/hated track?
    track_vote = models.IntegerField(default=0)

    def __str__(self):
        return f" Votes for: {self.room} * {self.playlist} * {self.track}"

    def update_vote(self, vote_type):
        # If the upvote already exists, then unset upvote
        # If the downvote already exists, then unset downvote
        # If upvote already exists and then downvote is clicked, unset upvote and set downvote
        # If downvote already exists and then upvote is clicked, unset downvote and set upvote
        # If the track in a playlist in a room hasn't
        # been voted on before by the user then create a vote for it.
        if self.track_vote == 1:
            if vote_type == 1:
                self.track_vote -= 1
            else:
                self.track_vote -= 2
        elif self.track_vote == -1:
            if vote_type == 1:
                self.track_vote += 2
            else:
                self.track_vote += 1
        else:
            if vote_type == 1:
                self.track_vote += 1
            else:
                self.track_vote -= 1
        self.save()

    def return_vote_count():
        votes = {}
        for track in tracks:
            # Return the votes for each of the tracks in the playlist for the room.
            total_votes_track = (
                Vote.objects.filter(playlist_id=playlist.pk)
                .filter(track_id=track)
                .filter(room_id=user.active_room_id)
                .aggregate(Sum("track_vote"))
            )
            votes[track.track_name] = total_votes_track["track_vote__sum"]

        return votes