from kanban_app.models import Board


class UserBoardsQuerysetMixin:
    """Mixin for checking if user is owner or member of a specific board"""
    def get_queryset(self):
        account = self.request.user
        owned = Board.objects.filter(owner=account)
        member = Board.objects.filter(members=account)
        return (owned | member).distinct()