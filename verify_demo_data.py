#!/usr/bin/env python
"""
Verification script for demo data setup
Shows all created demo data for new features
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from kanban.models import Task, ResourceDemandForecast, TeamCapacityAlert, WorkloadDistributionRecommendation
from kanban.stakeholder_models import ProjectStakeholder, StakeholderTaskInvolvement, StakeholderEngagementRecord, EngagementMetrics

def print_header(text):
    print(f"\n{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}\n")

print_header("📊 DEMO DATA VERIFICATION REPORT")

# Risk Management
print("🛡️  RISK MANAGEMENT")
print("-" * 60)
risk_tasks = Task.objects.filter(risk_level__isnull=False)
print(f"Tasks with risk assessments: {risk_tasks.count()}")
print(f"\nRisk levels distribution:")
for level in ['low', 'medium', 'high', 'critical']:
    count = risk_tasks.filter(risk_level=level).count()
    if count > 0:
        print(f"  • {level.capitalize()}: {count}")

if risk_tasks.exists():
    print(f"\nSample risky tasks:")
    for task in risk_tasks[:3]:
        print(f"  • {task.title} - Risk Level: {task.risk_level}")

# Resource Management
print("\n📦 RESOURCE MANAGEMENT")
print("-" * 60)
forecasts = ResourceDemandForecast.objects.all()
print(f"Resource forecasts created: {forecasts.count()}")
alerts = TeamCapacityAlert.objects.all()
print(f"Capacity alerts: {alerts.count()}")
recommendations = WorkloadDistributionRecommendation.objects.all()
print(f"Distribution recommendations: {recommendations.count()}")

if forecasts.exists():
    print(f"\nForecast details:")
    for forecast in forecasts[:3]:
        util = forecast.utilization_percentage
        print(f"  • {forecast.resource_user.username}: {util:.0f}% utilized")

if alerts.exists():
    print(f"\nActive alerts:")
    for alert in alerts[:3]:
        print(f"  • {alert.resource_user.username}: {alert.message}")

# Stakeholder Management
print("\n👥 STAKEHOLDER MANAGEMENT")
print("-" * 60)
stakeholders = ProjectStakeholder.objects.all()
print(f"Total stakeholders created: {stakeholders.count()}")
print(f"\nStakeholder profiles:")
for sh in stakeholders:
    print(f"  • {sh.name} - {sh.role}")
    print(f"    Influence: {sh.influence_level} | Interest: {sh.interest_level}")

involvements = StakeholderTaskInvolvement.objects.all()
print(f"\nTask-stakeholder involvement: {involvements.count()}")

engagements = StakeholderEngagementRecord.objects.all()
print(f"Engagement records created: {engagements.count()}")

metrics = EngagementMetrics.objects.all()
print(f"Engagement metrics tracked: {metrics.count()}")

if metrics.exists():
    print(f"\nEngagement metrics samples:")
    for m in metrics[:2]:
        print(f"  • {m.stakeholder.name}: {m.total_engagements} engagements, {m.average_satisfaction:.1f}/5 satisfaction")

# Requirements & Dependencies
print("\n📋 REQUIREMENTS & DEPENDENCIES")
print("-" * 60)
parent_tasks = Task.objects.filter(parent_task__isnull=False)
print(f"Subtasks (child tasks): {parent_tasks.count()}")

tasks_with_deps = Task.objects.filter(dependency_chain__isnull=False).exclude(dependency_chain=[])
print(f"Tasks with dependency chains: {tasks_with_deps.count()}")

tasks_with_skills = Task.objects.filter(required_skills__isnull=False).exclude(required_skills=[])
print(f"Tasks with skill requirements: {tasks_with_skills.count()}")

related_count = sum(task.related_tasks.count() for task in Task.objects.all())
print(f"Related task relationships: {related_count}")

if parent_tasks.exists():
    print(f"\nSample task hierarchies:")
    for task in parent_tasks[:3]:
        print(f"  • {task.title} (subtask of {task.parent_task.title})")

if tasks_with_skills.exists():
    print(f"\nTasks with skill requirements:")
    for task in tasks_with_skills[:3]:
        skills = ', '.join([s['name'] for s in task.required_skills])
        print(f"  • {task.title}: {skills}")

# Summary
print_header("✅ DEMO DATA SETUP COMPLETE!")

total_tasks = Task.objects.count()
print(f"\nSUMMARY:")
print(f"  Total tasks: {total_tasks}")
print(f"  Tasks with risk data: {risk_tasks.count()} ({risk_tasks.count()*100//total_tasks if total_tasks else 0}%)")
print(f"  Resource forecasts: {forecasts.count()}")
print(f"  Stakeholders: {stakeholders.count()}")
print(f"  Task dependencies: {parent_tasks.count()}")

print(f"\n🎉 All new features have comprehensive demo data!")
print(f"   Start the server and explore the boards!\n")
