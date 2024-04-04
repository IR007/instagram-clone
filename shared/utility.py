import re
import threading

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from twilio.rest import Client

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


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data.get('subject'),
            body=data.get('body'),
            to=[data.get('to_email')]
        )
        if data.get('content_type') == 'html':
            email.content_subtype = 'html'
        EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {"code": code}
    )
    Email.send_email({
        'subject': "Akkauntingizni tasdiqlang",
        "to_email": email,
        'body': html_content,
        'content_type': 'html'
    })


def send_phone(phone_number, code):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Sizning tasdiqlash kodingiz: {code}.\nKodni hech kimga bermang",
        from_="+13343730995",
        to=f"{phone_number}"
    )
