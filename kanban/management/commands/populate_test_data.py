import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Organization, UserProfile
from kanban.models import Board, Column, TaskLabel, Task, Comment, TaskActivity

class Command(BaseCommand):
    help = 'Populate the database with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting to populate database with test data...'))

        # Create test users if they don't exist
        self.create_users()
        
        # Create test organizations
        self.create_organizations()
        
        # Create test boards with columns, labels, tasks, and comments
        self.create_boards_and_content()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated the database!'))
        
        # Print login credentials for easy testing
        self.stdout.write(self.style.SUCCESS('You can now log in with the following credentials:'))
        self.stdout.write(self.style.SUCCESS('Username: admin, Password: admin123'))
        self.stdout.write(self.style.SUCCESS('Username: john_doe, Password: test1234'))
        self.stdout.write(self.style.SUCCESS('Username: jane_smith, Password: test1234'))
        self.stdout.write(self.style.SUCCESS('Username: robert_johnson, Password: test1234'))

    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@taskflow.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created admin user: {admin_user.username}')
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write('Admin user already exists')
        
        # Create regular users
        test_users = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'test1234',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'test1234',
                'first_name': 'Jane',
                'last_name': 'Smith'
            },
            {
                'username': 'robert_johnson',
                'email': 'robert@example.com',
                'password': 'test1234',
                'first_name': 'Robert',
                'last_name': 'Johnson'
            }
        ]
        
        self.users = {}
        for user_data in test_users:
            username = user_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                self.stdout.write(f'Created user: {user.username}')
            else:
                user = User.objects.get(username=username)
                self.stdout.write(f'User {user.username} already exists')
            
            self.users[username] = user
        
        # Add admin to users dictionary
        self.users['admin'] = admin_user

    def create_organizations(self):
        self.stdout.write('Creating organizations...')
        
        # Create dev team organization
        if not Organization.objects.filter(name='Dev Team').exists():
            dev_org = Organization.objects.create(
                name='Dev Team',
                domain='devteam.com',
                created_by=self.users['admin']
            )
            self.stdout.write(f'Created organization: {dev_org.name}')
        else:
            dev_org = Organization.objects.get(name='Dev Team')
            self.stdout.write(f'Organization {dev_org.name} already exists')
        
        # Create second organization
        if not Organization.objects.filter(name='Marketing Team').exists():
            marketing_org = Organization.objects.create(
                name='Marketing Team',
                domain='marketingteam.com',
                created_by=self.users['jane_smith']
            )
            self.stdout.write(f'Created organization: {marketing_org.name}')
        else:
            marketing_org = Organization.objects.get(name='Marketing Team')
            self.stdout.write(f'Organization {marketing_org.name} already exists')
        
        # Store organizations
        self.organizations = {
            'dev': dev_org,
            'marketing': marketing_org
        }
        
        # Create profiles for users if they don't exist
        for username, user in self.users.items():
            if not hasattr(user, 'profile'):
                # Assign users to organizations
                if username in ['admin', 'john_doe', 'robert_johnson']:
                    org = dev_org
                else:
                    org = marketing_org
                
                is_admin = username in ['admin', 'jane_smith']
                
                profile = UserProfile.objects.create(
                    user=user,
                    organization=org,
                    is_admin=is_admin
                )
                self.stdout.write(f'Created profile for: {user.username} in {org.name}')
            else:
                self.stdout.write(f'Profile for {user.username} already exists')

    def create_boards_and_content(self):
        self.stdout.write('Creating boards, columns, labels, and tasks...')
        
        # Create boards for Dev Team
        self.create_software_project_board()
        self.create_bug_tracking_board()
        
        # Create board for Marketing Team
        self.create_marketing_campaign_board()

    def create_software_project_board(self):
        # Create Software Project board if it doesn't exist
        if not Board.objects.filter(name='Software Project').exists():
            board = Board.objects.create(
                name='Software Project',
                description='Main product development board with Lean Six Sigma features',
                organization=self.organizations['dev'],
                created_by=self.users['admin']
            )
            self.stdout.write(f'Created board: {board.name}')
            
            # Add members
            board.members.add(self.users['john_doe'], self.users['robert_johnson'])
            
            # Create columns
            columns = [
                {'name': 'Backlog', 'position': 0},
                {'name': 'To Do', 'position': 1},
                {'name': 'In Progress', 'position': 2},
                {'name': 'Review', 'position': 3},
                {'name': 'Done', 'position': 4}
            ]
            
            board_columns = {}
            for col_data in columns:
                column = Column.objects.create(
                    name=col_data['name'],
                    board=board,
                    position=col_data['position']
                )
                board_columns[col_data['name']] = column
                self.stdout.write(f'Created column: {column.name}')
            
            # Create Lean Six Sigma labels
            lean_labels = [
                {'name': 'Value-Added', 'color': '#28a745', 'category': 'lean'},
                {'name': 'Necessary NVA', 'color': '#ffc107', 'category': 'lean'},
                {'name': 'Waste/Eliminate', 'color': '#dc3545', 'category': 'lean'}
            ]
            
            board_lean_labels = {}
            for label_data in lean_labels:
                label = TaskLabel.objects.create(
                    name=label_data['name'],
                    color=label_data['color'],
                    board=board,
                    category=label_data['category']
                )
                board_lean_labels[label_data['name']] = label
                self.stdout.write(f'Created label: {label.name}')
            
            # Create regular labels
            regular_labels = [
                {'name': 'Front-end', 'color': '#17a2b8'},
                {'name': 'Back-end', 'color': '#6f42c1'},
                {'name': 'Bug', 'color': '#dc3545'},
                {'name': 'Feature', 'color': '#28a745'},
                {'name': 'Documentation', 'color': '#6c757d'}
            ]
            
            board_regular_labels = {}
            for label_data in regular_labels:
                label = TaskLabel.objects.create(
                    name=label_data['name'],
                    color=label_data['color'],
                    board=board,
                    category='regular'
                )
                board_regular_labels[label_data['name']] = label
                self.stdout.write(f'Created label: {label.name}')
            
            # Create tasks for backlog
            backlog_tasks = [
                {
                    'title': 'Implement user authentication',
                    'description': 'Add login, registration, and password reset functionality',
                    'priority': 'high',
                    'due_date': timezone.now() + timedelta(days=7),
                    'progress': 0,
                    'created_by': self.users['admin'],
                    'assigned_to': self.users['john_doe'],
                    'labels': [board_regular_labels['Back-end'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Design database schema',
                    'description': 'Create ER diagrams and plan the database structure',
                    'priority': 'high',
                    'due_date': timezone.now() + timedelta(days=5),
                    'progress': 0,
                    'created_by': self.users['admin'],
                    'assigned_to': self.users['robert_johnson'],
                    'labels': [board_regular_labels['Back-end'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Setup CI/CD pipeline',
                    'description': 'Configure GitHub Actions for automated testing and deployment',
                    'priority': 'medium',
                    'due_date': timezone.now() + timedelta(days=10),
                    'progress': 0,
                    'created_by': self.users['robert_johnson'],
                    'assigned_to': None,
                    'labels': [board_lean_labels['Necessary NVA']]
                }
            ]
            
            self.create_tasks(backlog_tasks, board_columns['Backlog'])
            
            # Create tasks for To Do
            todo_tasks = [
                {
                    'title': 'Create component library',
                    'description': 'Develop reusable UI components for the application',
                    'priority': 'medium',
                    'due_date': timezone.now() + timedelta(days=8),
                    'progress': 0,
                    'created_by': self.users['admin'],
                    'assigned_to': self.users['john_doe'],
                    'labels': [board_regular_labels['Front-end'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Write documentation for API endpoints',
                    'description': 'Document all API endpoints with examples and response formats',
                    'priority': 'low',
                    'due_date': timezone.now() + timedelta(days=15),
                    'progress': 0,
                    'created_by': self.users['robert_johnson'],
                    'assigned_to': self.users['robert_johnson'],
                    'labels': [board_regular_labels['Documentation'], board_lean_labels['Necessary NVA']]
                }
            ]
            
            self.create_tasks(todo_tasks, board_columns['To Do'])
            
            # Create tasks for In Progress
            in_progress_tasks = [
                {
                    'title': 'Implement dashboard layout',
                    'description': 'Create the main dashboard layout with sidebar and main content area',
                    'priority': 'high',
                    'due_date': timezone.now() + timedelta(days=3),
                    'progress': 30,
                    'created_by': self.users['john_doe'],
                    'assigned_to': self.users['john_doe'],
                    'labels': [board_regular_labels['Front-end'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Setup authentication middleware',
                    'description': 'Create middleware for JWT token validation and user authentication',
                    'priority': 'urgent',
                    'due_date': timezone.now() + timedelta(days=2),
                    'progress': 65,
                    'created_by': self.users['admin'],
                    'assigned_to': self.users['robert_johnson'],
                    'labels': [board_regular_labels['Back-end'], board_lean_labels['Value-Added']]
                }
            ]
            
            self.create_tasks(in_progress_tasks, board_columns['In Progress'])
            
            # Create tasks for Review
            review_tasks = [
                {
                    'title': 'Review homepage design',
                    'description': 'Review and provide feedback on the new homepage design',
                    'priority': 'medium',
                    'due_date': timezone.now() + timedelta(days=1),
                    'progress': 90,
                    'created_by': self.users['john_doe'],
                    'assigned_to': self.users['admin'],
                    'labels': [board_regular_labels['Front-end'], board_lean_labels['Necessary NVA']]
                }
            ]
            
            self.create_tasks(review_tasks, board_columns['Review'])
            
            # Create tasks for Done
            done_tasks = [
                {
                    'title': 'Setup project repository',
                    'description': 'Create GitHub repository and initial project structure',
                    'priority': 'high',
                    'due_date': timezone.now() - timedelta(days=5),
                    'progress': 100,
                    'created_by': self.users['admin'],
                    'assigned_to': self.users['admin'],
                    'labels': [board_lean_labels['Necessary NVA']]
                },
                {
                    'title': 'Create UI mockups',
                    'description': 'Design UI mockups for the main application screens',
                    'priority': 'medium',
                    'due_date': timezone.now() - timedelta(days=8),
                    'progress': 100,
                    'created_by': self.users['john_doe'],
                    'assigned_to': self.users['john_doe'],
                    'labels': [board_regular_labels['Front-end'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Remove legacy code',
                    'description': 'Remove deprecated functions and clean up the codebase',
                    'priority': 'low',
                    'due_date': timezone.now() - timedelta(days=2),
                    'progress': 100,
                    'created_by': self.users['robert_johnson'],
                    'assigned_to': self.users['robert_johnson'],
                    'labels': [board_lean_labels['Waste/Eliminate']]
                }
            ]
            
            self.create_tasks(done_tasks, board_columns['Done'])
            
        else:
            self.stdout.write('Software Project board already exists')

    def create_bug_tracking_board(self):
        # Create Bug Tracking board if it doesn't exist
        if not Board.objects.filter(name='Bug Tracking').exists():
            board = Board.objects.create(
                name='Bug Tracking',
                description='Track and manage bugs and issues',
                organization=self.organizations['dev'],
                created_by=self.users['robert_johnson']
            )
            self.stdout.write(f'Created board: {board.name}')
            
            # Add members
            board.members.add(self.users['admin'], self.users['john_doe'])
            
            # Create columns
            columns = [
                {'name': 'New', 'position': 0},
                {'name': 'Investigating', 'position': 1},
                {'name': 'In Progress', 'position': 2},
                {'name': 'Testing', 'position': 3},
                {'name': 'Closed', 'position': 4}
            ]
            
            board_columns = {}
            for col_data in columns:
                column = Column.objects.create(
                    name=col_data['name'],
                    board=board,
                    position=col_data['position']
                )
                board_columns[col_data['name']] = column
                self.stdout.write(f'Created column: {column.name}')
            
            # Create Lean Six Sigma labels
            lean_labels = [
                {'name': 'Value-Added', 'color': '#28a745', 'category': 'lean'},
                {'name': 'Necessary NVA', 'color': '#ffc107', 'category': 'lean'},
                {'name': 'Waste/Eliminate', 'color': '#dc3545', 'category': 'lean'}
            ]
            
            board_lean_labels = {}
            for label_data in lean_labels:
                label = TaskLabel.objects.create(
                    name=label_data['name'],
                    color=label_data['color'],
                    board=board,
                    category=label_data['category']
                )
                board_lean_labels[label_data['name']] = label
                self.stdout.write(f'Created label: {label.name}')
            
            # Create regular labels
            regular_labels = [
                {'name': 'Critical', 'color': '#dc3545'},
                {'name': 'Major', 'color': '#fd7e14'},
                {'name': 'Minor', 'color': '#ffc107'},
                {'name': 'UI/UX', 'color': '#20c997'},
                {'name': 'Backend', 'color': '#6610f2'},
                {'name': 'Performance', 'color': '#17a2b8'}
            ]
            
            board_regular_labels = {}
            for label_data in regular_labels:
                label = TaskLabel.objects.create(
                    name=label_data['name'],
                    color=label_data['color'],
                    board=board,
                    category='regular'
                )
                board_regular_labels[label_data['name']] = label
                self.stdout.write(f'Created label: {label.name}')
            
            # Create tasks for New
            new_bugs = [
                {
                    'title': 'Login page not working on Safari',
                    'description': 'Users report they cannot login when using Safari browser',
                    'priority': 'high',
                    'due_date': timezone.now() + timedelta(days=2),
                    'progress': 0,
                    'created_by': self.users['john_doe'],
                    'assigned_to': None,
                    'labels': [board_regular_labels['Critical'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Slow response time on search feature',
                    'description': 'Search feature takes more than 5 seconds to return results',
                    'priority': 'medium',
                    'due_date': timezone.now() + timedelta(days=5),
                    'progress': 0,
                    'created_by': self.users['robert_johnson'],
                    'assigned_to': None,
                    'labels': [board_regular_labels['Performance'], board_lean_labels['Value-Added']]
                }
            ]
            
            self.create_tasks(new_bugs, board_columns['New'])
            
            # Create tasks for Investigating
            investigating_bugs = [
                {
                    'title': 'Inconsistent data in reports',
                    'description': 'Reports sometimes show different totals for the same data',
                    'priority': 'high',
                    'due_date': timezone.now() + timedelta(days=3),
                    'progress': 20,
                    'created_by': self.users['admin'],
                    'assigned_to': self.users['robert_johnson'],
                    'labels': [board_regular_labels['Major'], board_regular_labels['Backend'], board_lean_labels['Value-Added']]
                }
            ]
            
            self.create_tasks(investigating_bugs, board_columns['Investigating'])
            
            # Create tasks for In Progress
            in_progress_bugs = [
                {
                    'title': 'Button alignment issue on mobile',
                    'description': 'Save and Cancel buttons are misaligned on mobile view',
                    'priority': 'low',
                    'due_date': timezone.now() + timedelta(days=7),
                    'progress': 50,
                    'created_by': self.users['john_doe'],
                    'assigned_to': self.users['john_doe'],
                    'labels': [board_regular_labels['Minor'], board_regular_labels['UI/UX'], board_lean_labels['Necessary NVA']]
                }
            ]
            
            self.create_tasks(in_progress_bugs, board_columns['In Progress'])
            
            # Create tasks for Testing
            testing_bugs = [
                {
                    'title': 'Fixed pagination on user list',
                    'description': 'Fixed bug where pagination showed incorrect number of pages',
                    'priority': 'medium',
                    'due_date': timezone.now() + timedelta(days=1),
                    'progress': 90,
                    'created_by': self.users['robert_johnson'],
                    'assigned_to': self.users['admin'],
                    'labels': [board_regular_labels['Minor'], board_lean_labels['Value-Added']]
                }
            ]
            
            self.create_tasks(testing_bugs, board_columns['Testing'])
            
            # Create tasks for Closed
            closed_bugs = [
                {
                    'title': 'Error 500 when uploading large files',
                    'description': 'Server returns 500 error when uploading files larger than 10MB',
                    'priority': 'urgent',
                    'due_date': timezone.now() - timedelta(days=3),
                    'progress': 100,
                    'created_by': self.users['admin'],
                    'assigned_to': self.users['robert_johnson'],
                    'labels': [board_regular_labels['Critical'], board_regular_labels['Backend'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Typo on welcome screen',
                    'description': 'The welcome message has a spelling mistake',
                    'priority': 'low',
                    'due_date': timezone.now() - timedelta(days=5),
                    'progress': 100,
                    'created_by': self.users['john_doe'],
                    'assigned_to': self.users['john_doe'],
                    'labels': [board_regular_labels['Minor'], board_lean_labels['Waste/Eliminate']]
                }
            ]
            
            self.create_tasks(closed_bugs, board_columns['Closed'])
            
        else:
            self.stdout.write('Bug Tracking board already exists')

    def create_marketing_campaign_board(self):
        # Create Marketing Campaign board if it doesn't exist
        if not Board.objects.filter(name='Marketing Campaign').exists():
            board = Board.objects.create(
                name='Marketing Campaign',
                description='Plan and track marketing campaigns',
                organization=self.organizations['marketing'],
                created_by=self.users['jane_smith']
            )
            self.stdout.write(f'Created board: {board.name}')
            
            # Add members (just jane_smith for now)
            
            # Create columns
            columns = [
                {'name': 'Ideas', 'position': 0},
                {'name': 'Planning', 'position': 1},
                {'name': 'In Progress', 'position': 2},
                {'name': 'Review', 'position': 3},
                {'name': 'Completed', 'position': 4}
            ]
            
            board_columns = {}
            for col_data in columns:
                column = Column.objects.create(
                    name=col_data['name'],
                    board=board,
                    position=col_data['position']
                )
                board_columns[col_data['name']] = column
                self.stdout.write(f'Created column: {column.name}')
            
            # Create Lean Six Sigma labels
            lean_labels = [
                {'name': 'Value-Added', 'color': '#28a745', 'category': 'lean'},
                {'name': 'Necessary NVA', 'color': '#ffc107', 'category': 'lean'},
                {'name': 'Waste/Eliminate', 'color': '#dc3545', 'category': 'lean'}
            ]
            
            board_lean_labels = {}
            for label_data in lean_labels:
                label = TaskLabel.objects.create(
                    name=label_data['name'],
                    color=label_data['color'],
                    board=board,
                    category=label_data['category']
                )
                board_lean_labels[label_data['name']] = label
                self.stdout.write(f'Created label: {label.name}')
            
            # Create regular labels
            regular_labels = [
                {'name': 'Social Media', 'color': '#007bff'},
                {'name': 'Email', 'color': '#6f42c1'},
                {'name': 'Content', 'color': '#fd7e14'},
                {'name': 'Design', 'color': '#20c997'},
                {'name': 'Analytics', 'color': '#17a2b8'}
            ]
            
            board_regular_labels = {}
            for label_data in regular_labels:
                label = TaskLabel.objects.create(
                    name=label_data['name'],
                    color=label_data['color'],
                    board=board,
                    category='regular'
                )
                board_regular_labels[label_data['name']] = label
                self.stdout.write(f'Created label: {label.name}')
            
            # Create tasks for each column
            # Ideas
            ideas_tasks = [
                {
                    'title': 'Holiday social campaign concept',
                    'description': 'Brainstorm ideas for the upcoming holiday social media campaign',
                    'priority': 'medium',
                    'due_date': timezone.now() + timedelta(days=14),
                    'progress': 0,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Social Media'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Video content strategy',
                    'description': 'Explore video content ideas for product demonstrations',
                    'priority': 'low',
                    'due_date': timezone.now() + timedelta(days=21),
                    'progress': 0,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Content'], board_lean_labels['Value-Added']]
                }
            ]
            self.create_tasks(ideas_tasks, board_columns['Ideas'])
            
            # Planning
            planning_tasks = [
                {
                    'title': 'Q3 Email newsletter schedule',
                    'description': 'Create content calendar for Q3 email newsletters',
                    'priority': 'high',
                    'due_date': timezone.now() + timedelta(days=5),
                    'progress': 15,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Email'], board_lean_labels['Value-Added']]
                }
            ]
            self.create_tasks(planning_tasks, board_columns['Planning'])
            
            # In Progress
            in_progress_tasks = [
                {
                    'title': 'Website redesign for Q4 launch',
                    'description': 'Update website design to highlight new features',
                    'priority': 'high',
                    'due_date': timezone.now() + timedelta(days=10),
                    'progress': 40,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Design'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Monthly performance report',
                    'description': 'Compile social media and email campaign metrics for the month',
                    'priority': 'medium',
                    'due_date': timezone.now() + timedelta(days=3),
                    'progress': 60,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Analytics'], board_lean_labels['Necessary NVA']]
                }
            ]
            self.create_tasks(in_progress_tasks, board_columns['In Progress'])
            
            # Review
            review_tasks = [
                {
                    'title': 'New product announcement email',
                    'description': 'Email campaign for the upcoming product launch',
                    'priority': 'urgent',
                    'due_date': timezone.now() + timedelta(days=1),
                    'progress': 95,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Email'], board_lean_labels['Value-Added']]
                }
            ]
            self.create_tasks(review_tasks, board_columns['Review'])
            
            # Completed
            completed_tasks = [
                {
                    'title': 'Summer campaign graphics',
                    'description': 'Create social media graphics for summer campaign',
                    'priority': 'high',
                    'due_date': timezone.now() - timedelta(days=7),
                    'progress': 100,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Design'], board_regular_labels['Social Media'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Competitor analysis report',
                    'description': 'Research and document marketing strategies of main competitors',
                    'priority': 'medium',
                    'due_date': timezone.now() - timedelta(days=10),
                    'progress': 100,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Analytics'], board_lean_labels['Value-Added']]
                },
                {
                    'title': 'Remove outdated content',
                    'description': 'Archive or remove outdated content from the website',
                    'priority': 'low',
                    'due_date': timezone.now() - timedelta(days=3),
                    'progress': 100,
                    'created_by': self.users['jane_smith'],
                    'assigned_to': self.users['jane_smith'],
                    'labels': [board_regular_labels['Content'], board_lean_labels['Waste/Eliminate']]
                }
            ]
            self.create_tasks(completed_tasks, board_columns['Completed'])
            
        else:
            self.stdout.write('Marketing Campaign board already exists')

    def create_tasks(self, tasks_data, column):
        # Helper function to create tasks with comments and activity
        position = 0
        for task_data in tasks_data:
            task = Task.objects.create(
                title=task_data['title'],
                description=task_data['description'],
                column=column,
                position=position,
                due_date=task_data['due_date'],
                assigned_to=task_data['assigned_to'],
                created_by=task_data['created_by'],
                priority=task_data['priority'],
                progress=task_data['progress']
            )
            position += 1
            self.stdout.write(f'Created task: {task.title}')
            
            # Add labels
            if 'labels' in task_data:
                for label in task_data['labels']:
                    task.labels.add(label)
            
            # Create task activity
            TaskActivity.objects.create(
                task=task,
                user=task_data['created_by'],
                activity_type='created',
                description=f"Created task '{task.title}'"
            )
            
            # If assigned, create assignment activity
            if task_data['assigned_to']:
                TaskActivity.objects.create(
                    task=task,
                    user=task_data['created_by'],
                    activity_type='assigned',
                    description=f"Assigned to {task_data['assigned_to'].get_full_name() or task_data['assigned_to'].username}"
                )
            
            # Add some comments to random tasks (around 30% chance)
            if random.random() < 0.3:
                Comment.objects.create(
                    task=task,
                    user=task_data['created_by'],
                    content=f"Let's make sure we prioritize this correctly."
                )
                
                # Record comment activity
                TaskActivity.objects.create(
                    task=task,
                    user=task_data['created_by'],
                    activity_type='commented',
                    description=f"{task_data['created_by'].get_full_name() or task_data['created_by'].username} commented on this task"
                )
                
            if random.random() < 0.2 and task_data['assigned_to']:
                Comment.objects.create(
                    task=task,
                    user=task_data['assigned_to'],
                    content=f"I'll work on this as soon as possible."
                )
                
                # Record comment activity
                TaskActivity.objects.create(
                    task=task,
                    user=task_data['assigned_to'],
                    activity_type='commented',
                    description=f"{task_data['assigned_to'].get_full_name() or task_data['assigned_to'].username} commented on this task"
                )
