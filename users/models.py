import datetime
import random
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel

VIA_EMAIL, VIA_PHONE = 'via_email', 'via_phone'
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = 'new', 'code_verified', 'done', 'photo_step'
ORDINARY, MANAGER, ADMIN = 'ordinary', 'manager', 'admin'


class User(AbstractUser, BaseModel):
    AUTH_TYPE_STATUS = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )
    USER_ROLE = (
        (ORDINARY, ORDINARY),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    GENDER_CHOICE = (
        ('male', 'male'),
        ('female', 'female')
    )
    auth_type = models.CharField(max_length=10, choices=AUTH_TYPE_STATUS)
    auth_status = models.CharField(max_length=15, default=NEW, choices=AUTH_STATUS)
    user_role = models.CharField(max_length=15, default=ORDINARY, choices=USER_ROLE)
    email = models.EmailField(max_length=50, null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICE, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.username}"

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    def default_username(self):
        if not self.username:
            # 904a9321-c11f-4db9-bf0c-031de85b0223
            # instagram-031de85b0223
            norm_username = f"instagram-{str(uuid4()).split('-')[-1]}"
            while User.objects.filter(username=norm_username):
                norm_username += str(random.randrange(1, 9))
            self.username = norm_username

    def default_password(self):
        if not self.password:
            norm_password = f"password-{str(uuid4()).split('-')[-1]}"
            self.password = norm_password

    def check_email(self):
        if self.email:
            norm_email = str(self.email).lower()
            self.email = norm_email

    def hash_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def clean(self):
        self.default_username()
        self.default_password()
        self.check_email()
        self.hash_password()

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)

    def create_verify_code(self, verify_type):
        code = ''.join([str(random.randint(1, 10)) for _ in range(4)])
        user_confirmed = UserConfirmation.objects.filter(user_id=self.id)
        if user_confirmed:
            user_confirmed.update(code=code, verify_type=verify_type)
            if verify_type == VIA_PHONE:
                user_confirmed.update(expiration_time=datetime.datetime.now() + datetime.timedelta(minutes=2))
            elif verify_type == VIA_EMAIL:
                user_confirmed.update(expiration_time=datetime.datetime.now() + datetime.timedelta(minutes=5))
        else:
            UserConfirmation.objects.create(
                user_id=self.id,
                code=code,
                verify_type=verify_type
            ).save()
        return code

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserConfirmation(BaseModel):
    VERIFY_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verify_code')
    code = models.CharField(max_length=4, null=True, blank=True)
    expiration_time = models.DateTimeField(null=True, blank=True)
    verify_type = models.CharField(max_length=10, choices=VERIFY_TYPE)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.__str__()} - {self.is_confirmed}"

    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        elif self.verify_type == VIA_PHONE:
            self.expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
        super(UserConfirmation, self).save(*args, **kwargs)

