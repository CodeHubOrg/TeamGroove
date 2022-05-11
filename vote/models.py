from django.db import models

from room.models import Room
from users.models import CustomUser
from playlist.models import Track, Playlist


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
        return f" Votes for: {self.room } * {self.playlist } * {self.track}"
