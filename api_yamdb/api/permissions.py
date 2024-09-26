from rest_framework import permissions


class AdminModerAuthorOrReadOnly(permissions.BasePermission):
    """Безопасные запросы разрешены всем.
    Небозопасные только автору поста, модератору или администратору."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)


class AllReadOrAuthAdminOnly(permissions.BasePermission):
    """Безопасные запросы разрешены всем.
    Небезопасные только авторизованному администратору."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or (
                request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser
                )
            )
        )


class AuthAdminOnly(permissions.BasePermission):
    """Все запросы разрешены только авторизованному администратору."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and (
                request.user.is_admin or request.user.is_superuser
            )
        )
