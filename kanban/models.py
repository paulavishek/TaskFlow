from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
from accounts.models import Organization
from django.core.validators import MinValueValidator, MaxValueValidator

class Board(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='boards')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_boards')
    members = models.ManyToManyField(User, related_name='member_boards', blank=True)
    
    def __str__(self):
        return self.name

class Column(models.Model):
    name = models.CharField(max_length=100)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.name} - {self.board.name}"

class TaskLabel(models.Model):
    CATEGORY_CHOICES = [
        ('regular', 'Regular'),
        ('lean', 'Lean Six Sigma'),
    ]
    
    name = models.CharField(max_length=50)
    color = ColorField(default='#FF5733')
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='labels')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='regular')
    
    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='tasks')
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    labels = models.ManyToManyField(TaskLabel, related_name='tasks', blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"

class TaskActivity(models.Model):
    ACTIVITY_CHOICES = [
        ('created', 'Created'),
        ('moved', 'Moved'),
        ('assigned', 'Assigned'),
        ('updated', 'Updated'),
        ('commented', 'Commented'),
        ('label_added', 'Label Added'),
        ('label_removed', 'Label Removed'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Task Activities'
    
    def __str__(self):
        return f"{self.activity_type} by {self.user.username} on {self.task.title}"
