from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm


class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()

        user = User.objects.create_user(
            email="test@example.com",
            password="betterpassword",
            first_name="test",
            last_name="ing",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "test")
        self.assertEqual(user.last_name, "ing")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()

        admin_user = User.objects.create_superuser(
            "super@example.com", "betterpassword"
        )
        self.assertEqual(admin_user.email, "super@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_superuser)

    def test_email_already_exists(self):
        User = get_user_model()

        test_user = User.objects.create_user(
            email="test_already_exists@example.com", password="betterpassword"
        )

        data = {
            "email": "test_already_exists@example.com",
            "password1": "betterpassword",
            "password2": "betterpassword",
        }
        form = CustomUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["email"].errors, ["User with this Email address already exists."]
        )

    def test_invalid_email(self):
        data = {
            "email": "test_invalid_email!",
            "password1": "betterpassword",
            "password2": "betterpassword",
        }

        form = CustomUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["email"].errors, ["Enter a valid email address."])

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
            },
        ]
    )
    def test_validate_too_similar_password(self):
        data = {
            "email": "test_validate_too_similar@example.com",
            "password1": "test_validate_too_similar@example.com",
            "password2": "test_validate_too_similar@example.com",
        }

        form = CustomUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["password2"].errors,
            ["The password is too similar to the email address."],
        )

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        ]
    )
    def test_validate_too_common_password(self):
        data = {
            "email": "test_validate_too_common@example.com",
            "password1": "password",
            "password2": "password",
        }

        form = CustomUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form["password2"].errors, ["This password is too common."])

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
            },
        ]
    )
    def test_validate_numeric_password(self):
        data = {
            "email": "test_validate_numeric_password@example.com",
            "password1": "12345678",
            "password2": "12345678",
        }

        form = CustomUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["password2"].errors, ["This password is entirely numeric."]
        )

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
            },
        ]
    )
    def test_validate_minimum_length_password(self):
        data = {
            "email": "test_minimum_length_password@example.com",
            "password1": "bad",
            "password2": "bad",
        }

        form = CustomUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["password2"].errors,
            ["This password is too short. It must contain at least 8 characters."],
        )

    def test_email_too_long(self):
        data = {
            "email": "b" * 254 + "test_maximum_length_email@example.com",
            "password1": "betterpassword",
            "password2": "betterpassword",
        }

        form = CustomUserCreationForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.fields["email"].max_length, 254)
        self.assertEqual(
            form["email"].errors,
            ["Ensure this value has at most 254 characters (it has 291)."],
        )

    @override_settings(
            AUTH_PASSWORD_VALIDATORS=[
                {
                    'NAME': 'users.validators.MaximumLengthValidator',
                        'OPTIONS': {
                                    'max_length': 200, 
                                    }
                },
            ]
        )
    def test_password_too_long(self):
        data = {
            "email": "test_maximum_length_password@example.com",
            "password1": "betterpassword" * 100,
            "password2": "betterpassword" * 100,
        }

        form = CustomUserCreationForm(data)
        
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form["password2"].errors,
            ["This password is greater than the maximum of 200 characters."],
        )