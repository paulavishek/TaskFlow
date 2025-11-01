"""
Script to add sample tasks with dates for testing the Gantt chart
Run this with: python manage.py shell < add_gantt_sample_data.py
"""
from datetime import date, timedelta
from django.contrib.auth.models import User
from kanban.models import Board, Column, Task

# Get the first user and first board
user = User.objects.first()
board = Board.objects.first()

if not board:
    print("No boards found. Please create a board first.")
    exit()

# Get or create columns
columns = list(Column.objects.filter(board=board))
if not columns:
    print("No columns found. Creating default columns...")
    todo_col = Column.objects.create(board=board, name="To Do", position=0)
    progress_col = Column.objects.create(board=board, name="In Progress", position=1)
    done_col = Column.objects.create(board=board, name="Done", position=2)
    columns = [todo_col, progress_col, done_col]

# Sample tasks with dates for Gantt chart
today = date.today()

sample_tasks = [
    {
        'title': 'Project Planning',
        'description': 'Define project scope and requirements',
        'start_date': today,
        'due_date': today + timedelta(days=5),
        'progress': 80,
        'column': columns[1],  # In Progress
        'priority': 'high'
    },
    {
        'title': 'Design Database Schema',
        'description': 'Create database models and relationships',
        'start_date': today + timedelta(days=5),
        'due_date': today + timedelta(days=10),
        'progress': 30,
        'column': columns[0],  # To Do
        'priority': 'high'
    },
    {
        'title': 'Implement Backend API',
        'description': 'Build REST API endpoints',
        'start_date': today + timedelta(days=10),
        'due_date': today + timedelta(days=20),
        'progress': 0,
        'column': columns[0],  # To Do
        'priority': 'medium'
    },
    {
        'title': 'Create Frontend UI',
        'description': 'Design and implement user interface',
        'start_date': today + timedelta(days=15),
        'due_date': today + timedelta(days=25),
        'progress': 0,
        'column': columns[0],  # To Do
        'priority': 'medium'
    },
    {
        'title': 'Testing and QA',
        'description': 'Perform comprehensive testing',
        'start_date': today + timedelta(days=25),
        'due_date': today + timedelta(days=30),
        'progress': 0,
        'column': columns[0],  # To Do
        'priority': 'urgent'
    },
    {
        'title': 'Deployment',
        'description': 'Deploy to production environment',
        'start_date': today + timedelta(days=30),
        'due_date': today + timedelta(days=32),
        'progress': 0,
        'column': columns[0],  # To Do
        'priority': 'urgent'
    }
]

# Create tasks
created_tasks = []
for task_data in sample_tasks:
    # Convert due_date (date) to datetime for the model
    from datetime import datetime
    task_data_copy = task_data.copy()
    due_date = task_data_copy.pop('due_date')
    task_data_copy['due_date'] = datetime.combine(due_date, datetime.max.time())
    
    task = Task.objects.create(
        created_by=user,
        assigned_to=user,
        **task_data_copy
    )
    created_tasks.append(task)
    print(f"✓ Created task: {task.title}")

# Set up dependencies (each task depends on the previous one)
for i in range(1, len(created_tasks)):
    created_tasks[i].dependencies.add(created_tasks[i-1])
    print(f"✓ Added dependency: '{created_tasks[i].title}' depends on '{created_tasks[i-1].title}'")

print(f"\n✅ Successfully created {len(created_tasks)} sample tasks for board '{board.name}'")
print(f"📊 View the Gantt chart at: /boards/{board.id}/gantt/")
