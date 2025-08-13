from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from rest_framework import serializers
from kanban_app.models import Board, Task, Comment


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "fullname")


class UserShortSerializer(serializers.ModelSerializer):
    """Serializes user with full name"""
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TaskSerializer(serializers.ModelSerializer):
    board = serializers.ReadOnlyField(source="board.id")
    assignee = UserShortSerializer(read_only=True, allow_null=True)
    reviewer = UserShortSerializer(read_only=True, allow_null=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]
        
    def get_comments_count(self, obj):
        val = getattr(obj, "comments_count", None)
        if val is not None:
            return val
        return obj.comments.count()
        

class TaskInBoardSerializer(serializers.ModelSerializer):
    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        val = getattr(obj, "comments_count", None)
        if val is not None:
            return int(val)
        return obj.comments.count()

    class Meta:
        model = Task
        fields = (
            "id", "title", "description", "status", "priority",
            "assignee", "reviewer", "due_date", "comments_count",
        )
        
        
class TaskWriteSerializer(serializers.ModelSerializer):
    """Serializes and validates new and updated task"""
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ["id", "board", "title", "description", "status", "priority",
                  "assignee_id", "reviewer_id", "due_date"]

    def _get_allowed_user_ids(self, board: Board):
        return list(board.members.values_list("id", flat=True)) + [board.owner_id]

    def validate(self, attrs):
        board = attrs.get("board") or getattr(self.instance, "board", None)
        if board is None:
            raise serializers.ValidationError({"board": "Dieses Feld wird benötigt."})

        allowed = set(self._get_allowed_user_ids(board))

        assignee_id = attrs.pop("assignee_id", serializers.empty)
        reviewer_id = attrs.pop("reviewer_id", serializers.empty)

        errors = {}

        if assignee_id is not serializers.empty:
            if assignee_id is None:
                attrs["assignee"] = None
            elif assignee_id not in allowed:
                errors["assignee_id"] = "Assignee ist kein Mitglied dieses Boards."
            else:
                attrs["assignee"] = User.objects.filter(id=assignee_id).first()

        if reviewer_id is not serializers.empty:
            if reviewer_id is None:
                attrs["reviewer"] = None
            elif reviewer_id not in allowed:
                errors["reviewer_id"] = "Reviewer ist kein Mitglied dieses Boards."
            else:
                attrs["reviewer"] = User.objects.filter(id=reviewer_id).first()

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """Serializes and validates board list"""
    owner_id = serializers.ReadOnlyField(source="owner.id")
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False, write_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "members", "member_count", "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", "owner_id"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        board = Board.objects.create(**validated_data)
        if members:
            board.members.set(members)
        return board

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializes and validates board detail"""
    owner_id = serializers.ReadOnlyField(source="owner.id")
    members = UserShortSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]
        
        
class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializes for PUT/PATCH in boards"""
    owner_data = UserShortSerializer(source="owner", read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    members_data = UserShortSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members", "members_data"]
        read_only_fields = ["id", "owner_data", "members_data"]

    def update(self, instance, validated_data):
        title = validated_data.get("title", None)
        if title is not None:
            instance.title = title
            instance.save()

        if "members" in validated_data:
            members = validated_data.pop("members", [])
            instance.members.set(members)

        return instance


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializes and validates comment creation"""
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        fullname = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return fullname or obj.author.username or obj.author.email

    def validate_content(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Darf nicht leer sein.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        task = self.context["task"]
        return Comment.objects.create(task=task, author=request.user, **validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializes and validates comment, read-only"""
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        fullname = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return fullname or obj.author.username or obj.author.email
