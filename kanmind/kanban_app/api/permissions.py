from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

class IsBoardOwnerOrMember(BasePermission):
    """Allows access only for owner or members"""
    message = "Kein Zugriff auf dieses Board."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Anmeldung erforderlich.")
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Anmeldung erforderlich.")

        if hasattr(obj, "owner") and hasattr(obj, "members"):
            board = obj
        elif hasattr(obj, "board"):
            board = obj.board
        elif hasattr(obj, "task") and hasattr(obj.task, "board"):
            board = obj.task.board
        else:
            raise PermissionDenied(self.message)

        if board.owner_id == request.user.id or request.user in board.members.all():
            return True
        raise PermissionDenied(self.message)