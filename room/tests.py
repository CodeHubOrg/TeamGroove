from django.test import TestCase

from .forms import AddRoom, AcceptInvitation, EmailInvite, EditRoom

class AddRoomFormTests(TestCase):

    def test_title_is_less_than_255(self):
        form = AddRoom(data={"title": "a test room name"})

        self.assertEqual(form.errors, {})

    def test_title_is_greater_than_255(self):
        form = AddRoom(data={"title": "test" * 64 })

        self.assertEqual(form.errors['title'], ['Ensure this value has at most 255 characters (it has 256).'])

class AcceptInvitationFormTests(TestCase):

    def test_invitation_code_is_less_than_20(self):
        form = AcceptInvitation(data={"invitation_code": "1234567890"})

        self.assertEqual(form.errors, {})
    
    def test_invitation_code_is_greater_than_20(self):
        form = AcceptInvitation(data={"invitation_code": "a" * 21})

        self.assertEqual(form.errors['invitation_code'], ['Ensure this value has at most 20 characters (it has 21).'])

class EmailInviteFormTests(TestCase):

    def test_email_invite_is_email(self):
        form = EmailInvite(data={"email": "test@test"})

        self.assertEqual(form.errors['email'], ['Enter a valid email address.'])

    def test_email_invite_is_less_than_255(self):
        form = EmailInvite(data={"email": "test@example.com"})

        self.assertEqual(form.errors, {})

    def test_email_invite_is_less_than_255(self):
        form = EmailInvite(data={"email": "test" * 64 + "@example.com"})

        self.assertEqual(form.errors['email'], ['Ensure this value has at most 255 characters (it has 268).'])

class EditRoomFormTests(TestCase):

    def test_title_is_less_than_255(self):
        form = EditRoom(data={"title": "a test room name"})

        self.assertEqual(form.errors, {})

    def test_title_is_greater_than_255(self):
        form = EditRoom(data={"title": "test" * 64 })

        self.assertEqual(form.errors['title'], ['Ensure this value has at most 255 characters (it has 256).'])

