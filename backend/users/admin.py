from django.contrib import admin
from .models import User

admin.site.register(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Административная панель для управления пользователями.

    Позволяет:
    - просматривать список пользователей с основными полями;
    - фильтровать и искать пользователей;
    - массово активировать/деактивировать пользователей;
    - редактировать поля пользователя.

    Поля, отображаемые в таблице списка пользователей:
    - emai;
    - first_name: Имя пользователя;
    - last_name: Фамилия пользователя;
    - is_active: Статус учетной записи;
    - is_staff: Право доступа к админ-панели;
    - date_joined: Дата регистрации пользователя.
    """

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "date_joined", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    list_editable = ("is_active", "is_staff")
    fields = (
        (None, {"fields": ("email", "password")}),
        ("Персональные данные", {"fields": ("first_name", "last_name", "avatar")}),
        ("Права доступа", {"fields": ("is_active",)}),
        (
            "Важные даты",
            {"fields": ("last_login", "date_joined"), "class": ("collapse",)},
        ),
    )
    readonly_fields = ("last_login", "date_joined")
    list_per_page = 20
    actions = ["activate_users", "deactivate_users"]

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
