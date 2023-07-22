from rest_framework import permissions


class UserPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            return True
        elif request.method == "PUT":
            if obj == request.user or request.user.is_staff:
                return True
        elif request.method == "DELETE":
            return request.user.is_staff
        else:
            return False


class OrderPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            if obj == request.user or request.user.is_staff:
                return True
        elif request.method == "DELETE":
            return request.user.is_staff
        else:
            return False
