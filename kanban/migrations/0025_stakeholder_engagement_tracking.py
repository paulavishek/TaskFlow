# kanban/migrations/0025_stakeholder_engagement_tracking.py
"""
Migration for Stakeholder Engagement Tracking integration
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0010_resourcedemandforecast_teamcapacityalert_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create ProjectStakeholder model
        migrations.CreateModel(
            name='ProjectStakeholder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Stakeholder name', max_length=100)),
                ('role', models.CharField(help_text="Role/Title of stakeholder", max_length=100)),
                ('organization', models.CharField(blank=True, help_text='Organization/Department', max_length=100)),
                ('email', models.EmailField(blank=True, help_text='Contact email', max_length=254)),
                ('phone', models.CharField(blank=True, help_text='Contact phone', max_length=20)),
                ('influence_level', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', help_text="Stakeholder's level of influence on project", max_length=10)),
                ('interest_level', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', help_text="Stakeholder's level of interest in project", max_length=10)),
                ('current_engagement', models.CharField(choices=[('inform', 'Inform'), ('consult', 'Consult'), ('involve', 'Involve'), ('collaborate', 'Collaborate'), ('empower', 'Empower')], default='inform', help_text='Current engagement level with stakeholder', max_length=20)),
                ('desired_engagement', models.CharField(choices=[('inform', 'Inform'), ('consult', 'Consult'), ('involve', 'Involve'), ('collaborate', 'Collaborate'), ('empower', 'Empower')], default='involve', help_text='Desired engagement level for this stakeholder', max_length=20)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about stakeholder')),
                ('is_active', models.BooleanField(default=True, help_text='Whether stakeholder is still active on project')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('board', models.ForeignKey(help_text='Project/Board this stakeholder is associated with', on_delete=django.db.models.deletion.CASCADE, related_name='stakeholders', to='kanban.board')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_stakeholders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Create StakeholderTag model
        migrations.CreateModel(
            name='StakeholderTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Tag name', max_length=50)),
                ('color', models.CharField(default='#808080', help_text='Hex color code for tag display', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stakeholder_tags', to='kanban.board')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_stakeholder_tags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Create StakeholderTaskInvolvement model
        migrations.CreateModel(
            name='StakeholderTaskInvolvement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('involvement_type', models.CharField(choices=[('owner', 'Task Owner'), ('contributor', 'Contributor'), ('reviewer', 'Reviewer'), ('stakeholder', 'Stakeholder'), ('beneficiary', 'Beneficiary'), ('impacted', 'Impacted')], default='stakeholder', help_text='Type of stakeholder involvement in task', max_length=20)),
                ('engagement_status', models.CharField(choices=[('not_engaged', 'Not Engaged'), ('informed', 'Informed'), ('consulted', 'Consulted'), ('involved', 'Involved'), ('collaborated', 'Collaborated'), ('satisfied', 'Satisfied')], default='not_engaged', help_text='Current engagement status', max_length=20)),
                ('engagement_count', models.IntegerField(default=0, help_text='Number of times engaged on this task')),
                ('last_engagement', models.DateTimeField(blank=True, help_text='Last engagement timestamp', null=True)),
                ('satisfaction_rating', models.IntegerField(blank=True, choices=[(1, '1 - Very Dissatisfied'), (2, '2 - Dissatisfied'), (3, '3 - Neutral'), (4, '4 - Satisfied'), (5, '5 - Very Satisfied')], help_text='Stakeholder satisfaction with task outcome', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('feedback', models.TextField(blank=True, help_text='Stakeholder feedback on task')),
                ('concerns', models.TextField(blank=True, help_text='Any concerns or issues raised')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional tracking data (involvement dates, channels, etc.)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('stakeholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_involvements', to='kanban.projectstakeholder')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stakeholder_involvements', to='kanban.task')),
            ],
            options={
                'ordering': ['-last_engagement'],
            },
        ),
        
        # Create StakeholderEngagementRecord model
        migrations.CreateModel(
            name='StakeholderEngagementRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, help_text='Date of engagement')),
                ('description', models.TextField(help_text='Description of engagement activity')),
                ('communication_channel', models.CharField(choices=[('email', 'Email'), ('phone', 'Phone Call'), ('meeting', 'In-Person Meeting'), ('video', 'Video Call'), ('chat', 'Chat/Messaging'), ('presentation', 'Presentation'), ('survey', 'Survey'), ('other', 'Other')], default='email', help_text='How stakeholder was engaged', max_length=20)),
                ('outcome', models.TextField(blank=True, help_text='Outcome or results of engagement')),
                ('follow_up_required', models.BooleanField(default=False, help_text='Whether follow-up is needed')),
                ('follow_up_date', models.DateField(blank=True, help_text='Date for follow-up', null=True)),
                ('follow_up_completed', models.BooleanField(default=False, help_text='Whether follow-up was completed')),
                ('engagement_sentiment', models.CharField(choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative')], default='neutral', help_text='Sentiment of stakeholder after engagement', max_length=20)),
                ('satisfaction_rating', models.IntegerField(blank=True, choices=[(1, '1 - Very Dissatisfied'), (2, '2 - Dissatisfied'), (3, '3 - Neutral'), (4, '4 - Satisfied'), (5, '5 - Very Satisfied')], help_text='Engagement satisfaction rating', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes about engagement')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagement_records_created', to=settings.AUTH_USER_MODEL)),
                ('stakeholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagement_records', to='kanban.projectstakeholder')),
                ('task', models.ForeignKey(blank=True, help_text='Task associated with this engagement (optional)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stakeholder_engagement_records', to='kanban.task')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        
        # Create EngagementMetrics model
        migrations.CreateModel(
            name='EngagementMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_engagements', models.IntegerField(default=0, help_text='Total number of engagements')),
                ('engagements_this_month', models.IntegerField(default=0, help_text='Engagements in current month')),
                ('engagements_this_quarter', models.IntegerField(default=0, help_text='Engagements in current quarter')),
                ('average_engagements_per_month', models.DecimalField(decimal_places=2, default=0, help_text='Average engagements per month', max_digits=5)),
                ('primary_channel', models.CharField(blank=True, help_text='Most frequently used communication channel', max_length=20)),
                ('channels_used', models.JSONField(blank=True, default=list, help_text='List of communication channels used with counts')),
                ('average_satisfaction', models.DecimalField(decimal_places=2, default=0, help_text='Average satisfaction rating (1-5)', max_digits=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('positive_engagements_count', models.IntegerField(default=0, help_text='Number of positive engagements')),
                ('negative_engagements_count', models.IntegerField(default=0, help_text='Number of negative engagements')),
                ('days_since_last_engagement', models.IntegerField(default=0, help_text='Days since last engagement')),
                ('pending_follow_ups', models.IntegerField(default=0, help_text='Number of pending follow-ups')),
                ('engagement_gap', models.IntegerField(default=0, help_text='Gap between desired and current engagement level')),
                ('calculated_at', models.DateTimeField(auto_now=True)),
                ('period_start', models.DateField(help_text='Start date for metrics period')),
                ('period_end', models.DateField(help_text='End date for metrics period')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='engagement_metrics', to='kanban.board')),
                ('stakeholder', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='kanban.projectstakeholder')),
            ],
            options={
                'ordering': ['-calculated_at'],
            },
        ),
        
        # Create ProjectStakeholderTag through model
        migrations.CreateModel(
            name='ProjectStakeholderTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stakeholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kanban.projectstakeholder')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kanban.StakeholderTag')),
            ],
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='stakeholdertag',
            unique_together={('board', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='stakeholdertaskinvolvement',
            unique_together={('stakeholder', 'task')},
        ),
        migrations.AlterUniqueTogether(
            name='projectstakeholdertag',
            unique_together={('stakeholder', 'tag')},
        ),
    ]
