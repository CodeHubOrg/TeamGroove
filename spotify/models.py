from django.db import models

from room.models import Room
from users.models import CustomUser

class Playlist(models.Model):
    # at the moment we only hook into spotify but we might want to
    # use other services so do we want an identifier for playlist source/type?
    room = models.ForeignKey(Room, related_name='playlists', on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, related_name='created_playlist', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    playlist_id = models.CharField(max_length=50)
    playlist_name = models.CharField(max_length=255)

    def __str__(self):
        return self.playlist_name

class Track(models.Model):
    playlist = models.ForeignKey(Playlist, related_name='tracks', on_delete=models.CASCADE)
    track_id = models.CharField(max_length=50)
    track_name = models.CharField(max_length=255)
    track_artist = models.CharField(max_length=255)

    def __str__(self):
        return self.track_name