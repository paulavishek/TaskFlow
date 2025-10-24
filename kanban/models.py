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
      # AI Analysis Results
    ai_risk_score = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                      help_text="AI-calculated risk score (0-100)")
    ai_recommendations = models.TextField(blank=True, null=True, help_text="AI-generated recommendations for this task")
    last_ai_analysis = models.DateTimeField(blank=True, null=True, help_text="When AI last analyzed this task")
    
    # Smart Resource Analysis Fields
    required_skills = models.JSONField(
        default=list,
        blank=True,
        help_text="Required skills for this task (e.g., [{'name': 'Python', 'level': 'Intermediate'}])"
    )
    skill_match_score = models.IntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="AI-calculated skill match score for assigned user (0-100)"
    )
    optimal_assignee_suggestions = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-suggested optimal assignees with match scores"
    )
    workload_impact = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Impact'),
            ('medium', 'Medium Impact'),
            ('high', 'High Impact'),
            ('critical', 'Critical Impact'),
        ],
        default='medium',
        help_text="Impact on assignee's workload"
    )
    resource_conflicts = models.JSONField(
        default=list,
        blank=True,
        help_text="Identified resource conflicts and scheduling issues"
    )
    
    # Enhanced Resource Tracking    
    complexity_score = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Task complexity score (1-10)"  
    )
    collaboration_required = models.BooleanField(
        default=False,
        help_text="Does this task require collaboration with others?"
    )
    suggested_team_members = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-suggested team members for collaborative tasks"
    )
    
    # Risk Management Fields
    risk_likelihood = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')],
        help_text="Risk likelihood score (1=Low, 2=Medium, 3=High)"
    )
    risk_impact = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')],
        help_text="Risk impact score (1=Low, 2=Medium, 3=High)"
    )
    risk_score = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        help_text="AI-calculated risk score (Likelihood × Impact, range 1-9)"
    )
    risk_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        blank=True,
        null=True,
        help_text="AI-determined risk level classification"
    )
    risk_indicators = models.JSONField(
        default=list,
        blank=True,
        help_text="Key indicators to monitor for this risk (from AI analysis)"
    )
    mitigation_suggestions = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-generated mitigation strategies and action plans"
    )
    risk_analysis = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete AI risk analysis including reasoning and factors"
    )
    last_risk_assessment = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When AI last performed risk assessment for this task"
    )
    
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

class MeetingTranscript(models.Model):
    MEETING_TYPE_CHOICES = [
        ('standup', 'Daily Standup'),
        ('planning', 'Sprint Planning'),
        ('review', 'Review Meeting'),
        ('retrospective', 'Retrospective'),
        ('general', 'General Meeting'),
    ]
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    title = models.CharField(max_length=200, help_text="Meeting title or topic")
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='general')
    meeting_date = models.DateField(help_text="Date when the meeting occurred")
    transcript_text = models.TextField(help_text="Raw meeting transcript")
    transcript_file = models.FileField(upload_to='meeting_transcripts/', blank=True, null=True, 
                                     help_text="Uploaded transcript file")
    
    # Processing information
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='meeting_transcripts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_transcripts')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='pending')
    
    # AI extraction results
    extraction_results = models.JSONField(default=dict, blank=True, 
                                        help_text="AI extraction results including tasks and metadata")
    tasks_extracted_count = models.IntegerField(default=0)
    tasks_created_count = models.IntegerField(default=0)
    
    # Meeting context
    participants = models.JSONField(default=list, blank=True, 
                                  help_text="List of meeting participants")
    meeting_context = models.JSONField(default=dict, blank=True,
                                     help_text="Additional meeting context and metadata")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.meeting_date}"
