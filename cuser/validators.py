# Custom password validator as Django doesn't enforce max password length checks
# which is a bit silly on a hashing function that has a lot of iterations (32,000 default)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MaximumLengthValidator:
    def __init__(self, max_length=200):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password is greater than the maximum of %(max_length)d characters."),
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return _(
            "Your password can be a maximum of %(max_length)d characters."
            % {'max_length': self.max_length}
        )