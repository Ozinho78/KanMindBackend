from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

class IsBoardOwnerOrMember(BasePermission):
    """Allows access only for owner or members"""
    message = "Kein Zugriff auf dieses Board."

    def has_permission(self, request, view):
        # if not logged in 401
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Anmeldung erforderlich.")
        return True

    def has_object_permission(self, request, view, obj):
        # double check for direct request
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Anmeldung erforderlich.")

        # Determination of board (Board | Task | Comment)
        if hasattr(obj, "owner") and hasattr(obj, "members"):
            board = obj
        elif hasattr(obj, "board"):
            board = obj.board
        elif hasattr(obj, "task") and hasattr(obj.task, "board"):
            board = obj.task.board
        else:
            # object doesn't fit to the scheme → handle as missing permission 403
            raise PermissionDenied(self.message)

        # if logged in but not owner or member 403
        if board.owner_id == request.user.id or request.user in board.members.all():
            return True
        raise PermissionDenied(self.message)