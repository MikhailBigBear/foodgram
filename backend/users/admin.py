from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Административная панель для управления пользователями.

    Позволяет:
    - просматривать список пользователей с основными полями;
    - фильтровать и искать пользователей;
    - массово активировать/деактивировать пользователей;
    - редактировать поля пользователя.
    """

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active")
    ordering = ("email",)
    list_editable = ("is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("email", "first_name", "last_name")}),
    )
    ordering = ("email",)
    readonly_fields = ("date_joined", "last_login")

    @admin.action(description="Активировать пользователей")
    def activate_users(self, request, queryset):
        """Активирует выбранных пользователей."""
        queryset.update(is_active=True)
        self.message_user(request, "Выбранные пользователи активированы")

    @admin.action(description="Деактивировать пользователей")
    def deactivate_users(self, request, queryset):
        """Деактивирует выбранных пользователей."""
        queryset.update(is_active=False)
        self.message_user(request, "Выбранные пользователи деактивированы")
