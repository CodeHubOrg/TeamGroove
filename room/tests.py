from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test.client import Client

from room.models import Room, Invitation
from room.forms import AddRoom, EditRoom


class AddRoomFormTests(TestCase):
    # test form validation
    def test_add_room_max_characters(self):
        form = AddRoom(data={"title": "Maximum characters working?" * 10})

        self.assertEqual(
            form.errors["title"],
            ["Ensure this value has at most 255 characters (it has 270)."],
        )


class EditRoomFormTests(TestCase):
    # test form validation
    def test_add_room_max_characters(self):
        form = EditRoom(data={"title": "Maximum characters working?" * 10})

        self.assertEqual(
            form.errors["title"],
            ["Ensure this value has at most 255 characters (it has 270)."],
        )


class AddRoomViewTests(TestCase):
    def test_login_required(self):
        response = self.client.get("/room/add_room/")

        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 302)

    def test_add_a_room(self):
        # create user and login
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test_add_a_room@example.com",
            password="betterpassword",
        )

        self.client.login(
            email="test_add_a_room@example.com", password="betterpassword"
        )

        response = self.client.post(
            "/room/add_room/", data={"title": "Very Silent Disco"}
        )
        # Django redirects to grooveboard if successful
        self.assertEqual(response.status_code, 302)


class ActivateRoomViewTests(TestCase):
    def test_login_required(self):
        response = self.client.get("/room/activate_room/1/")

        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 302)

    def test_activate_room(self):
        # create user and login
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test_activate_a_room@example.com",
            password="betterpassword",
        )

        self.client.login(
            email="test_activate_a_room@example.com", password="betterpassword"
        )
        # create a room so we can activate it
        response = self.client.post("/room/add_room/", data={"title": "Rave in a cave"})
        # activate room
        response = self.client.get("/room/activate_room/1/")
        # Django should redirect to room 1 as it is now active
        self.assertEqual(response.status_code, 302)
    
class EditRoomView(TestCase):
    def test_login_required(self):
        response = self.client.get("/room/activate_room/1/")

        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 302)

    def test_edit_room_title(self):
        # create user and login
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test_edit_a_room@example.com",
            password="betterpassword",
        )

        self.client.login(
            email="test_edit_a_room@example.com", password="betterpassword"
        )
        # create a room so we can activate it
        response = self.client.post("/room/add_room/", data={"title": "Rave in a cave"})
        # activate room
        response = self.client.get("/room/activate_room/1/")
        
        response = self.client.post("/room/edit_room/", data={"title": "bRave in a cave"})
        
        # Django should redirect to room 1 as it is now active and we've changed the title
        self.assertEqual(response.status_code, 302)
