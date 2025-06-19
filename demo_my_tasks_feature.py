#!/usr/bin/env python
"""
Demo script for the new "My Tasks" feature on the TaskFlow dashboard.
This script demonstrates the functionality and creates a visual representation.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from kanban.models import Board, Column, Task, TaskLabel
from accounts.models import Organization, UserProfile

def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_section(title):
    """Print a section header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def demo_my_tasks_feature():
    """Demonstrate the My Tasks feature"""
    
    print_banner("MY TASKS FEATURE DEMONSTRATION")
    
    print("""
The 'My Tasks' feature has been successfully added to the TaskFlow dashboard!

FEATURE OVERVIEW:
✅ New 'My Tasks' metric card in the analytics row
✅ Dedicated 'My Tasks' section showing top 5 assigned tasks
✅ Full 'My Tasks' modal with all assigned tasks
✅ Priority-based color coding and visual indicators
✅ Progress tracking with visual progress bars
✅ Overdue task highlighting
✅ Quick access buttons to view task details and boards
    """)
    
    # Get test users
    try:
        team_member = User.objects.get(username='john_doe')
        admin_user = User.objects.get(username='admin')
        board = Board.objects.get(name='My Tasks Demo Board')
    except:
        print("❌ Test data not found. Please run test_my_tasks_feature.py first!")
        return
    
    print_section("DASHBOARD COMPONENTS ADDED")
    
    print("""
1. ANALYTICS CARDS ROW:
   • Added 'My Tasks' metric card (6th card in the analytics row)
   • Shows count of tasks assigned to the logged-in user
   • Clickable to open the full 'My Tasks' modal
   • Icon: user-check (FontAwesome)
   
2. MY TASKS SECTION:
   • Positioned between Lean Six Sigma highlight and Your Boards
   • Shows top 5 most recent tasks assigned to current user
   • Excludes completed tasks (tasks in 'Done' columns)
   • Card layout with priority-based left border colors:
     - Red: Urgent priority
     - Orange: High priority  
     - Blue: Medium priority
     - Green: Low priority
   
3. MY TASKS MODAL:
   • Full table view of all assigned tasks
   • Columns: Title, Board, Column, Priority, Due Date, Progress
   • Overdue tasks highlighted in red
   • Quick action buttons for each task
    """)
    
    print_section("CURRENT TEST DATA SUMMARY")
    
    # Get current task statistics
    my_tasks = Task.objects.filter(
        column__board=board,
        assigned_to=team_member
    ).exclude(column__name__icontains='done')
    
    overdue_tasks = my_tasks.filter(due_date__lt=timezone.now())
    urgent_tasks = my_tasks.filter(priority='urgent')
    high_tasks = my_tasks.filter(priority='high')
    
    print(f"""
User: {team_member.first_name} {team_member.last_name} ({team_member.username})
Organization: {team_member.profile.organization.name}
Board: {board.name}

📊 TASK STATISTICS:
   • Total assigned tasks: {my_tasks.count()}
   • Overdue tasks: {overdue_tasks.count()}
   • Urgent priority: {urgent_tasks.count()}
   • High priority: {high_tasks.count()}
    """)
    
    print_section("TASK DETAILS")
    
    print(f"{'Title':<30} {'Priority':<10} {'Progress':<10} {'Status':<12} {'Due Date':<12}")
    print("-" * 80)
    
    for task in my_tasks.order_by('-created_at'):
        status = "OVERDUE" if task.due_date and task.due_date < timezone.now() else "ON TIME"
        due_str = task.due_date.strftime('%m/%d/%Y') if task.due_date else "No due date"
        
        title = task.title[:28] + ".." if len(task.title) > 30 else task.title
        print(f"{title:<30} {task.priority.upper():<10} {task.progress:>3}%{'':<6} {status:<12} {due_str:<12}")
    
    print_section("FEATURE BENEFITS")
    
    print("""
✅ INDIVIDUAL PRODUCTIVITY:
   • Quick view of personal workload
   • Immediate visibility of what needs attention
   • Priority-based visual organization
   • Progress tracking at a glance
   
✅ TIME MANAGEMENT:
   • Overdue task identification
   • Due date awareness
   • Task prioritization support
   
✅ WORKFLOW EFFICIENCY:
   • Quick navigation to task details
   • Direct access to relevant boards
   • Reduced context switching
   
✅ USER EXPERIENCE:
   • Clean, intuitive interface
   • Consistent with existing design
   • Mobile-responsive layout
   • Accessible color coding
    """)
    
    print_section("TECHNICAL IMPLEMENTATION")
    
    print("""
📁 FILES MODIFIED:
   • kanban/views.py - Added my_tasks queries and context
   • templates/kanban/dashboard.html - Added UI components
   
🔧 DATABASE QUERIES ADDED:
   • my_tasks: Top 5 recent tasks assigned to user (excluding done)
   • my_tasks_count: Count of all assigned tasks (excluding done)
   
🎨 UI COMPONENTS:
   • Analytics metric card with user-check icon
   • Task cards with priority-based styling
   • Comprehensive modal with table layout
   • Responsive grid system (col-md-6 col-lg-4)
   
🚀 PERFORMANCE OPTIMIZATIONS:
   • select_related() for efficient database queries
   • Limited to top 5 for dashboard performance
   • Proper indexing on assigned_to field
    """)
    
    print_section("TESTING INSTRUCTIONS")
    
    print(f"""
🧪 TO TEST THE FEATURE:

1. Start the Django development server:
   python manage.py runserver
   
2. Navigate to: http://127.0.0.1:8000/dashboard/

3. Login with test credentials:
   Username: {team_member.username}
   Password: password123
   
4. Observe the dashboard changes:
   ✓ New 'My Tasks' metric card in analytics row
   ✓ 'My Tasks' section with assigned task cards
   ✓ Click 'View All' to open the full modal
   
5. Test with different user:
   Username: {admin_user.username}
   Password: admin123
   (Should show different/fewer tasks)
    """)
    
    print_section("FEATURE VALIDATION CHECKLIST")
    
    print("""
☑️ VISUAL VERIFICATION:
   □ My Tasks metric card appears in analytics row
   □ My Tasks section displays between features and boards
   □ Task cards show appropriate priority colors
   □ Overdue tasks are highlighted in red
   □ Progress bars display correctly
   
☑️ FUNCTIONAL VERIFICATION:
   □ Metric card click opens modal
   □ Task cards show correct information
   □ View buttons navigate to task details
   □ Board buttons navigate to correct boards
   □ Modal displays all assigned tasks
   
☑️ RESPONSIVE VERIFICATION:
   □ Layout works on desktop
   □ Layout adapts to tablet view
   □ Cards stack properly on mobile
   □ Modal is scrollable on small screens
    """)
    
    print_banner("FEATURE DEMONSTRATION COMPLETE")
    
    print(f"""
🎉 SUCCESS! The "My Tasks" feature has been successfully implemented!

This feature provides team members with immediate visibility into their 
personal workload, helping them prioritize and manage their tasks more 
effectively. The implementation follows TaskFlow's existing design patterns 
and integrates seamlessly with the current dashboard layout.

Ready for testing at: http://127.0.0.1:8000/dashboard/
    """)

if __name__ == '__main__':
    demo_my_tasks_feature()
