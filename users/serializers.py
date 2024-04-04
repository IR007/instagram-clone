from rest_framework import serializers
from rest_framework.validators import ValidationError

from shared.utility import check_email_or_phone
from users.models import User, VIA_EMAIL, VIA_PHONE


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


