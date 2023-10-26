from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdminReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.borrowing.user == request.user or request.user.is_staff
