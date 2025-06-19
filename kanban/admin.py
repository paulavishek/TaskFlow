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
    list_display = ('title', 'column', 'priority', 'due_date', 'assigned_to', 'is_milestone', 'is_critical_path', 'created_by')
    list_filter = ('column', 'priority', 'due_date', 'is_milestone', 'is_critical_path', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('labels', 'predecessors')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'column', 'assigned_to', 'priority', 'progress', 'labels')
        }),
        ('Timeline & Dependencies', {
            'fields': ('due_date', 'estimated_start_date', 'estimated_duration_hours', 
                      'actual_start_date', 'actual_duration_hours', 'is_milestone', 'predecessors'),
            'classes': ('collapse',)
        }),
        ('AI Analysis Results', {
            'fields': ('earliest_start', 'earliest_finish', 'latest_start', 'latest_finish', 
                      'slack_time_hours', 'is_critical_path', 'ai_risk_score', 'ai_recommendations', 'last_ai_analysis'),
            'classes': ('collapse',),
            'description': 'These fields are automatically calculated by AI analysis'
        }),
    )
    
    readonly_fields = ('earliest_start', 'earliest_finish', 'latest_start', 'latest_finish', 
                      'slack_time_hours', 'is_critical_path', 'last_ai_analysis')

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
