from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'First_Name', 'Last_Name', 'user', 'public_key')


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
