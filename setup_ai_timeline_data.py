#!/usr/bin/env python
"""
Script to enhance existing TaskFlow data with AI timeline features
This will add dependencies, estimated durations, and timeline data to test the AI features
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from kanban.models import Board, Task, Column
from django.contrib.auth.models import User

def create_sample_timeline_data():
    """Add timeline data and dependencies to existing tasks"""
    
    print("🚀 Enhancing TaskFlow data with AI timeline features...")
    
    # Focus on the Software Project board (ID: 2) as it has the most tasks
    try:
        software_board = Board.objects.get(id=2)
        print(f"✅ Found board: {software_board.name}")
    except Board.DoesNotExist:
        print("❌ Software Project board not found!")
        return
    
    # Get all tasks from this board
    tasks = Task.objects.filter(column__board=software_board).order_by('id')
    print(f"📋 Found {tasks.count()} tasks in {software_board.name}")
    
    if tasks.count() == 0:
        print("❌ No tasks found!")
        return
    
    # Convert tasks to list for easier manipulation
    task_list = list(tasks)
    
    # Add estimated durations and start dates
    print("\n⏱️ Adding estimated durations and timeline data...")
    
    base_date = timezone.now().date()
    current_date = base_date
    
    for i, task in enumerate(task_list):
        # Add estimated duration (4-40 hours based on complexity)
        duration_hours = random.choice([4, 8, 12, 16, 20, 24, 32, 40])
        task.estimated_duration_hours = duration_hours
        
        # Add estimated start date
        task.estimated_start_date = timezone.make_aware(
            datetime.combine(current_date, datetime.min.time())
        )
        
        # Add some milestone tasks
        if i % 7 == 0:  # Every 7th task is a milestone
            task.is_milestone = True
            task.estimated_duration_hours = 4  # Milestones are shorter
        
        # Simulate some tasks that have started
        if task.progress > 0:
            task.actual_start_date = task.estimated_start_date
            # Add some actual duration based on progress
            task.actual_duration_hours = int(duration_hours * (task.progress / 100))
        
        task.save()
        print(f"  ✅ {task.title[:50]}... | {duration_hours}h | Milestone: {task.is_milestone}")
        
        # Increment date for next task (not all tasks start on same day)
        if i % 3 == 0:  # Every 3rd task starts on a new day
            current_date += timedelta(days=1)
    
    print(f"\n🔗 Creating task dependencies...")
    
    # Create logical dependencies
    dependencies_created = 0
    
    # Group tasks by column to create realistic dependencies
    columns = Column.objects.filter(board=software_board).order_by('position')
    
    for i, column in enumerate(columns):
        column_tasks = list(Task.objects.filter(column=column))
        
        if i > 0:  # Tasks in later columns depend on earlier columns
            prev_column = columns[i-1]
            prev_column_tasks = list(Task.objects.filter(column=prev_column))
            
            # Each task in current column depends on 1-2 tasks from previous column
            for task in column_tasks:
                # Randomly select 1-2 predecessor tasks
                num_predecessors = random.randint(1, min(2, len(prev_column_tasks)))
                predecessors = random.sample(prev_column_tasks, num_predecessors)
                
                for pred in predecessors:
                    task.predecessors.add(pred)
                    dependencies_created += 1
                    print(f"  🔗 {pred.title[:30]}... → {task.title[:30]}...")
        
        # Also create some dependencies within the same column
        if len(column_tasks) > 1:
            for j in range(1, len(column_tasks)):
                # 30% chance to depend on previous task in same column
                if random.random() < 0.3:
                    column_tasks[j].predecessors.add(column_tasks[j-1])
                    dependencies_created += 1
                    print(f"  🔗 {column_tasks[j-1].title[:30]}... → {column_tasks[j].title[:30]}...")
    
    print(f"\n✅ Created {dependencies_created} task dependencies")
    
    # Add some high-priority tasks to test risk assessment
    high_priority_tasks = Task.objects.filter(
        column__board=software_board, 
        priority__in=['high', 'urgent']
    )
    
    print(f"\n⚠️ Setting up risk scenarios for {high_priority_tasks.count()} high-priority tasks...")
    
    for task in high_priority_tasks:
        # Add longer durations to high-priority tasks to create potential bottlenecks
        task.estimated_duration_hours = max(task.estimated_duration_hours, 24)
        
        # Some high-priority tasks are overdue
        if random.random() < 0.4:  # 40% chance
            task.due_date = timezone.now() - timedelta(days=random.randint(1, 5))
        
        task.save()
        print(f"  ⚠️ Risk scenario: {task.title[:50]}...")
    
    print(f"\n🎯 Summary:")
    print(f"  📊 Enhanced {tasks.count()} tasks with timeline data")
    print(f"  🔗 Created {dependencies_created} task dependencies") 
    print(f"  🏁 Added {Task.objects.filter(column__board=software_board, is_milestone=True).count()} milestone tasks")
    print(f"  ⚠️ Configured {high_priority_tasks.count()} high-risk tasks")
    
    print(f"\n🚀 Ready to test AI features!")
    print(f"  🌐 Visit: http://localhost:8000/boards/{software_board.id}/analytics/")
    print(f"  🧠 Click 'Critical Path' and 'Timeline View' buttons to test AI analysis")

if __name__ == "__main__":
    create_sample_timeline_data()
