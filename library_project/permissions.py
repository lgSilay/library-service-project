from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsBorrowingOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.borrowing.user == request.user or request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.method in SAFE_METHODS and request.user)
            or (request.user and request.user.is_staff)
        )
