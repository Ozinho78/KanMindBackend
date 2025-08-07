from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed

class IsBoardOwnerOrMember(BasePermission):
    """Allows access only for owner or members"""
    message = "Kein Zugriff auf dieses Board."

    def has_object_permission(self, request, view, obj):
        """If it's a task object -> access over Board"""
        if hasattr(obj, "board"):
            board = obj.board
        else:
            board = obj

        if board.owner == request.user or request.user in board.members.all():
            return True

        raise AuthenticationFailed(self.message)



# class IsBoardOwnerOrMember(BasePermission):
#     """Allows access only for owner or members"""
#     message = "Kein Zugriff auf dieses Board."

#     def has_object_permission(self, request, view, obj):
#         if obj.owner == request.user or request.user in obj.members.all():
#             return True
#         raise AuthenticationFailed(self.message)