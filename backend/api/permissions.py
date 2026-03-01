from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешает только автору изменять/удалять объект.

    Для остальных — только чтение.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthenticated(permissions.BasePermission):
    """Только для авторизованных пользователей."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
