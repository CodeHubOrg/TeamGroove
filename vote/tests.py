from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from room.models import Room
from spotify.models import Playlist, Track
from users.models import CustomUser
from .models import Vote

import json

class VoteTests(TestCase):
    def setUp(self):
        # create users 
        self.user1 = CustomUser.objects.create(
            email="test1@example.com",
            first_name="firstname1",
            last_name="lastname1",
        )
        self.user2 = CustomUser.objects.create(
            email="test2@example.com",
            first_name="firstname2",
            last_name="lastname2",
        )
        self.user1.save()
        self.user2.save()
        # create room
        self.room = Room.objects.create(title='test_room1', created_by=self.user1)
        self.room.members.add(self.user1)
        self.room.members.add(self.user2)
        self.room.save()
        # create playlist
        self.playlist = Playlist.objects.create(room=self.room, created_by=self.user1, playlist_id="playlist_id1", playlist_name="playlist_name1")
        self.playlist.save()
        # create track(s)
        self.track1 = Track.objects.create(playlist=self.playlist, track_id="track_id1", track_name="track_name1", track_artist="track_artist1")
        self.track2 = Track.objects.create(playlist=self.playlist, track_id="track_id2", track_name="track_name2", track_artist="track_artist2")
        self.track1.save()
        self.track2.save()
        # create tracks
        self.tracks = Track.objects.filter(playlist_id=self.playlist)

    # test vote is created
    def test_single_user_create_vote(self):
        # create request for user1
        self.user = self.user1
        # create upvote for track1 by user1
        self.vote_type = 1

        response = self.client.get(reverse('vote'))
        # test model
        self.assertEqual(self.vote.track_vote, 1)

        # create downvote for track2 by user1
        vote_type = -1
        response = self.client.get(reverse('vote'))
        vote_for_track(request, playlist, tracks, track2, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, -1)
        
    # try second vote by user1
    def test_single_user_clear_vote(self):
        # create request for user1
        request.user = user1
        
        # clear upvote by upvoting again on track1
        vote_type = 1
        response = self.client.get(reverse('vote'))
        vote_for_track(request, playlist, tracks, track1, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, 0)

        # clear downvote by downvoting again on track2
        vote_type = -1
        vote_for_track(request, playlist, tracks, track2, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, 0)

    def test_single_user_cross_vote(self):
        # re-add votes by user1
        test_create_votes()

        # create request for user1
        request.user = user1
        
        # clear downvote by upvoting on track2
        vote_type = 1
        response = self.client.get(reverse('vote'))
        vote_for_track(request, playlist, tracks, track2, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, 1)

        # clear upvote by downvoting on track1
        vote_type = -1
        response = self.client.get(reverse('vote'))
        vote_for_track(request, playlist, tracks, track1, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, -1)

        # clear votes
        test_single_user_clear_vote()

    def test_multiple_user_create_vote(self):
        # re-add votes by user1
        test_create_votes()

        # create request for user2
        request.user = user2

        # create upvote for track1 by user2
        vote_type = 1
        response = self.client.get(reverse('vote'))
        vote_for_track(request, playlist, tracks, track1, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, 1)
        # test view
        self.assertEqual(votes[track1.track_name],2)

        # create downvote for track2 by user2
        vote_type = -1
        response = self.client.get(reverse('vote'))
        votes = vote_for_track(request, playlist, tracks, track2, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, -1)
        # test view
        self.assertEqual(votes[track2.track_name],-2)

    def test_multiple_user_clear_vote(self):
        # create request for user2
        request.user = user2

        # clear downvote by upvoting on track2
        vote_type = 1
        response = self.client.get(reverse('vote'))
        vote_for_track(request, playlist, tracks, track1, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, 1)
        # test view
        self.assertEqual(votes[track1.track_name],2)

        # clear upvote by downvoting on track11
        vote_type = -1
        response = self.client.get(reverse('vote'))
        votes = vote_for_track(request, playlist, tracks, track2, room, vote_type)
        # test model
        self.assertEqual(vote.track_vote, -1)
        # test view
        self.assertEqual(votes[track2.track_name],-2)

    def test_multiple_user_cross_vote(self):