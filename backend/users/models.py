from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Кастомный менеджер."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields["is_staff"] = extra_fields.get("is_staff", True)
        extra_fields["is_superuser"] = extra_fields.get("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField("Email", unique=True)
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    avatar = models.ImageField(upload_to="users/", null=True, blank=True)
    is_active = models.BooleanField(
        default=True, verbose_name="Активен", help_text="Разрешает вход в систему."
    )
    is_staff = models.BooleanField(
        default=False, verbose_name="Персонал", help_text="Доступ к админ‑панели."
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
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_user_email")
        ]

    def get_by_natural_key(self, username):
        return self.get(email=username)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else ""

    def get_short_name(self):
        return self.first_name.strip() if self.first_name else ""
