from rest_framework.permissions import BasePermission
    
class AdminOrUserPermissions (BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.FileOwner:
            return True
        return request.user.is_staff

class AdminOrUserForUserViewSetPermissions (BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True
        return request.user.is_staff