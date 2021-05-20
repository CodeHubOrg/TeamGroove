from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test.client import Client

from room.models import Room, Invitation

class GrooveboardViewTests(TestCase):

    def test_user_has_not_logged_in(self):
        response = self.client.get(reverse('grooveboard'))
        # Django should redirect to login page if not logged in         
        self.assertEqual(response.status_code, 302)

    def test_user_has_logged_in(self):
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test@example.com",
            password="betterpassword",
        )

        self.client.login(email='test@example.com', password='betterpassword')
        response = self.client.get(reverse('grooveboard'))      
        self.assertEqual(response.status_code, 200)
        
    def test_user_has_a_room(self):
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test@example.com",
            password="betterpassword",
        )

        self.client.login(email='test@example.com', password='betterpassword')
        # create 'test room' so we can check grooveboard passes the room back
        # in the context
        room = Room.objects.create(title='test room', created_by=user)
        room.members.add(user)
        room.save()