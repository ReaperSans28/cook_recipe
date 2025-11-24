from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Профиль",
            {"fields": ("headline", "bio", "is_instructor", "avatar")},
        ),
    )
    list_display = ("username", "email", "is_instructor", "is_staff", "is_active")
    list_filter = ("is_instructor", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
