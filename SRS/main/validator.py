import re    
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

def validate_user_password(password):
    try:
        validate_password(password)
    except ValidationError as e:
        raise ValidationError({'password': e.messages})

class MinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ("This password must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return (
            "Your password must contain at least %(self.min_length)d characters."
            % {'min_length': self.min_length}
        )


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                ("The password must contain at least %(min_digits)d digit(s), 0-9."),
                code='password_no_number',
                params={'min_digits': 1},
            )

    def get_help_text(self):
        return (
            "Your password must contain at least 1 digit, 0-9."
        )


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                ("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return (
            "Your password must contain at least 1 uppercase letter, A-Z."
        )