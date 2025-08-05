from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class RegistrationUserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)

    def __str__(self):
        return self.fullname
    

class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_boards"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="member_boards",
        blank=True
    )

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review_tasks"
    )
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def comments_count(self):
        # Falls es ein Comment-Modell gibt:
        return self.comments.count() if hasattr(self, "comments") else 0