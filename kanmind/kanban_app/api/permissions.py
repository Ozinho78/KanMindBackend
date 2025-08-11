from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import PermissionDenied


class IsBoardOwnerOrMember(BasePermission):
    """Allows access only for owner or members"""
    message = "Kein Zugriff auf dieses Board."

    def has_object_permission(self, request, view, obj):
        """Attributes needs to be checked to avoid unwanted error messages"""
        
        # Determine board object (Board | Task | Comment)
        # Attributes for board
        if hasattr(obj, "owner") and hasattr(obj, "members"):
            board = obj
            
        # Attributes for task
        elif hasattr(obj, "board"):
            board = obj.board
            
        # Attributes for comment
        elif hasattr(obj, "task") and hasattr(obj.task, "board"):
            board = obj.task.board
        else:
            # raise AuthenticationFailed(self.message)
            raise PermissionDenied(self.message)

        # Allow access if the user is the owner or member of the board
        if board.owner == request.user or request.user in board.members.all():
            return True

        # Logged in but no access
        # raise AuthenticationFailed(self.message)
        # Why fail if you can deny someone
        raise PermissionDenied(self.message)
