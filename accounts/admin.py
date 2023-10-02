from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.forms import CustomUserCreationForm, CustomUserChangeForm
from accounts.models import Org, User, Account, AccountApiToken


@admin.register(Org)
class OrgAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "created_at",
    ]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "created_at",
        "owner",
    ]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("email", "org", "account", "is_staff", "is_active",)
    list_filter = ("email", "org", "account", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
        ("org", {"fields": ("org", "account",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions", "org", "account",
            )}
         ),
    )
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(AccountApiToken)
class AccountApiTokenAdmin(admin.ModelAdmin):
    list_display = [
        "key",
        "account",
        "created_by",
        "created_at",
    ]
    search_fields = ("account",)
    list_filter = ("created_by", "account",)
    fieldsets = (
        (None, {"fields": ("account", "created_by")}),
    )
