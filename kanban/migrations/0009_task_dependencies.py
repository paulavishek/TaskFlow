# Generated migration for task dependencies

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0008_task_last_risk_assessment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='parent_task',
            field=models.ForeignKey(blank=True, help_text='Parent task for this subtask', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subtasks', to='kanban.task'),
        ),
        migrations.AddField(
            model_name='task',
            name='related_tasks',
            field=models.ManyToManyField(blank=True, help_text='Tasks that are related but not parent-child', related_name='related_to', to='kanban.task'),
        ),
        migrations.AddField(
            model_name='task',
            name='dependency_chain',
            field=models.JSONField(blank=True, default=list, help_text='Ordered list of task IDs showing complete dependency chain'),
        ),
        migrations.AddField(
            model_name='task',
            name='suggested_dependencies',
            field=models.JSONField(blank=True, default=list, help_text='AI-suggested task dependencies based on description analysis'),
        ),
        migrations.AddField(
            model_name='task',
            name='last_dependency_analysis',
            field=models.DateTimeField(blank=True, help_text='When AI last analyzed this task for dependency suggestions', null=True),
        ),
    ]
