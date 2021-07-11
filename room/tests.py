from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test.client import Client

from room.models import Room, Invitation
from room.forms import AddRoom, EditRoom, EmailInvite


class AddRoomFormTests(TestCase):
    # test form validation
    def test_add_room_max_characters(self):
        form = AddRoom(data={"title": "Maximum characters working?" * 10})

        self.assertEqual(
            form.errors["title"],
            ["Ensure this value has at most 255 characters (it has 270)."],
        )


class EmailInviteFormTests(TestCase):
    # test form validation
    def test_invite_to_room_vaild_email(self):
        form = EmailInvite(data={"email": "not a valid email"})

        self.assertEqual(
            form.errors["email"],
            ["Enter a valid email address."],
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

        response = self.client.post(
            "/room/edit_room/", data={"title": "bRave in a cave"}
        )

        # Django should redirect to room 1 as it is now active and we've changed the title
        self.assertEqual(response.status_code, 302)


class DeleteRoomView(TestCase):
    def test_login_required(self):
        response = self.client.get("/room/delete_room/1/")

        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 302)

    def test_delete_room(self):
        # create user and login
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test_delete_a_room@example.com",
            password="betterpassword",
        )

        self.client.login(
            email="test_delete_a_room@example.com", password="betterpassword"
        )

        # create a room so we can delete it
        response = self.client.post(
            "/room/add_room/", data={"title": "Short lived room"}
        )

        response = self.client.get("/room/delete_room/1/")

        # Django should redirect to grooveboard
        self.assertEqual(response.status_code, 302)


class InviteToRoomView(TestCase):
    def test_login_required(self):
        response = self.client.get("/room/invite/")

        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 302)

    def test_invite_to_room(self):
        # create user and login
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test_invite_to_room@example.com",
            password="betterpassword",
        )

        self.client.login(
            email="test_invite_to_room@example.com", password="betterpassword"
        )

        # create a room so we can invite people to it
        response = self.client.post("/room/add_room/", data={"title": "Inviting room"})
        # activate room
        response = self.client.get("/room/activate_room/1/")
        # create an invite
        response = self.client.post(
            "/room/invite/", data={"email": "DiscoStu@example.com"}
        )

        # Django should redirect back to active room
        self.assertEqual(response.status_code, 302)


class DeleteInviteToRoom(TestCase):
    def test_login_required(self):
        response = self.client.get("/room/delete_invitation/bob@example.com/")

        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 302)

    def test_delete_invite_to_user(self):
        # create user and login
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test_delete_invite@example.com",
            password="betterpassword",
        )

        self.client.login(
            email="test_delete_invite@example.com", password="betterpassword"
        )

        # create a room so we can invite people to it
        response = self.client.post(
            "/room/add_room/", data={"title": "You aren't invited room"}
        )
        # activate room
        response = self.client.get("/room/activate_room/1/")
        # create an invite
        response = self.client.post(
            "/room/invite/", data={"email": "DiscoStu@example.com"}
        )
        # Delete DiscoStu invitation because we don't dig disco
        response = self.client.get("/room/delete_invitation/DiscoStu@example.com/")

        # Django should redirect back to active room
        self.assertEqual(response.status_code, 302)


class DeleteUserFromRoom(TestCase):
    def test_login_required(self):
        response = self.client.get("/room/remove_user_from_room/bob@example.com/")

        # Django should redirect to login page as client not logged in
        self.assertEqual(response.status_code, 302)

    def test_delete_user_from_room(self):
        # create user and login
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="test_delete_user@example.com",
            password="betterpassword",
        )

        self.client.login(
            email="test_delete_user@example.com", password="betterpassword"
        )

        # Create a room so we can invite people to it
        response = self.client.post(
            "/room/add_room/", data={"title": "You are goint to be deleted"}
        )
        # Activate room
        response = self.client.get("/room/activate_room/1/")
        # Create an invite
        response = self.client.post(
            "/room/invite/", data={"email": "DiscoStu@example.com"}
        )

        self.client.logout()
        # Need to logon as DiscoStu so we can accept the invitation.
        User = get_user_model()
        self.client = Client()

        user = User.objects.create_user(
            email="DiscoStu@example.com",
            password="betterpassword",
        )

        self.client.login(email="DiscoStu@example.com", password="betterpassword")

        # How to retrieve Disco Stu's invitation code? Direct from DB? Works but not how Stu gets his code.
        test_invite = Invitation.objects.get(email="DiscoStu@example.com")

        response = self.client.post(
            "/room/accept_invitation/", data={"invitation_code": test_invite}
        )
        # Logout Disco Stu
        self.client.logout()

        # Login with our test user again
        self.client.login(
            email="test_delete_user@example.com", password="betterpassword"
        )
        # Delete DiscoStu from room because we don't dig disco.
        response = self.client.get("/room/remove_user_from_room/DiscoStu@example.com/")

        # Django should redirect back to active room
        self.assertEqual(response.status_code, 302)
