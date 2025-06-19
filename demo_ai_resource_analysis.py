"""
Demo script for AI-Powered Smart Resource Analysis

This script demonstrates the new AI resource analysis capabilities in TaskFlow.
It populates sample data and shows how the AI analyzes resource bottlenecks,
optimizes assignments, and provides intelligent recommendations.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from kanban.models import Board, Column, Task
from accounts.models import Organization, UserProfile
from kanban.utils.ai_resource_analysis import (
    analyze_resource_bottlenecks,
    optimize_task_assignments,
    balance_team_workload,
    forecast_resource_needs,
    suggest_resource_reallocation
)

def create_demo_data():
    """Create comprehensive demo data for resource analysis"""
    print("🚀 Creating demo data for AI Resource Analysis...")
    
    # Create a demo admin user first
    admin_user, created = User.objects.get_or_create(
        username='admin_demo',
        defaults={
            'first_name': 'Demo',
            'last_name': 'Admin',
            'email': 'admin@aidemo.com',
            'is_staff': True
        }
    )
    
    # Create organization with the admin user
    org, created = Organization.objects.get_or_create(
        name="AI Demo Corp",
        defaults={
            'domain': 'aidemo.com',
            'created_by': admin_user
        }
    )
    
    # Create admin profile
    admin_profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'organization': org,
            'is_admin': True,
            'weekly_capacity_hours': 40
        }
    )
    
    # Create diverse team members with different skills and capacities
    team_members = [
        {
            'username': 'sarah_backend',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah@aidemo.com',
            'skills': [
                {'name': 'Python', 'level': 'Expert'},
                {'name': 'Django', 'level': 'Expert'},
                {'name': 'PostgreSQL', 'level': 'Advanced'},
                {'name': 'API Design', 'level': 'Expert'},
                {'name': 'DevOps', 'level': 'Intermediate'}
            ],
            'capacity': 40,
            'preferred_types': ['Backend Development', 'API Development', 'Database Design']
        },
        {
            'username': 'mike_fullstack',
            'first_name': 'Mike',
            'last_name': 'Chen',
            'email': 'mike@aidemo.com',
            'skills': [
                {'name': 'JavaScript', 'level': 'Expert'},
                {'name': 'React', 'level': 'Advanced'},
                {'name': 'Node.js', 'level': 'Advanced'},
                {'name': 'Python', 'level': 'Intermediate'},
                {'name': 'MongoDB', 'level': 'Advanced'}
            ],
            'capacity': 40,
            'preferred_types': ['Full Stack Development', 'Frontend Development', 'UI/UX']
        },
        {
            'username': 'alex_database',
            'first_name': 'Alex',
            'last_name': 'Rodriguez',
            'email': 'alex@aidemo.com',
            'skills': [
                {'name': 'PostgreSQL', 'level': 'Expert'},
                {'name': 'MongoDB', 'level': 'Expert'},
                {'name': 'Data Modeling', 'level': 'Expert'},
                {'name': 'Performance Optimization', 'level': 'Advanced'},
                {'name': 'Python', 'level': 'Intermediate'}
            ],
            'capacity': 35,  # Part-time consultant
            'preferred_types': ['Database Design', 'Performance Optimization', 'Data Analysis']
        },
        {
            'username': 'emma_frontend',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'email': 'emma@aidemo.com',
            'skills': [
                {'name': 'React', 'level': 'Expert'},
                {'name': 'TypeScript', 'level': 'Advanced'},
                {'name': 'CSS/SCSS', 'level': 'Expert'},
                {'name': 'UI/UX Design', 'level': 'Advanced'},
                {'name': 'Testing', 'level': 'Intermediate'}
            ],
            'capacity': 40,
            'preferred_types': ['Frontend Development', 'UI/UX Design', 'Component Development']
        },
        {
            'username': 'david_devops',
            'first_name': 'David',
            'last_name': 'Kumar',
            'email': 'david@aidemo.com',
            'skills': [
                {'name': 'AWS', 'level': 'Expert'},
                {'name': 'Docker', 'level': 'Expert'},
                {'name': 'Kubernetes', 'level': 'Advanced'},
                {'name': 'CI/CD', 'level': 'Expert'},
                {'name': 'Python', 'level': 'Intermediate'}
            ],
            'capacity': 40,
            'preferred_types': ['DevOps', 'Infrastructure', 'Deployment', 'Monitoring']
        },
        {
            'username': 'lisa_junior',
            'first_name': 'Lisa',
            'last_name': 'Park',
            'email': 'lisa@aidemo.com',
            'skills': [
                {'name': 'JavaScript', 'level': 'Intermediate'},
                {'name': 'React', 'level': 'Beginner'},
                {'name': 'HTML/CSS', 'level': 'Advanced'},
                {'name': 'Testing', 'level': 'Beginner'}
            ],
            'capacity': 40,
            'preferred_types': ['Frontend Development', 'Testing', 'Documentation']
        }
    ]
    
    # Create users and profiles
    created_users = []
    for member_data in team_members:
        user, created = User.objects.get_or_create(
            username=member_data['username'],
            defaults={
                'first_name': member_data['first_name'],
                'last_name': member_data['last_name'],
                'email': member_data['email']
            }
        )
        
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'organization': org,
                'skills': member_data['skills'],
                'weekly_capacity_hours': member_data['capacity'],
                'preferred_task_types': member_data['preferred_types'],
                'quality_score': random.randint(75, 100),
                'average_task_completion_time': random.uniform(6.0, 12.0),
                'collaboration_score': random.randint(80, 100)
            }
        )
        
        created_users.append(user)
      # Create a comprehensive project board
    board, created = Board.objects.get_or_create(
        name="AI-Powered E-commerce Platform Development",
        defaults={
            'description': 'Building a modern e-commerce platform with AI features, microservices architecture, and advanced analytics',
            'organization': org,
            'created_by': admin_user
        }
    )
    
    # Add all team members to the board
    for user in created_users:
        board.members.add(user)
    
    # Create workflow columns
    columns_data = [
        'Backlog',
        'Analysis & Design', 
        'In Development',
        'Code Review',
        'Testing',
        'Deployment',
        'Done'
    ]
    
    columns = []
    for i, col_name in enumerate(columns_data):
        column, created = Column.objects.get_or_create(
            name=col_name,
            board=board,
            defaults={'position': i}
        )
        columns.append(column)
    
    # Create diverse tasks with different complexity and skill requirements
    tasks_data = [
        # Backend heavy tasks
        {
            'title': 'Design User Authentication Microservice',
            'description': 'Create a scalable authentication service with JWT, OAuth2, and multi-factor authentication',
            'column': 'Analysis & Design',
            'priority': 'high',
            'estimated_hours': 24,
            'complexity': 8,
            'required_skills': [
                {'name': 'Python', 'level': 'Expert'},
                {'name': 'API Design', 'level': 'Advanced'},
                {'name': 'Security', 'level': 'Advanced'}
            ],
            'assigned_to': 'sarah_backend',
            'due_days': 5
        },
        {
            'title': 'Implement Payment Processing API',
            'description': 'Integrate with Stripe and PayPal, handle webhooks, and implement transaction monitoring',
            'column': 'Backlog',
            'priority': 'urgent',
            'estimated_hours': 32,
            'complexity': 9,
            'required_skills': [
                {'name': 'Python', 'level': 'Expert'},
                {'name': 'API Design', 'level': 'Expert'},
                {'name': 'Security', 'level': 'Advanced'}
            ],
            'assigned_to': 'sarah_backend',
            'due_days': 3
        },
        {
            'title': 'Optimize Database Performance',
            'description': 'Analyze query performance, implement indexing strategy, and optimize database schema',
            'column': 'In Development',
            'priority': 'high',
            'estimated_hours': 16,
            'complexity': 7,
            'required_skills': [
                {'name': 'PostgreSQL', 'level': 'Expert'},
                {'name': 'Performance Optimization', 'level': 'Expert'}
            ],
            'assigned_to': 'alex_database',
            'due_days': 7
        },
        
        # Frontend heavy tasks
        {
            'title': 'Build Product Catalog Component',
            'description': 'Create responsive product grid with filtering, sorting, and pagination',
            'column': 'In Development',
            'priority': 'medium',
            'estimated_hours': 20,
            'complexity': 6,
            'required_skills': [
                {'name': 'React', 'level': 'Advanced'},
                {'name': 'TypeScript', 'level': 'Intermediate'},
                {'name': 'CSS/SCSS', 'level': 'Advanced'}
            ],
            'assigned_to': 'emma_frontend',
            'due_days': 10
        },
        {
            'title': 'Implement Shopping Cart UI',
            'description': 'Build interactive shopping cart with quantity updates, price calculations, and checkout flow',
            'column': 'Code Review',
            'priority': 'high',
            'estimated_hours': 18,
            'complexity': 5,
            'required_skills': [
                {'name': 'React', 'level': 'Advanced'},
                {'name': 'JavaScript', 'level': 'Advanced'}
            ],
            'assigned_to': 'mike_fullstack',
            'due_days': 8
        },
        {
            'title': 'Create User Dashboard',
            'description': 'Build user profile page with order history, preferences, and account management',
            'column': 'Backlog',
            'priority': 'medium',
            'estimated_hours': 24,
            'complexity': 6,
            'required_skills': [
                {'name': 'React', 'level': 'Intermediate'},
                {'name': 'UI/UX Design', 'level': 'Intermediate'}
            ],
            'assigned_to': None,  # Unassigned - good for optimization demo
            'due_days': 14
        },
        
        # DevOps tasks
        {
            'title': 'Setup CI/CD Pipeline',
            'description': 'Configure automated testing, building, and deployment pipeline with Docker and Kubernetes',
            'column': 'In Development',
            'priority': 'high',
            'estimated_hours': 20,
            'complexity': 8,
            'required_skills': [
                {'name': 'Docker', 'level': 'Expert'},
                {'name': 'CI/CD', 'level': 'Expert'},
                {'name': 'Kubernetes', 'level': 'Advanced'}
            ],
            'assigned_to': 'david_devops',
            'due_days': 6
        },
        {
            'title': 'Configure Monitoring and Logging',
            'description': 'Setup application monitoring, log aggregation, and alerting systems',
            'column': 'Backlog',
            'priority': 'medium',
            'estimated_hours': 16,
            'complexity': 7,
            'required_skills': [
                {'name': 'AWS', 'level': 'Advanced'},
                {'name': 'Monitoring', 'level': 'Advanced'}
            ],
            'assigned_to': 'david_devops',
            'due_days': 12
        },
        
        # Junior-level tasks
        {
            'title': 'Write Unit Tests for Components',
            'description': 'Create comprehensive test suite for React components using Jest and React Testing Library',
            'column': 'Backlog',
            'priority': 'medium',
            'estimated_hours': 12,
            'complexity': 3,
            'required_skills': [
                {'name': 'Testing', 'level': 'Intermediate'},
                {'name': 'JavaScript', 'level': 'Intermediate'}
            ],
            'assigned_to': 'lisa_junior',
            'due_days': 15
        },
        {
            'title': 'Update Documentation',
            'description': 'Update API documentation and create user guides for new features',
            'column': 'Backlog',
            'priority': 'low',
            'estimated_hours': 8,
            'complexity': 2,
            'required_skills': [
                {'name': 'Documentation', 'level': 'Intermediate'}
            ],
            'assigned_to': None,  # Unassigned
            'due_days': 20
        },
        
        # Full-stack tasks
        {
            'title': 'Implement Search Functionality',
            'description': 'Build search API with Elasticsearch and create search UI with autocomplete',
            'column': 'Backlog',
            'priority': 'high',
            'estimated_hours': 28,
            'complexity': 8,
            'required_skills': [
                {'name': 'Python', 'level': 'Advanced'},
                {'name': 'JavaScript', 'level': 'Advanced'},
                {'name': 'Elasticsearch', 'level': 'Intermediate'}
            ],
            'assigned_to': 'mike_fullstack',
            'due_days': 9
        }
    ]
    
    # Create tasks
    user_lookup = {user.username: user for user in created_users}
    column_lookup = {col.name: col for col in columns}
    
    for task_data in tasks_data:
        assigned_user = None
        if task_data['assigned_to']:
            assigned_user = user_lookup.get(task_data['assigned_to'])
        
        due_date = timezone.now() + timedelta(days=task_data['due_days'])
        
        task, created = Task.objects.get_or_create(
            title=task_data['title'],
            column=column_lookup[task_data['column']],
            defaults={
                'description': task_data['description'],
                'assigned_to': assigned_user,
                'created_by': admin_user,
                'priority': task_data['priority'],
                'estimated_duration_hours': task_data['estimated_hours'],
                'complexity_score': task_data['complexity'],
                'required_skills': task_data['required_skills'],
                'due_date': due_date,
                'progress': random.randint(0, 30) if task_data['column'] != 'Backlog' else 0
            }
        )
    
    print(f"✅ Created demo board '{board.name}' with {len(created_users)} team members and {len(tasks_data)} tasks")
    return board

def demonstrate_ai_features(board):
    """Demonstrate all AI resource analysis features"""
    print(f"\n🧠 Demonstrating AI Resource Analysis for board: {board.name}")
    print("=" * 70)
    
    # 1. Analyze Resource Bottlenecks
    print("\n1. 🔥 ANALYZING RESOURCE BOTTLENECKS")
    print("-" * 40)
    bottleneck_result = analyze_resource_bottlenecks(board.id)
    if bottleneck_result:
        print(f"Risk Score: {bottleneck_result.get('bottleneck_risk_score', 'N/A')}/10")
        print(f"Critical Bottlenecks Found: {len(bottleneck_result.get('critical_bottlenecks', []))}")
        
        for bottleneck in bottleneck_result.get('critical_bottlenecks', [])[:2]:  # Show first 2
            print(f"  • {bottleneck.get('type', 'Unknown').upper()}: {bottleneck.get('description', 'No description')}")
            print(f"    Affected: {bottleneck.get('affected_person', 'Unknown')}")
            print(f"    Severity: {bottleneck.get('severity', 'Unknown')}")
        
        print(f"Resource Recommendations: {len(bottleneck_result.get('resource_recommendations', []))}")
        for rec in bottleneck_result.get('resource_recommendations', [])[:2]:
            print(f"  • {rec.get('action', 'Unknown').upper()}: {rec.get('description', 'No description')}")
    
    # 2. Optimize Task Assignments
    print("\n2. 🎯 OPTIMIZING TASK ASSIGNMENTS")
    print("-" * 40)
    optimization_result = optimize_task_assignments(board.id)
    if optimization_result:
        summary = optimization_result.get('optimization_summary', {})
        print(f"Tasks Analyzed: {summary.get('total_tasks_analyzed', 0)}")
        print(f"Assignments Changed: {summary.get('assignments_changed', 0)}")
        print(f"Skill Match Improvement: {summary.get('average_skill_match_improvement', 0)}%")
        print(f"Workload Balance Score: {summary.get('workload_balance_score', 0)}/10")
        
        optimal_assignments = optimization_result.get('optimal_assignments', [])
        print(f"\nOptimal Assignment Suggestions: {len(optimal_assignments)}")
        for assignment in optimal_assignments[:3]:  # Show first 3
            print(f"  • '{assignment.get('task_title', 'Unknown Task')}' -> {assignment.get('recommended_assignee', 'Unknown')}")
            print(f"    Skill Match: {assignment.get('skill_match_score', 0)}%")
            print(f"    Reasoning: {assignment.get('reasoning', 'No reasoning provided')[:80]}...")
    
    # 3. Balance Team Workload
    print("\n3. ⚖️ BALANCING TEAM WORKLOAD")
    print("-" * 40)
    balance_result = balance_team_workload(board.id)
    if balance_result:
        print(f"Workload Health Score: {balance_result.get('workload_health_score', 0)}/10")
        print(f"Imbalance Severity: {balance_result.get('imbalance_severity', 'Unknown').upper()}")
        
        overloaded = balance_result.get('overloaded_members', [])
        underutilized = balance_result.get('underutilized_members', [])
        
        print(f"Overloaded Members: {len(overloaded)}")
        for member in overloaded[:2]:
            print(f"  • {member.get('username', 'Unknown')}: {member.get('current_utilization', 0)}% utilization")
            print(f"    Recommended Reduction: {member.get('recommended_reduction', 0)} hours")
        
        print(f"Underutilized Members: {len(underutilized)}")
        for member in underutilized[:2]:
            print(f"  • {member.get('username', 'Unknown')}: {member.get('current_utilization', 0)}% utilization")
            print(f"    Available Capacity: {member.get('available_capacity', 0)} hours")
    
    # 4. Forecast Resource Needs
    print("\n4. 📈 FORECASTING RESOURCE NEEDS")
    print("-" * 40)
    forecast_result = forecast_resource_needs(board.id, 4)  # 4 weeks
    if forecast_result:
        summary = forecast_result.get('forecast_summary', {})
        print(f"Forecast Period: {summary.get('forecast_period_weeks', 0)} weeks")
        print(f"Demand vs Capacity Ratio: {summary.get('demand_vs_capacity_ratio', 0)}")
        print(f"Overall Risk Level: {summary.get('overall_risk_level', 'Unknown').upper()}")
        print(f"Recommended Action: {summary.get('recommended_action', 'Unknown').upper()}")
        
        capacity_forecast = forecast_result.get('capacity_forecast', [])
        if capacity_forecast:
            print(f"\nCapacity Forecast for Next {len(capacity_forecast)} Weeks:")
            for week_data in capacity_forecast[:2]:  # Show first 2 weeks
                week = week_data.get('week', 'Unknown')
                available = week_data.get('available_hours', 0)
                required = week_data.get('required_hours', 0)
                utilization = week_data.get('utilization_percentage', 0)
                print(f"  Week {week}: {available}h available, {required}h required ({utilization}% utilization)")
    
    # 5. Suggest Resource Reallocation
    print("\n5. 🔄 SUGGESTING REAL-TIME REALLOCATION")
    print("-" * 40)
    reallocation_result = suggest_resource_reallocation(board.id)
    if reallocation_result:
        print(f"Reallocation Urgency: {reallocation_result.get('reallocation_urgency', 'Unknown').upper()}")
        print(f"Immediate Actions Required: {reallocation_result.get('immediate_actions_required', False)}")
        
        crisis_tasks = reallocation_result.get('crisis_tasks', [])
        if crisis_tasks:
            print(f"Crisis Tasks Identified: {len(crisis_tasks)}")
            for crisis in crisis_tasks[:2]:
                print(f"  • '{crisis.get('task_title', 'Unknown')}' -> {crisis.get('action', 'Unknown').upper()}")
                print(f"    Recommended Assignee: {crisis.get('recommended_assignee', 'Unknown')}")
                print(f"    Time Sensitivity: {crisis.get('time_sensitivity', 'Unknown')}")
        
        reallocations = reallocation_result.get('immediate_reallocations', [])
        if reallocations:
            print(f"Immediate Reallocations Suggested: {len(reallocations)}")
            for realloc in reallocations[:2]:
                print(f"  • Move tasks from {realloc.get('from_user', 'Unknown')} to {realloc.get('to_user', 'Unknown')}")
                print(f"    Estimated Time Saved: {realloc.get('estimated_time_saved', 'Unknown')}")

def main():
    """Main function to run the demo"""
    print("🎯 AI-Powered Smart Resource Analysis Demo")
    print("=" * 50)
    
    # Create demo data
    board = create_demo_data()
    
    # Demonstrate AI features
    demonstrate_ai_features(board)
    
    print("\n🎉 Demo completed successfully!")
    print("\nTo explore the AI Resource Analysis features:")
    print(f"1. Visit your board: http://localhost:8000/boards/{board.id}/")
    print(f"2. Click 'AI Resource Analysis' button")
    print("3. Try different analysis options to see AI-powered insights")
    print("\nKey Features Demonstrated:")
    print("• Bottleneck prediction before they happen")
    print("• Intelligent task assignment optimization")
    print("• Dynamic team workload balancing")
    print("• Future resource needs forecasting")
    print("• Real-time resource reallocation suggestions")

if __name__ == "__main__":
    main()
