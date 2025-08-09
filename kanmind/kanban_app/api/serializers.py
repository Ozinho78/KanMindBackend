from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from kanban_app.models import Board, Task, Comment

class RegistrationUserSerializer(serializers.ModelSerializer):
    """"""
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        account = User(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"]
        )
        account.set_password(validated_data["password"])
        account.save()
        return account


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            account = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "E-Mail-Adresse nicht gefunden."})

        account = authenticate(username=account.username, password=password)
        if not account:
            raise serializers.ValidationError({"password": "Falsches Passwort."})

        data["user"] = account
        return data

class UserShortSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True, allow_null=True)
    reviewer = UserShortSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "priority", "assignee", "reviewer", "due_date"]


class BoardListSerializer(serializers.ModelSerializer):
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
    owner_data = UserShortSerializer(source="owner", read_only=True)
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    members_data = UserShortSerializer(source="members", many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members", "members_data", "tasks"]
        read_only_fields = ["id", "owner_data", "members_data", "tasks"]


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ["id", "board", "title", "description", "status", "priority", "assignee_id", "reviewer_id", "due_date"]

    def create(self, validated_data):
        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        if assignee_id:
            validated_data["assignee"] = User.objects.filter(id=assignee_id).first()
        if reviewer_id:
            validated_data["reviewer"] = User.objects.filter(id=reviewer_id).first()

        return Task.objects.create(**validated_data)
    
    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        fullname = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return fullname or obj.author.username or obj.author.email

