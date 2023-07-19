from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .models import User


class UsersAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name',)
    list_filter = ('username', 'email',)
    ordering = ['id']


admin.site.register(User, UsersAdmin)
