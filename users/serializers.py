from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import check_email_or_phone, send_email, send_phone
from users.models import User, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, DONE, PHOTO_STEP


class SignUpSerializer(serializers.ModelSerializer):
    auth_status = serializers.CharField(read_only=True, required=False)
    user_role = serializers.CharField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_or_phone'] = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'auth_type', 'auth_status', 'user_role']
        extra_kwargs = {
            'id': {
                'read_only': True,
                'required': False
            },
            'auth_type': {
                'read_only': True,
                'required': False
            }
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_phone(user.phone_number, code)
            user.save()
            # send_mail(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            # send_phone(user.phone_number, code)

        return user

    def validate(self, attrs):
        super(SignUpSerializer, self).validate(attrs)
        data = self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(attrs):
        email_or_phone = attrs.get('email_or_phone')
        auth_type = check_email_or_phone(email_or_phone)
        if auth_type == VIA_EMAIL:
            data = {
                'auth_type': VIA_EMAIL,
                'email': email_or_phone
            }
        elif auth_type == VIA_PHONE:
            data = {
                'auth_type': VIA_PHONE,
                'phone_number': email_or_phone
            }
        return data

    def validate_email_or_phone(self, email_or_phone):
        email_or_phone = email_or_phone.lower()
        if User.objects.filter(email=email_or_phone):
            data = "Bunday email manzilli foydalanuvchi mavjud!"
            raise ValidationError(data)
        elif User.objects.filter(phone_number=email_or_phone):
            data = "Bunday telefon raqamli foydalanuvchi mavjud!"
            raise ValidationError(data)
        return email_or_phone

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class VerifySerializer(serializers.Serializer):
    code = serializers.IntegerField(write_only=True, required=True)


class UserInfoUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    gender = serializers.CharField(max_length=10, required=False)
    bio = serializers.CharField(max_length=1000, required=False)
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        password_confirm = data.get('password_confirm', None)
        if password != password_confirm:
            data = {
                'success': False,
                'message': "Parollaringiz mos emas!"
            }
            raise ValidationError(data)
        if password:
            validate_password(password)
        return data

    def validate_username(self, username):
        if len(username) <= 4 or len(username) > 15:
            data = {
                'success': False,
                'message': 'Username xatolik'
            }
            raise ValidationError(data)
        else:
            if username.isdigit():
                data = {
                    'success': False,
                    'message': "Foydalanuvchi nomi sonlar bo'lmasligi kerak!"
                }
                raise ValidationError(data)
            user = User.objects.filter(username=username)
            if user:
                data = {
                    'success': False,
                    'message': 'Bunday foydalanuvchi nomli foydalanuvchi mavjud'
                }
                raise ValidationError(data)
        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.password = validated_data.get('password', instance.password)

        if instance.password:
            instance.set_password(validated_data.get('password'))
        if instance.auth_status in (CODE_VERIFIED, DONE, PHOTO_STEP):
            instance.auth_status = DONE
        else:
            data = {
                'success': False,
                'message': 'Sizga ruxsat yo\'q'
            }
            raise ValidationError(data)

        instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=35, required=True)


class RefreshTokenSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class UserPhotoChangeSerializer(serializers.Serializer):
    photo = serializers.ImageField(write_only=True, required=False,
                                   validators=[FileExtensionValidator(allowed_extensions=['jgp', 'png', 'jpeg', 'heic', 'heif'])])

    def update(self, instance, validated_data):
        instance.photo = validated_data.get('photo', None)
        if instance.auth_status in (DONE, PHOTO_STEP):
            instance.auth_status = PHOTO_STEP
        instance.save()
        return instance


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


