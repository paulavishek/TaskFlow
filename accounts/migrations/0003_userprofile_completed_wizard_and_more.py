# Generated by Django 5.2.3 on 2025-06-19 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_availability_schedule_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='completed_wizard',
            field=models.BooleanField(default=False, help_text='Whether user has completed the getting started wizard'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='wizard_completed_at',
            field=models.DateTimeField(blank=True, help_text='When user completed the getting started wizard', null=True),
        ),
    ]
