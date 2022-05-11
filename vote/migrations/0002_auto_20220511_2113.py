# Generated by Django 3.2.13 on 2022-05-11 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("playlist", "0002_auto_20220511_2140"),
        ("vote", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vote",
            name="playlist",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="playlists",
                to="playlist.playlist",
            ),
        ),
        migrations.AlterField(
            model_name="vote",
            name="track",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tracks",
                to="playlist.track",
            ),
        ),
    ]