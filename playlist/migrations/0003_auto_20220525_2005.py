# Generated by Django 3.2.13 on 2022-05-25 20:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0002_auto_20220511_2140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='playlist',
            old_name='playlist_id',
            new_name='ext_playlist_id',
        ),
        migrations.RenameField(
            model_name='track',
            old_name='track_id',
            new_name='ext_track_id',
        ),
    ]
