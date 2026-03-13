from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование и удаление только автору.

    Чтение (включая список) — всем.
    """

    def has_permission(self, request, view):
        """
        Разрешает GET, HEAD, OPTIONS всем.

        Остальные действия — только авторизованным.
        """
        if view.action in ["list", "retrieve"]:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Разрешает чтение всем, изменение — только автору."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthenticated(permissions.BasePermission):
    """Только для авторизованных пользователей."""

    def has_permission(self, request, view):
        """Разрешает только аутентифицированным пользователям."""
        return request.user and request.user.is_authenticated
