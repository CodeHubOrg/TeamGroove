# Generated by Django 3.2.13 on 2022-05-11 21:40

from django.db import migrations
import logging

logger = logging.getLogger(__name__)


def move_spotify_playlists(apps, schema_editor):
    Spotify_Playlist = apps.get_model("spotify", "Playlist")
    Spotify_Track = apps.get_model("spotify", "Track")
    Playlist_Playlist = apps.get_model("playlist", "Playlist")
    Playlist_Track = apps.get_model("playlist", "Track")
    Vote = apps.get_model("Vote", "Vote")

    # Migrate each playlist
    for spotify_playlist in Spotify_Playlist.objects.all():
        logger.info("move_spotify_playlists: from %s", str(spotify_playlist))
        playlist_playlist = Playlist_Playlist.objects.create(
            room=spotify_playlist.room,
            created_by=spotify_playlist.created_by,
            created_at=spotify_playlist.created_at,
            playlist_id=spotify_playlist.playlist_id,
            playlist_name=spotify_playlist.playlist_name,
        )
        playlist_playlist.save()
        logger.info("move_spotify_playlists: to %s", str(playlist_playlist))

        # Migrate each track
        for spotify_track in Spotify_Track.objects.filter(
            playlist_id=spotify_playlist.id
        ):
            logger.info("move_spotify_tracks: from %s", str(spotify_track))
            playlist_track = Playlist_Track.objects.create(
                playlist_id=playlist_playlist.id,
                track_id=spotify_track.track_id,
                track_name=spotify_track.track_name,
                track_artist=spotify_track.track_artist,
            )
            playlist_track.save()
            logger.info("move_spotify_tracks: to %s", str(playlist_track))


class Migration(migrations.Migration):

    dependencies = [
        ("spotify", "0003_delete_vote"),
        ("playlist", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(move_spotify_playlists),
    ]
