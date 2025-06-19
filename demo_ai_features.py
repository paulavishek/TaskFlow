#!/usr/bin/env python3
"""
TaskFlow AI Features Demo Script
===============================

This script demonstrates TaskFlow's AI capabilities by creating sample boards
and showcasing the AI-powered features in action.

Run this script to see how TaskFlow's AI features work with real examples.
"""

import os
import sys
import django
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow.settings')
django.setup()

from django.contrib.auth.models import User
from kanban.models import Organization, Board, Column, Task, Comment

def create_demo_data():
    """Create demonstration data showing AI features."""
    
    print("🤖 TaskFlow AI Features Demo")
    print("=" * 50)
    
    # Create or get demo organization
    org, created = Organization.objects.get_or_create(
        name="AI Demo Company",
        defaults={'domain': 'aidemo.com'}
    )
    print(f"✅ Organization: {org.name}")
    
    # Create or get demo user
    user, created = User.objects.get_or_create(
        username="ai_demo_user",
        defaults={
            'email': 'demo@aidemo.com',
            'first_name': 'AI',
            'last_name': 'Demo'
        }
    )
    user.organization = org
    user.save()
    print(f"✅ User: {user.get_full_name()}")
    
    # Demo 1: AI Column Recommendations
    print("\n🎯 Demo 1: Smart Column Recommendations")
    print("-" * 40)
    
    board_examples = [
        {
            'title': 'E-commerce Website Development with Payment Integration',
            'ai_columns': ['Discovery & Planning', 'Design & Wireframes', 'Frontend Development', 
                          'Backend & API Development', 'Payment Integration', 'Testing & QA', 
                          'Deployment & Launch']
        },
        {
            'title': 'Social Media Marketing Campaign for Product Launch Q2 2025',
            'ai_columns': ['Campaign Strategy', 'Content Creation', 'Design & Visuals',
                          'Approval & Review', 'Scheduling & Publishing', 'Monitoring & Engagement',
                          'Analytics & Reporting']
        },
        {
            'title': 'Customer Support Process Improvement Initiative',
            'ai_columns': ['Issue Identification', 'Analysis & Research', 'Solution Design',
                          'Implementation Planning', 'Testing & Validation', 'Training & Rollout',
                          'Monitoring & Optimization']
        }
    ]
    
    for i, example in enumerate(board_examples, 1):
        print(f"\n📋 Board {i}: {example['title']}")
        print("🤖 AI Recommended Columns:")
        for j, column in enumerate(example['ai_columns'], 1):
            print(f"   {j}. {column}")
        
        # Create the board
        board = Board.objects.create(
            title=example['title'],
            organization=org,
            created_by=user
        )
        
        # Create AI-recommended columns
        for position, column_name in enumerate(example['ai_columns']):
            Column.objects.create(
                title=column_name,
                board=board,
                position=position
            )
    
    # Demo 2: Intelligent Task Assistant
    print(f"\n🤖 Demo 2: Intelligent Task Assistant")
    print("-" * 40)
    
    task_examples = [
        {
            'title': 'Implement user authentication system',
            'ai_description': '''Complete user authentication system with the following requirements:

**Core Features:**
• User registration with email verification
• Secure login/logout functionality  
• Password reset via email
• Session management and security

**Technical Requirements:**
• Django authentication framework
• CSRF protection implementation
• Secure password hashing (bcrypt/PBKDF2)
• Email backend configuration

**Acceptance Criteria:**
□ Users can register with valid email addresses
□ Email verification prevents unauthorized access
□ Password reset emails sent successfully
□ Sessions expire after inactivity
□ All forms protected against CSRF attacks

**Estimated Effort:** 8-12 hours
**Dependencies:** Email service configuration, frontend templates'''
        },
        {
            'title': 'Create social media content calendar',
            'ai_description': '''Develop comprehensive social media content calendar for Q2 2025:

**Platform Strategy:**
• LinkedIn: Professional insights and company updates (3x/week)
• Twitter: Quick tips and industry news (daily)
• Instagram: Behind-the-scenes and visual content (2x/week)
• Facebook: Community engagement and customer stories (2x/week)

**Content Types:**
□ Educational posts (40%)
□ Product highlights (25%)
□ Company culture (20%)  
□ User-generated content (15%)

**Deliverables:**
□ 3-month content calendar spreadsheet
□ Content templates for each platform
□ Hashtag research and strategy
□ Engagement tracking metrics setup

**Timeline:** 2 weeks
**Resources Needed:** Design team collaboration, brand guidelines'''
        }
    ]
    
    demo_board = Board.objects.filter(organization=org).first()
    first_column = demo_board.column_set.first()
    
    for i, example in enumerate(task_examples, 1):
        print(f"\n📝 Task {i}: {example['title']}")
        print("🤖 AI Generated Description:")
        print(f"   {example['ai_description'][:200]}...")
        
        Task.objects.create(
            title=example['title'],
            description=example['ai_description'],
            column=first_column,
            created_by=user,
            assignee=user,
            progress=25
        )
    
    # Demo 3: AI Analytics Summary
    print(f"\n📊 Demo 3: AI Analytics Summary")
    print("-" * 40)
    
    analytics_summary = """
🎯 **Team Performance Analysis - Week of {date}**

**📈 Productivity Insights:**
• Team completed 23 tasks this week (↑15% from last week)
• Average task completion time: 2.3 days (↓8% improvement)
• Current sprint velocity: 87% of planned capacity

**⚠️ Bottleneck Detection:**
• 67% of delays occur in the 'Testing & QA' column
• Tasks spending average 3.2 days in 'In Progress' vs 0.8 days in other stages
• 3 high-priority tasks blocked by external dependencies

**💡 AI Recommendations:**
1. **Add Quick Review Column**: Separate simple tasks from complex reviews
   - Expected improvement: 25% faster completion for routine tasks
2. **Load Balancing**: Redistribute 2 tasks from Sarah to Mike
   - Current workload: Sarah (8 tasks), Mike (3 tasks)
3. **Process Optimization**: Implement parallel testing for independent features
   - Potential time savings: 1.5 days per sprint

**🎯 Next Sprint Predictions:**
• Projected completion: 28 tasks (92% confidence)
• Risk factors: 2 critical dependencies, 1 team member on leave
• Recommended capacity: 85% of normal to account for risks

**🏆 Team Highlights:**
• Alex improved task completion rate by 40%
• Quality metrics: 95% first-time pass rate (↑12%)
• Zero critical bugs reported from production deployments
    """.format(date=datetime.now().strftime("%B %d, %Y"))
    
    print(analytics_summary)
    
    print(f"\n✨ Demo Complete!")
    print("=" * 50)
    print("🚀 TaskFlow AI Features successfully demonstrated!")
    print(f"📊 Created {len(board_examples)} AI-optimized boards")
    print(f"📝 Generated {len(task_examples)} intelligent task descriptions")
    print("📈 Showcased predictive analytics and insights")
    print("\n🎯 Ready to experience AI-powered project management!")
    print("   Visit: http://127.0.0.1:8000")

if __name__ == '__main__':
    try:
        create_demo_data()
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        print("💡 Make sure Django is set up and database is migrated")
        print("   Run: python manage.py migrate")
