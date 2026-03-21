"""Модуль содержит пользовательские разрешения (permissions) для API."""

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование и удаление только автору.

    Чтение (GET, HEAD, OPTIONS) — всем.
    Запись - (POST, PUT, PATH, DELETE) - авторизованным пользователям.
    Изменение - только автору.
    """

    def has_permission(self, request, view):
        """
        Проверяет разрешение на уровне действия.

        Доступ к списку и деталям разрешён всем.
        Другие действия требуют аутентификации.
        """
        if view.action in ["list", "retrieve"]:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Проверяет разрешение на уровне объекта.

        Автор может редактировать/удалять. Остальные — только читать.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthenticated(permissions.BasePermission):
    """Доступ только для авторизованных пользователей."""

    def has_permission(self, request, view):
        """Проверяет что пользователь аутентифицирован."""
        return request.user and request.user.is_authenticated
