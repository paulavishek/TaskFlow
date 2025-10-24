from django.contrib import admin
from .models import Board, Column, Task, TaskLabel, Comment, TaskActivity

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('organization', 'created_at')

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'board', 'position')
    list_filter = ('board',)
    search_fields = ('name', 'board__name')

@admin.register(TaskLabel)
class TaskLabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'board')
    list_filter = ('board',)
    search_fields = ('name', 'board__name')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'column', 'priority', 'due_date', 'assigned_to', 'created_by', 'parent_task')
    list_filter = ('column', 'priority', 'due_date', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('labels', 'related_tasks')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'column', 'assigned_to', 'priority', 'progress', 'labels')
        }),
        ('Timeline', {
            'fields': ('due_date',),
        }),
        ('Task Dependencies', {
            'fields': ('parent_task', 'related_tasks', 'dependency_chain'),
            'classes': ('collapse',),
            'description': 'Manage task relationships and dependencies'
        }),
        ('AI-Suggested Dependencies', {
            'fields': ('suggested_dependencies', 'last_dependency_analysis'),
            'classes': ('collapse',),
            'description': 'AI analysis results for task dependencies'
        }),
        ('AI Analysis Results', {
            'fields': ('ai_risk_score', 'ai_recommendations', 'last_ai_analysis'),
            'classes': ('collapse',),
            'description': 'These fields are related to AI analysis'
        }),
    )
    
    readonly_fields = ('last_ai_analysis', 'last_dependency_analysis', 'dependency_chain')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'task__title', 'user__username')

@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'activity_type', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('description', 'task__title', 'user__username')
