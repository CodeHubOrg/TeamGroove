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

        response = self.client.get(reverse('grooveboard'))
        test_room = response.context['rooms'][0]
        self.assertEqual('test room', test_room.title)
        self.assertEqual(response.status_code, 200)        

    def test_user_has_invitations(self):
        User = get_user_model()
        self.client = Client()

        send_invite_user = User.objects.create_user(
            email="test_send_invite@example.com",
            password="betterpassword",
        )
        accept_invite_user = User.objects.create_user(
            email="test_accept_invite@example.com",
            password="betterpassword",
        )

        self.client.login(email='test_accept_invite@example.com', password='betterpassword')
        # create invitation so we can check grooveboard redirects to accept_invitation
        room = Room.objects.create(title='invite room', created_by=send_invite_user)
        room.members.add(send_invite_user)
        room.save()
        invitation = Invitation.objects.create(email='test_accept_invite@example.com', room=room, invitation_code='12345678')        
        invitation.save()

        response = self.client.get(reverse('grooveboard'))
        self.assertEqual(response.status_code, 302)


