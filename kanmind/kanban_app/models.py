from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """Model for board"""
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")
    members = models.ManyToManyField(User, related_name="member_boards", blank=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    """Model for task with predefined choices"""
    STATUS_CHOICES = [("to-do", "To Do"), ("in-progress", "In Progress"), ("review", "Review"), ("done", "Done"),]
    PRIORITY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High"),]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="review_tasks")
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    
class Comment(models.Model):
    """Model for comment"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=600)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"