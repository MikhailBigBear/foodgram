"""
Модуль содержит кастомную модель пользователя и её менеджер.

Переопределяет стандартную модель User, используя email как USERNAME_FIELD.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .const import USER_FIRST_NAME_MAX_LENGTH, USER_LAST_NAME_MAX_LENGTH


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User.

    Переопределяет методы создания пользователя и суперпользователя,
    чтобы использовать email вместо username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя."""
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает суперпользователя."""
        extra_fields["is_staff"] = extra_fields.get("is_staff", True)
        extra_fields["is_superuser"] = extra_fields.get("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Суперпользователь должен иметь is_superuser=True."
            )

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        "Email",
        unique=True,
        help_text="Уникальный адрес электронной почты.",
    )
    first_name = models.CharField(
        "Имя", max_length=USER_FIRST_NAME_MAX_LENGTH, blank=True
    )
    last_name = models.CharField(
        "Фамилия", max_length=USER_LAST_NAME_MAX_LENGTH, blank=True
    )
    avatar = models.ImageField(
        upload_to="users/",
        null=True,
        blank=True,
        help_text="Фотография профиля.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Разрешает вход в систему.",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Персонал",
        help_text="Доступ к админ‑панели.",
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Суперпользователь",
        help_text="Полный доступ к системе.",
    )
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )
    last_login = models.DateTimeField(
        null=True, blank=True, verbose_name="Последний вход"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        """Метаданные модели."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_user_email")
        ]

    def get_by_natural_key(self, username):
        """Возвращает пользователя по его email."""
        return self.get(email=username)

    def __str__(self):
        """Возвращает краткое описание пользователя."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else ""

    def get_short_name(self):
        """Возвращает короткое имя пользователя."""
        return self.first_name.strip() if self.first_name else ""
