from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from accounts.models import Organization, UserProfile
from kanban.models import Board, Column, Task, TaskLabel, Comment, TaskActivity


class Command(BaseCommand):
    help = 'Load demo data for specific scenarios to showcase TaskFlow AI features'

    def add_arguments(self, parser):
        parser.add_argument('--scenario', type=str, default='tech_startup',
                          help='Demo scenario to load (tech_startup, marketing_agency, enterprise_it)')
        parser.add_argument('--user-id', type=int, help='User ID to create demo data for')

    def handle(self, *args, **options):
        scenario = options['scenario']
        user_id = options.get('user_id')
        
        self.stdout.write(f"🚀 Loading demo data for scenario: {scenario}")
        
        # Get or use provided user
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
                return
        else:
            # Use the current authenticated user (this will be handled in the view)
            self.stdout.write(self.style.ERROR("User ID is required when running from command line"))
            return
        
        # Load the scenario
        if scenario == 'tech_startup':
            self.create_tech_startup_scenario(user)
        elif scenario == 'marketing_agency':
            self.create_marketing_agency_scenario(user)
        elif scenario == 'enterprise_it':
            self.create_enterprise_it_scenario(user)
        else:
            self.stdout.write(self.style.ERROR(f"Unknown scenario: {scenario}"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"✅ Demo data loaded successfully for {scenario}!"))

    def create_tech_startup_scenario(self, user):
        """Create tech startup demo scenario"""
        self.stdout.write("📱 Creating Tech Startup scenario...")
        
        # Create boards
        boards_data = [
            {
                'name': 'E-commerce Mobile App Development',
                'description': 'Complete mobile application development with payment gateway integration, user authentication, and AI-powered recommendation engine.',
                'columns': ['Product Backlog', 'Sprint Planning', 'Development', 'Code Review', 'Testing', 'Deployment', 'Done']
            },
            {
                'name': 'Bug Tracking & Quality Assurance',
                'description': 'Critical bug tracking and quality assurance workflow for production releases.',
                'columns': ['New Issues', 'Triaged', 'In Progress', 'Under Review', 'Testing', 'Verified', 'Closed']
            },
            {
                'name': 'DevOps & Infrastructure',
                'description': 'Infrastructure management, CI/CD pipeline, and deployment automation.',
                'columns': ['Planning', 'Implementation', 'Testing', 'Staging', 'Production', 'Monitoring']
            }
        ]
        
        created_boards = []
        for board_data in boards_data:
            board = self.create_board_with_tasks(user, board_data, 'tech_startup')
            created_boards.append(board)
        
        # Create team members for collaboration
        self.create_demo_team_members(user, 'tech_startup')
        
        self.stdout.write(f"✅ Created {len(created_boards)} boards for tech startup scenario")

    def create_marketing_agency_scenario(self, user):
        """Create marketing agency demo scenario"""
        self.stdout.write("📢 Creating Marketing Agency scenario...")
        
        boards_data = [
            {
                'name': 'Q1 Multi-Client Campaign Management',
                'description': 'Coordinating campaigns for 5+ clients with different objectives, timelines, and creative requirements.',
                'columns': ['Client Briefing', 'Strategy Development', 'Creative Production', 'Client Review', 'Revisions', 'Approval', 'Launch', 'Performance Tracking']
            },
            {
                'name': 'Content Calendar & Social Media',
                'description': 'Cross-platform content creation and social media management for multiple brands.',
                'columns': ['Content Ideas', 'Writing', 'Design', 'Approval', 'Scheduled', 'Published', 'Analytics']
            },
            {
                'name': 'Client Relationship & Account Management',
                'description': 'Managing client relationships, proposals, contracts, and ongoing communication.',
                'columns': ['Prospects', 'Proposals', 'Negotiations', 'Onboarding', 'Active Projects', 'Renewal', 'Completed']
            },
            {
                'name': 'Performance Analytics & Reporting',
                'description': 'Campaign performance analysis, client reporting, and optimization recommendations.',
                'columns': ['Data Collection', 'Analysis', 'Report Creation', 'Client Presentation', 'Optimization', 'Archived']
            }
        ]
        
        created_boards = []
        for board_data in boards_data:
            board = self.create_board_with_tasks(user, board_data, 'marketing_agency')
            created_boards.append(board)
        
        self.create_demo_team_members(user, 'marketing_agency')
        self.stdout.write(f"✅ Created {len(created_boards)} boards for marketing agency scenario")

    def create_enterprise_it_scenario(self, user):
        """Create enterprise IT demo scenario"""
        self.stdout.write("🏢 Creating Enterprise IT scenario...")
        
        boards_data = [
            {
                'name': 'Legacy System Migration to Cloud',
                'description': 'Large-scale migration of legacy ERP system to AWS cloud infrastructure with zero downtime requirement.',
                'columns': ['Assessment', 'Planning', 'Development', 'Testing', 'Staging', 'Migration', 'Validation', 'Completed']
            },
            {
                'name': 'Cybersecurity & Compliance',
                'description': 'Security audits, vulnerability management, and compliance preparation for SOC 2 certification.',
                'columns': ['Risk Assessment', 'Planning', 'Implementation', 'Testing', 'Documentation', 'Audit', 'Certification']
            }
        ]
        
        created_boards = []
        for board_data in boards_data:
            board = self.create_board_with_tasks(user, board_data, 'enterprise_it')
            created_boards.append(board)
        
        self.create_demo_team_members(user, 'enterprise_it')
        self.stdout.write(f"✅ Created {len(created_boards)} boards for enterprise IT scenario")

    def create_board_with_tasks(self, user, board_data, scenario):
        """Create a board with columns and realistic tasks"""
        try:
            profile = user.profile
            organization = profile.organization
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR("User profile not found"))
            return None
        
        # Create board
        board = Board.objects.create(
            name=board_data['name'],
            description=board_data['description'],
            organization=organization,
            created_by=user
        )
        
        # Create columns
        columns = []
        for i, column_name in enumerate(board_data['columns']):
            column = Column.objects.create(
                name=column_name,
                board=board,
                position=i
            )
            columns.append(column)
        
        # Create labels based on scenario
        self.create_demo_labels(board, scenario)
        
        # Create tasks based on scenario
        self.create_scenario_tasks(board, columns, scenario, user)
        
        return board

    def create_demo_labels(self, board, scenario):
        """Create scenario-specific labels"""
        if scenario == 'tech_startup':
            labels = [
                {'name': 'Frontend', 'color': '#3498db'},
                {'name': 'Backend', 'color': '#e74c3c'},
                {'name': 'Database', 'color': '#f39c12'},
                {'name': 'API', 'color': '#9b59b6'},
                {'name': 'Security', 'color': '#e67e22'},
                {'name': 'Performance', 'color': '#1abc9c'},
                {'name': 'Bug', 'color': '#e74c3c'},
                {'name': 'Enhancement', 'color': '#2ecc71'},
            ]
        elif scenario == 'marketing_agency':
            labels = [
                {'name': 'Creative', 'color': '#ff69b4'},
                {'name': 'Strategy', 'color': '#4169e1'},
                {'name': 'Client A', 'color': '#ff6347'},
                {'name': 'Client B', 'color': '#32cd32'},
                {'name': 'Client C', 'color': '#ffd700'},
                {'name': 'Social Media', 'color': '#8a2be2'},
                {'name': 'Urgent', 'color': '#dc143c'},
                {'name': 'Campaign', 'color': '#00ced1'},
            ]
        else:  # enterprise_it
            labels = [
                {'name': 'Critical', 'color': '#dc143c'},
                {'name': 'Security', 'color': '#b22222'},
                {'name': 'Infrastructure', 'color': '#4682b4'},
                {'name': 'Compliance', 'color': '#daa520'},
                {'name': 'Migration', 'color': '#2e8b57'},
                {'name': 'Documentation', 'color': '#708090'},
                {'name': 'Stakeholder Review', 'color': '#9370db'},
            ]
        
        for label_data in labels:
            TaskLabel.objects.create(
                name=label_data['name'],
                color=label_data['color'],
                board=board
            )

    def create_scenario_tasks(self, board, columns, scenario, user):
        """Create realistic tasks for each scenario"""
        if scenario == 'tech_startup':
            self.create_tech_startup_tasks(board, columns, user)
        elif scenario == 'marketing_agency':
            self.create_marketing_agency_tasks(board, columns, user)
        else:  # enterprise_it
            self.create_enterprise_it_tasks(board, columns, user)

    def create_tech_startup_tasks(self, board, columns, user):
        """Create tech startup specific tasks"""
        tasks_by_column = {
            0: [  # Product Backlog
                {
                    'title': 'User Authentication System with OAuth Integration',
                    'description': 'Implement comprehensive user authentication system supporting email/password, Google OAuth, and Apple Sign-In. Include password reset, email verification, and two-factor authentication options.',
                    'priority': 'high',
                    'labels': ['Backend', 'Security'],
                    'progress': 0
                },
                {
                    'title': 'AI-Powered Product Recommendation Engine',
                    'description': 'Design and implement machine learning algorithms to provide personalized product recommendations based on user behavior, purchase history, and demographic data.',
                    'priority': 'medium',
                    'labels': ['Backend', 'API'],
                    'progress': 15
                }
            ],
            1: [  # Sprint Planning
                {
                    'title': 'Payment Gateway Integration (Stripe & PayPal)',
                    'description': 'Integrate multiple payment processors to handle transactions, subscriptions, and refunds. Implement proper error handling and webhook management.',
                    'priority': 'urgent',
                    'labels': ['Backend', 'Security'],
                    'progress': 25
                }
            ],
            2: [  # Development
                {
                    'title': 'Real-time Order Tracking System',
                    'description': 'Build real-time order tracking with WebSocket connections, push notifications, and integration with shipping APIs from major carriers.',
                    'priority': 'high',
                    'labels': ['Frontend', 'Backend'],
                    'progress': 60
                },
                {
                    'title': 'Advanced Search & Filtering UI',
                    'description': 'Create sophisticated product search with auto-complete, faceted filtering, and search result optimization.',
                    'priority': 'medium',
                    'labels': ['Frontend'],
                    'progress': 40
                }
            ],
            3: [  # Code Review
                {
                    'title': 'Shopping Cart Persistence & Sync',
                    'description': 'Implement cart synchronization across devices with conflict resolution and offline support.',
                    'priority': 'medium',
                    'labels': ['Frontend', 'Backend'],
                    'progress': 85
                }
            ],
            4: [  # Testing
                {
                    'title': 'Performance Testing for 10K Concurrent Users',
                    'description': 'Comprehensive load testing to ensure system can handle peak traffic during sales events.',
                    'priority': 'high',
                    'labels': ['Performance'],
                    'progress': 70
                }
            ],
            5: [  # Deployment
                {
                    'title': 'CI/CD Pipeline Setup with Auto-scaling',
                    'description': 'Configure automated deployment pipeline with staging environments and auto-scaling based on traffic.',
                    'priority': 'high',
                    'labels': ['Performance'],
                    'progress': 90
                }
            ],
            6: [  # Done
                {
                    'title': 'Database Schema Optimization',
                    'description': 'Optimize database queries and implement proper indexing for improved performance.',
                    'priority': 'medium',
                    'labels': ['Database', 'Performance'],
                    'progress': 100
                }
            ]
        }
        
        self.create_tasks_from_data(board, columns, tasks_by_column, user)

    def create_marketing_agency_tasks(self, board, columns, user):
        """Create marketing agency specific tasks"""
        tasks_by_column = {
            0: [  # Client Briefing
                {
                    'title': 'TechCorp Q1 Campaign Strategy Session',
                    'description': 'Initial stakeholder meeting to define campaign objectives, target audience, and key performance indicators for the product launch campaign.',
                    'priority': 'urgent',
                    'labels': ['Strategy', 'Client A'],
                    'progress': 10
                }
            ],
            1: [  # Strategy Development
                {
                    'title': 'Consumer Behavior Analysis & Market Research',
                    'description': 'Conduct comprehensive market research including competitor analysis, consumer surveys, and trend identification to inform campaign strategy.',
                    'priority': 'high',
                    'labels': ['Strategy'],
                    'progress': 45
                },
                {
                    'title': 'Multi-Channel Campaign Architecture',
                    'description': 'Design integrated campaign across social media, traditional advertising, influencer partnerships, and content marketing channels.',
                    'priority': 'high',
                    'labels': ['Strategy', 'Campaign'],
                    'progress': 30
                }
            ],
            2: [  # Creative Production
                {
                    'title': 'Video Content Creation for Social Platforms',
                    'description': 'Produce 15-second Instagram Reels, 30-second TikTok videos, and 60-second YouTube shorts with brand messaging optimization.',
                    'priority': 'medium',
                    'labels': ['Creative', 'Social Media'],
                    'progress': 65
                },
                {
                    'title': 'Interactive Landing Page Design',
                    'description': 'Design and develop conversion-optimized landing pages with A/B testing capabilities and analytics integration.',
                    'priority': 'high',
                    'labels': ['Creative'],
                    'progress': 50
                }
            ],
            3: [  # Client Review
                {
                    'title': 'Campaign Creative Presentation Deck',
                    'description': 'Prepare comprehensive presentation showcasing all creative assets, campaign timeline, and expected ROI projections.',
                    'priority': 'urgent',
                    'labels': ['Client B'],
                    'progress': 80
                }
            ],
            4: [  # Revisions
                {
                    'title': 'Brand Guideline Compliance Updates',
                    'description': 'Revise creative materials to align with updated brand guidelines and stakeholder feedback.',
                    'priority': 'medium',
                    'labels': ['Creative', 'Client C'],
                    'progress': 35
                }
            ],
            5: [  # Approval
                {
                    'title': 'Legal & Compliance Review',
                    'description': 'Final legal review of all campaign materials to ensure regulatory compliance and trademark clearance.',
                    'priority': 'high',
                    'labels': ['Client A'],
                    'progress': 90
                }
            ],
            6: [  # Launch
                {
                    'title': 'Cross-Platform Campaign Launch',
                    'description': 'Coordinate simultaneous launch across all platforms with real-time monitoring and optimization.',
                    'priority': 'urgent',
                    'labels': ['Campaign', 'Social Media'],
                    'progress': 95
                }
            ],
            7: [  # Performance Tracking
                {
                    'title': 'Weekly Performance Analytics Report',
                    'description': 'Comprehensive analysis of campaign metrics including reach, engagement, conversions, and ROI calculations.',
                    'priority': 'medium',
                    'labels': ['Client B'],
                    'progress': 100
                }
            ]
        }
        
        self.create_tasks_from_data(board, columns, tasks_by_column, user)

    def create_enterprise_it_tasks(self, board, columns, user):
        """Create enterprise IT specific tasks"""
        tasks_by_column = {
            0: [  # Assessment
                {
                    'title': 'Legacy System Architecture Audit',
                    'description': 'Comprehensive assessment of current ERP system architecture, dependencies, data flows, and integration points to identify migration challenges.',
                    'priority': 'critical',
                    'labels': ['Critical', 'Migration'],
                    'progress': 20
                }
            ],
            1: [  # Planning
                {
                    'title': 'Cloud Infrastructure Design & Cost Analysis',
                    'description': 'Design AWS cloud architecture with disaster recovery, implement cost optimization strategies, and create detailed migration timeline.',
                    'priority': 'critical',
                    'labels': ['Infrastructure', 'Migration'],
                    'progress': 40
                },
                {
                    'title': 'Data Migration Strategy & Risk Assessment',
                    'description': 'Plan for migrating 15TB of historical data with zero data loss tolerance and minimal downtime requirements.',
                    'priority': 'critical',
                    'labels': ['Critical', 'Migration'],
                    'progress': 55
                }
            ],
            2: [  # Development
                {
                    'title': 'API Gateway & Microservices Architecture',
                    'description': 'Develop cloud-native API architecture to replace monolithic legacy system while maintaining backward compatibility.',
                    'priority': 'high',
                    'labels': ['Infrastructure'],
                    'progress': 35
                }
            ],
            3: [  # Testing
                {
                    'title': 'Load Testing for Enterprise Scale',
                    'description': 'Performance testing to ensure system can handle 50,000 concurrent users during peak business hours.',
                    'priority': 'critical',
                    'labels': ['Critical', 'Infrastructure'],
                    'progress': 70
                }
            ],
            4: [  # Staging
                {
                    'title': 'User Acceptance Testing with Department Heads',
                    'description': 'Coordinate UAT sessions with all department stakeholders to validate functionality and user experience.',
                    'priority': 'high',
                    'labels': ['Stakeholder Review'],
                    'progress': 85
                }
            ],
            5: [  # Migration
                {
                    'title': 'Production Migration Weekend Event',
                    'description': 'Execute 48-hour migration window with rollback procedures and 24/7 monitoring team standby.',
                    'priority': 'critical',
                    'labels': ['Critical', 'Migration'],
                    'progress': 95
                }
            ],
            6: [  # Validation
                {
                    'title': 'Post-Migration Security Compliance Audit',
                    'description': 'Comprehensive security validation and compliance documentation for SOC 2 Type II certification.',
                    'priority': 'critical',
                    'labels': ['Security', 'Compliance'],
                    'progress': 90
                }
            ],
            7: [  # Completed
                {
                    'title': 'Staff Training & Documentation Handover',
                    'description': 'Complete training program for 200+ staff members and comprehensive documentation delivery.',
                    'priority': 'medium',
                    'labels': ['Documentation'],
                    'progress': 100
                }
            ]
        }
        
        self.create_tasks_from_data(board, columns, tasks_by_column, user)

    def create_tasks_from_data(self, board, columns, tasks_by_column, user):
        """Helper to create tasks from structured data"""
        labels = {label.name: label for label in board.labels.all()}
        
        for column_index, tasks_data in tasks_by_column.items():
            if column_index < len(columns):
                column = columns[column_index]
                
                for i, task_data in enumerate(tasks_data):
                    # Create realistic due dates
                    base_date = timezone.now()
                    if column_index < 3:  # Earlier columns get future dates
                        days_ahead = random.randint(7, 30)
                        due_date = base_date + timedelta(days=days_ahead)
                    elif column_index < 6:  # Middle columns get closer dates
                        days_ahead = random.randint(1, 14)
                        due_date = base_date + timedelta(days=days_ahead)
                    else:  # Later columns may be overdue or completed
                        days_past = random.randint(-7, 7)
                        due_date = base_date + timedelta(days=days_past)
                    
                    task = Task.objects.create(
                        title=task_data['title'],
                        description=task_data['description'],
                        column=column,
                        position=i,
                        created_by=user,
                        priority=task_data['priority'],
                        progress=task_data['progress'],
                        due_date=due_date,
                        # Add some AI-enhanced fields for demo
                        complexity_score=random.randint(3, 9),
                        ai_risk_score=random.randint(10, 75) if random.choice([True, False]) else None,
                    )
                    
                    # Add labels
                    for label_name in task_data['labels']:
                        if label_name in labels:
                            task.labels.add(labels[label_name])
                    
                    # Add some realistic comments for demonstration
                    self.add_demo_comments(task, user)

    def add_demo_comments(self, task, user):
        """Add realistic comments to tasks for demo purposes"""
        comment_templates = [
            "Updated the implementation approach based on the latest requirements. The new solution should be more scalable.",
            "Encountered some integration challenges with the third-party API. Working on a workaround.",
            "Great progress on this! The UI looks much cleaner now. Ready for stakeholder review.",
            "Added comprehensive test coverage. All edge cases are now properly handled.",
            "Performance benchmarks look excellent. This optimization reduced response time by 40%.",
            "Collaborating with the design team to ensure brand consistency across all touchpoints.",
            "Security review completed. Implemented additional encryption for sensitive data.",
            "Documentation updated with the new API endpoints and usage examples.",
        ]
        
        # Add 1-3 comments per task randomly
        num_comments = random.randint(0, 3)
        for i in range(num_comments):
            Comment.objects.create(
                task=task,
                user=user,
                content=random.choice(comment_templates),
                created_at=timezone.now() - timedelta(days=random.randint(1, 10))
            )

    def create_demo_team_members(self, user, scenario):
        """Create demo team members for collaborative scenario"""
        try:
            organization = user.profile.organization
        except UserProfile.DoesNotExist:
            return
        
        if scenario == 'tech_startup':
            team_data = [
                {'username': 'sarah_dev', 'first_name': 'Sarah', 'last_name': 'Chen', 'email': 'sarah@demo.com', 'role': 'Senior Developer'},
                {'username': 'mike_qa', 'first_name': 'Mike', 'last_name': 'Johnson', 'email': 'mike@demo.com', 'role': 'QA Engineer'},
                {'username': 'alex_devops', 'first_name': 'Alex', 'last_name': 'Rodriguez', 'email': 'alex@demo.com', 'role': 'DevOps Engineer'},
                {'username': 'lisa_pm', 'first_name': 'Lisa', 'last_name': 'Wang', 'email': 'lisa@demo.com', 'role': 'Product Manager'},
            ]
        elif scenario == 'marketing_agency':
            team_data = [
                {'username': 'emily_creative', 'first_name': 'Emily', 'last_name': 'Davis', 'email': 'emily@demo.com', 'role': 'Creative Director'},
                {'username': 'james_strategy', 'first_name': 'James', 'last_name': 'Miller', 'email': 'james@demo.com', 'role': 'Strategy Lead'},
                {'username': 'maria_social', 'first_name': 'Maria', 'last_name': 'Garcia', 'email': 'maria@demo.com', 'role': 'Social Media Manager'},
                {'username': 'david_analytics', 'first_name': 'David', 'last_name': 'Kim', 'email': 'david@demo.com', 'role': 'Analytics Specialist'},
            ]
        else:  # enterprise_it
            team_data = [
                {'username': 'robert_architect', 'first_name': 'Robert', 'last_name': 'Thompson', 'email': 'robert@demo.com', 'role': 'Solution Architect'},
                {'username': 'jennifer_security', 'first_name': 'Jennifer', 'last_name': 'Lee', 'email': 'jennifer@demo.com', 'role': 'Security Specialist'},
                {'username': 'william_dba', 'first_name': 'William', 'last_name': 'Brown', 'email': 'william@demo.com', 'role': 'Database Administrator'},
                {'username': 'michelle_pm', 'first_name': 'Michelle', 'last_name': 'Wilson', 'email': 'michelle@demo.com', 'role': 'Project Manager'},
            ]
        
        # Create team members if they don't exist
        for member_data in team_data:
            team_user, created = User.objects.get_or_create(
                username=member_data['username'],
                defaults={
                    'first_name': member_data['first_name'],
                    'last_name': member_data['last_name'],
                    'email': member_data['email'],
                    'is_active': True
                }
            )
            
            if created:
                team_user.set_password('demo123')
                team_user.save()
            
            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(
                user=team_user,
                defaults={
                    'organization': organization,
                    'is_admin': False
                }
            )

    def clear_demo_data(self, user):
        """Clear all demo data for a user"""
        try:
            profile = user.profile
            organization = profile.organization
            
            # Delete all boards created by this user
            boards = Board.objects.filter(created_by=user, organization=organization)
            board_count = boards.count()
            boards.delete()
            
            self.stdout.write(f"✅ Cleared {board_count} demo boards")
            
            # Delete demo team members (only if they have no other activity)
            demo_usernames = [
                'sarah_dev', 'mike_qa', 'alex_devops', 'lisa_pm',
                'emily_creative', 'james_strategy', 'maria_social', 'david_analytics',
                'robert_architect', 'jennifer_security', 'william_dba', 'michelle_pm'
            ]
            
            deleted_users = 0
            for username in demo_usernames:
                try:
                    demo_user = User.objects.get(username=username)
                    # Only delete if they have no created boards
                    if not Board.objects.filter(created_by=demo_user).exists():
                        demo_user.delete()
                        deleted_users += 1
                except User.DoesNotExist:
                    pass
            
            self.stdout.write(f"✅ Cleared {deleted_users} demo team members")
            
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR("User profile not found"))
