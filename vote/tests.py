from django.test import TestCase
from django.contrib.auth import get_user_model

from room.models import Room
from spotify.models import Playlist, Track
from users.models import CustomUser
from .models import Vote
from .utils import return_vote_count

import logging

logger = logging.getLogger(__name__)


class VoteUnitTests(TestCase):
    def setUp(self):
        # create users
        User = get_user_model()
        self.user1 = User.objects.create(
            email="test1@example.com",
            first_name="firstname1",
            last_name="lastname1",
        )
        self.user1.save()
        self.user2 = User.objects.create(
            email="test2@example.com",
            first_name="firstname2",
            last_name="lastname2",
        )
        self.user2.save()
        # create room
        self.room = Room.objects.create(title="test_room1", created_by=self.user1)
        self.room.members.add(self.user1)
        self.room.members.add(self.user2)
        self.room.save()
        # create playlist
        self.playlist = Playlist.objects.create(
            room=self.room,
            created_by=self.user1,
            playlist_id="playlist_id1",
            playlist_name="Playlist 1",
        )
        self.playlist.save()
        # create track(s)
        self.track1 = Track.objects.create(
            playlist=self.playlist,
            track_id="track_id1",
            track_name="Track Name 1",
            track_artist="Track Artist 1",
        )
        self.track2 = Track.objects.create(
            playlist=self.playlist,
            track_id="track_id2",
            track_name="Track Name 2",
            track_artist="Track Artist 2",
        )
        self.track1.save()
        self.track2.save()
        # create tracks
        self.tracks = Track.objects.filter(playlist_id=self.playlist)
        # create votes
        self.vote1 = Vote.objects.create(
            track=self.track1,
            playlist=self.playlist,
            created_by=self.user1,
            room=self.room,
        )
        self.vote2 = Vote.objects.create(
            track=self.track2,
            playlist=self.playlist,
            created_by=self.user1,
            room=self.room,
        )
        self.vote3 = Vote.objects.create(
            track=self.track1,
            playlist=self.playlist,
            created_by=self.user2,
            room=self.room,
        )
        self.vote4 = Vote.objects.create(
            track=self.track2,
            playlist=self.playlist,
            created_by=self.user2,
            room=self.room,
        )

    def test_single_user_create_up_vote(self):
        """Create an up vote for a track by a single user"""

        self.vote1.update_vote(1)
        self.assertEqual(self.vote1.track_vote, 1)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], 1)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_single_user_create_down_vote(self):
        """Create a down vote for a track by a single user"""

        self.vote1.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, -1)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], -1)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_single_user_second_up_vote(self):
        """Place a second up vote for a track by a single user with an existing vote"""

        self.vote1.update_vote(1)
        self.assertEqual(self.vote1.track_vote, 1)
        self.vote1.update_vote(1)
        self.assertEqual(self.vote1.track_vote, 0)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], 0)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_single_user_second_down_vote(self):
        """Place a second down vote for a track by a single user with an existing vote"""

        self.vote1.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, -1)
        self.vote1.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, 0)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], 0)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_single_user_change_to_down_vote(self):
        """Place a down vote for a track by a single user with an existing up vote"""

        self.vote1.update_vote(1)
        self.assertEqual(self.vote1.track_vote, 1)
        self.vote1.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, -1)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], -1)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_single_user_change_to_up_vote(self):
        """Place an up vote for a track by a single user with an existing down vote"""

        self.vote1.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, -1)
        self.vote1.update_vote(1)
        self.assertEqual(self.vote1.track_vote, 1)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], 1)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_two_users_vote_up_on_track(self):
        """Place two up votes for different users on the same track"""

        self.vote1.update_vote(1)
        self.assertEqual(self.vote1.track_vote, 1)
        self.vote3.update_vote(1)
        self.assertEqual(self.vote1.track_vote, 1)
        self.assertEqual(self.vote3.track_vote, 1)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], 2)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_two_users_vote_down_on_track(self):
        """Place two down votes for different users on the same track"""

        self.vote1.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, -1)
        self.vote3.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, -1)
        self.assertEqual(self.vote3.track_vote, -1)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], -2)
        self.assertEqual(votes["Track Name 2"], 0)

    def test_two_users_vote_up_down_on_track(self):
        """Place two down votes for different users on the same track"""

        self.vote1.update_vote(-1)
        self.assertEqual(self.vote1.track_vote, -1)
        self.vote3.update_vote(1)
        self.assertEqual(self.vote1.track_vote, -1)
        self.assertEqual(self.vote3.track_vote, 1)

        votes = return_vote_count(self.playlist, self.tracks, self.room)
        self.assertEqual(votes["Track Name 1"], 0)
        self.assertEqual(votes["Track Name 2"], 0)


class VoteViewsTests(TestCase):
    def setUp(self):
        # create user
        User = get_user_model()

        user1 = User.objects.create(
            email="vote_view_tests@example.com",
            password="betterpassword1",
            first_name="firstname1",
            last_name="lastname1",
        )
        user1.save()

        # create room
        room = Room.objects.create(title="test_room1", created_by=user1)
        room.members.add(user1)
        room.save()
        # create playlist
        playlist = Playlist.objects.create(
            room=room,
            created_by=user1,
            playlist_id="playlist_id1",
            playlist_name="Playlist 1",
        )
        playlist.save()
        # create track(s)
        track1 = Track.objects.create(
            playlist=playlist,
            track_id="track_id1",
            track_name="Track Name 1",
            track_artist="Track Artist 1",
        )
        track1.save()
        track2 = Track.objects.create(
            playlist=playlist,
            track_id="track_id2",
            track_name="Track Name 2",
            track_artist="Track Artist 2",
        )
        track2.save()

    def test_login_required(self):
        response = self.client.get("/vote/show_user_playlist_tracks/playlist_id1/")
        # Django should redirect to login page as client not logged in
        self.assertRedirects(
            response, "/login/?next=/vote/show_user_playlist_tracks/playlist_id1/"
        )

    def test_invalid_playlist(self):
        User = get_user_model()

        user1 = User.objects.filter(email="vote_view_tests@example.com")
        logger.info("test_invalid_playlist - user1: %s", user1[0])
        # login
        login = self.client.login(
            email="vote_view_tests@example.com", password="betterpassword1"
        )
        logger.info("test_invalid_playlist - login: %s", login)

        response = self.client.get("/vote/show_user_playlist_tracks/no_such_playlist/")
        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "")

    def test_valid_playlist(self):
        # login
        login = self.client.login(
            email="vote_view_tests@example.com", password="betterpassword1"
        )
        logger.info("test_valid_playlist - login: %s", login)

        response = self.client.get("/vote/show_user_playlist_tracks/no_such_playlist/")
        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_playlist_tracks.html")
