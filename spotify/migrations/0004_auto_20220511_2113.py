# Generated by Django 3.2.13 on 2022-05-11 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0002_auto_20220511_2113'),
        ('spotify', '0003_delete_vote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='track',
            name='playlist',
        ),
        migrations.DeleteModel(
            name='Playlist',
        ),
        migrations.DeleteModel(
            name='Track',
        ),
    ]