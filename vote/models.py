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
    track_vote = models.IntegerField(default=0)

    def __str__(self):
        return f" Votes for: {self.room} * {self.playlist} * {self.track}"

    def update_vote(self, vote_type):
        # Voting the same way twice resets the vote
        # If the user has already voted up...
        if self.track_vote > 0:
            # And the user votes up...
            if vote_type == 1:
                # Then reset the vote
                self.track_vote = 0
            # Otherwise if the user votes down...
            else:
                # Then record a down vote
                self.track_vote = -1
        # If the user has already voted down...
        elif self.track_vote < 0:
            # And the user votes up...
            if vote_type == 1:
                # Then record an up vote
                self.track_vote = 1
            # Otherwise if the user votes down...
            else:
                # Then reset the vote
                self.track_vote = 0
        # Otherwise the user has not voted yet
        else:
            # So if the user votes up...
            if vote_type == 1:
                # Record an up vote
                self.track_vote = 1
            # So if the user votes down...
            else:
                # Record a down vote
                self.track_vote = -1
        self.save()
