import re

from rest_framework.exceptions import ValidationError

from users.models import VIA_EMAIL, VIA_PHONE

phone_regex = re.compile(r"^[\+]?[(]?[0-9]{2,5}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{2,4}[-\s\.]?[0-9]{2}$")
email_regex = re.compile(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")


def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        return VIA_EMAIL
    elif re.fullmatch(phone_regex, email_or_phone):
        return VIA_PHONE
    else:
        data = {
            'success': False,
            'message': "Telefon yoki email manzilingiz xato"
        }
        raise ValidationError(data)
