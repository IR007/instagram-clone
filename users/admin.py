from django.contrib import admin

from .models import User, UserConfirmation


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'user_role', 'email', 'phone_number', 'gender']


class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ['user', 'verify_type', 'is_confirmed']


admin.site.register(User, UserAdmin)
admin.site.register(UserConfirmation, UserConfirmationAdmin)
