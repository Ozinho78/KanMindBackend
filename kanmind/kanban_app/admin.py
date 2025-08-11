from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from kanban_app.models import Board, Task, Comment

User = get_user_model()


admin.site.site_header = "KanMind Admin"
admin.site.site_title = "KanMind Admin"
admin.site.index_title = "Übersicht"


class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        board = cleaned.get("board") or getattr(self.instance, "board", None)
        assignee = cleaned.get("assignee")
        reviewer = cleaned.get("reviewer")

        if board:
            allowed_ids = set(board.members.values_list("id", flat=True)) | {board.owner_id}
            if assignee and assignee.id not in allowed_ids:
                self.add_error("assignee", "Assignee ist kein Mitglied/Owner dieses Boards.")
            if reviewer and reviewer.id not in allowed_ids:
                self.add_error("reviewer", "Reviewer ist kein Mitglied/Owner dieses Boards.")
        return cleaned
    
    
class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        task = cleaned.get("task") or getattr(self.instance, "task", None)
        author = cleaned.get("author")

        if task and author:
            board = getattr(task, "board", None)
            if board:
                allowed_ids = set(board.members.values_list("id", flat=True)) | {board.owner_id}
                if author.id not in allowed_ids:
                    self.add_error("author", "Autor ist kein Mitglied/Owner dieses Boards.")
        return cleaned


class TaskInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        board = self.instance
        if not board:
            return
        allowed_ids = set(board.members.values_list("id", flat=True)) | {board.owner_id}

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE", False):
                continue

            assignee = form.cleaned_data.get("assignee")
            reviewer = form.cleaned_data.get("reviewer")

            if assignee and assignee.id not in allowed_ids:
                form.add_error("assignee", "Assignee ist kein Mitglied/Owner dieses Boards.")
            if reviewer and reviewer.id not in allowed_ids:
                form.add_error("reviewer", "Reviewer ist kein Mitglied/Owner dieses Boards.")


class CommentInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        task = self.instance            # Parent-Objekt = Task
        board = getattr(task, "board", None)
        if not board:
            return

        allowed_ids = set(board.members.values_list("id", flat=True)) | {board.owner_id}
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE", False):
                continue
            author = form.cleaned_data.get("author")
            if author and author.id not in allowed_ids:
                form.add_error("author", "Autor ist kein Mitglied/Owner dieses Boards.")


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ("title", "status", "priority", "assignee", "reviewer", "due_date")
    autocomplete_fields = ("assignee", "reviewer")
    formset = TaskInlineFormSet
    form = TaskAdminForm

    def get_formset(self, request, obj=None, **kwargs):
        self._parent_board = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ("assignee", "reviewer"):
            board = getattr(self, "_parent_board", None)
            if board:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                allowed_ids = set(board.members.values_list("id", flat=True)) | {board.owner_id}
                kwargs["queryset"] = User.objects.filter(id__in=allowed_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author", "content", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)

    # NEU:
    formset = CommentInlineFormSet
    form = CommentAdminForm

    def get_formset(self, request, obj=None, **kwargs):
        self._parent_task = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            task = getattr(self, "_parent_task", None)
            if task and getattr(task, "board", None):
                User = get_user_model()
                board = task.board
                allowed_ids = set(board.members.values_list("id", flat=True)) | {board.owner_id}
                kwargs["queryset"] = User.objects.filter(id__in=allowed_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "member_count",
        "ticket_count",
        "tasks_to_do_count",
        "tasks_high_prio_count",
    )
    search_fields = ("title", "owner__username", "owner__email")
    list_filter = ("owner",)
    autocomplete_fields = ("owner", "members")
    filter_horizontal = ("members",)
    inlines = [TaskInline]

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Mitglieder"

    def ticket_count(self, obj):
        return obj.tasks.count()
    ticket_count.short_description = "Tasks gesamt"

    def tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()
    tasks_to_do_count.short_description = "To Do"

    def tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
    tasks_high_prio_count.short_description = "High Prio"



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = (
        "id",
        "title",
        "board",
        "status",
        "priority",
        "assignee",
        "reviewer",
        "due_date",
        "comments_count",
    )
    list_filter = ("status", "priority", "board")
    search_fields = (
        "title",
        "description",
        "board__title",
        "assignee__username",
        "assignee__email",
        "reviewer__username",
        "reviewer__email",
    )
    autocomplete_fields = ("board", "assignee", "reviewer")
    inlines = [CommentInline]

    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = "Kommentare"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm
    list_display = ("id", "task", "author", "created_at", "short_content")
    list_filter = ("created_at", "author")
    search_fields = ("content", "task__title", "author__username", "author__email")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("task", "author")

    def short_content(self, obj):
        return (obj.content[:60] + "…") if len(obj.content) > 60 else obj.content
    short_content.short_description = "Inhalt"