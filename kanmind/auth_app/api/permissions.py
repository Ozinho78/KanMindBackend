from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed


class IsBoardOwnerOrMember(BasePermission):
    """Allows access only for owner or members"""
    message = "Kein Zugriff auf dieses Board."

    def has_object_permission(self, request, view, obj):
        """Attributes needs to be checked to avoid unwanted error messages"""
        
        if hasattr(obj, "owner") and hasattr(obj, "members"):
            board = obj
            
        elif hasattr(obj, "board"):
            board = obj.board
            
        elif hasattr(obj, "task") and hasattr(obj.task, "board"):
            board = obj.task.board
        else:
            raise AuthenticationFailed(self.message)

        if board.owner == request.user or request.user in board.members.all():
            return True

        raise AuthenticationFailed(self.message)

