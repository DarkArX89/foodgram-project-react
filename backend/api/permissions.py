from rest_framework import permissions


class AuthorOrAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return ((request.method in permissions.SAFE_METHODS
                 and len(request.query_params) == 0)
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_active
            and (obj.author == request.user
                 or request.user.is_staff
                 or request.user.is_superuser)
        )
