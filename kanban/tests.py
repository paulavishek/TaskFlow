from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Board, Column, Task, TaskLabel, Comment, TaskActivity
from accounts.models import Organization, UserProfile # Assuming you have these models

class KanbanModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.organization = Organization.objects.create(name='Test Org', owner=self.user)
        UserProfile.objects.create(user=self.user, organization=self.organization)
        self.board = Board.objects.create(name='Test Board', organization=self.organization, created_by=self.user)
        self.column = Column.objects.create(name='To Do', board=self.board, position=0)

    def test_board_creation(self):
        self.assertEqual(self.board.name, 'Test Board')
        self.assertEqual(self.board.organization, self.organization)
        self.assertEqual(self.board.created_by, self.user)
        self.assertEqual(str(self.board), 'Test Board')

    def test_column_creation(self):
        self.assertEqual(self.column.name, 'To Do')
        self.assertEqual(self.column.board, self.board)
        self.assertEqual(str(self.column), f'{self.column.name} - {self.board.name}')

    def test_task_creation(self):
        task = Task.objects.create(
            title='Test Task',
            column=self.column,
            created_by=self.user,
            priority='medium'
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.column, self.column)
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.priority, 'medium')
        self.assertEqual(str(task), 'Test Task')

    def test_task_label_creation(self):
        label = TaskLabel.objects.create(name='Urgent', board=self.board, color='#FF0000')
        self.assertEqual(label.name, 'Urgent')
        self.assertEqual(label.board, self.board)
        self.assertEqual(label.color, '#FF0000')
        self.assertEqual(str(label), 'Urgent')

    def test_comment_creation(self):
        task = Task.objects.create(title='Task for Comment', column=self.column, created_by=self.user)
        comment = Comment.objects.create(task=task, user=self.user, content='This is a test comment.')
        self.assertEqual(comment.task, task)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'This is a test comment.')
        self.assertEqual(str(comment), f'Comment by {self.user.username} on {task.title}')

    def test_task_activity_creation(self):
        task = Task.objects.create(title='Task for Activity', column=self.column, created_by=self.user)
        activity = TaskActivity.objects.create(
            task=task,
            user=self.user,
            activity_type='created',
            description='Task was created'
        )
        self.assertEqual(activity.task, task)
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'created')
        self.assertEqual(str(activity), f'{activity.activity_type} by {self.user.username} on {task.title}')


class KanbanViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password', email='test@example.com')
        self.organization = Organization.objects.create(name='Test Org View', owner=self.user)
        self.user_profile = UserProfile.objects.create(user=self.user, organization=self.organization)
        self.board = Board.objects.create(name='View Test Board', organization=self.organization, created_by=self.user)
        self.board.members.add(self.user) # Add user as a member
        self.column = Column.objects.create(name='To Do View', board=self.board, position=0)
        self.client.login(username='testuser', password='password')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/dashboard.html')

    def test_board_list_view_get(self):
        response = self.client.get(reverse('board_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/board_list.html')

    def test_board_detail_view_get(self):
        response = self.client.get(reverse('board_detail', args=[self.board.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/board_detail.html')

    def test_board_creation_post(self):
        response = self.client.post(reverse('board_list'), {
            'name': 'New Test Board',
            'description': 'A board created via test.'
        })
        # Expect a redirect after successful creation
        self.assertEqual(response.status_code, 302) 
        new_board = Board.objects.get(name='New Test Board')
        self.assertIsNotNone(new_board)
        self.assertTrue(self.user in new_board.members.all())

    def test_create_task_view_get(self):
        response = self.client.get(reverse('create_task', args=[self.board.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/create_task.html')

    def test_create_task_post(self):
        task_data = {
            'title': 'New Task via Test',
            'description': 'Task description.',
            'priority': 'high',
            'column': self.column.id, # Pass column ID
            # 'assigned_to': self.user.id, # Optional: assign to user
            # 'labels': [] # Optional: add labels if you have a form field for it
        }
        response = self.client.post(reverse('create_task_in_column', args=[self.board.id, self.column.id]), task_data)
        self.assertEqual(response.status_code, 302) # Redirects to board_detail
        new_task = Task.objects.get(title='New Task via Test')
        self.assertIsNotNone(new_task)
        self.assertEqual(new_task.column, self.column)
        self.assertEqual(new_task.created_by, self.user)

    def test_task_detail_view(self):
        task = Task.objects.create(title='Detail Test Task', column=self.column, created_by=self.user)
        response = self.client.get(reverse('task_detail', args=[task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kanban/task_detail.html')

class KanbanURLTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='urluser', password='password')
        self.organization = Organization.objects.create(name='Test Org URL', owner=self.user)
        UserProfile.objects.create(user=self.user, organization=self.organization)
        self.board = Board.objects.create(name='URL Test Board', organization=self.organization, created_by=self.user)
        self.column = Column.objects.create(name='URL Column', board=self.board, position=0)
        self.task = Task.objects.create(title='URL Task', column=self.column, created_by=self.user)

    def test_dashboard_url_resolves(self):
        url = reverse('dashboard')
        self.assertEqual(url, '/') # Assuming dashboard is at root of kanban app

    def test_board_list_url_resolves(self):
        url = reverse('board_list')
        self.assertEqual(url, '/boards/')

    def test_board_detail_url_resolves(self):
        url = reverse('board_detail', args=[self.board.id])
        self.assertEqual(url, f'/boards/{self.board.id}/')

    def test_create_task_url_resolves(self):
        url = reverse('create_task', args=[self.board.id])
        self.assertEqual(url, f'/boards/{self.board.id}/create-task/')
        
    def test_create_task_in_column_url_resolves(self):
        url = reverse('create_task_in_column', args=[self.board.id, self.column.id])
        self.assertEqual(url, f'/boards/{self.board.id}/columns/{self.column.id}/create-task/')

    def test_task_detail_url_resolves(self):
        url = reverse('task_detail', args=[self.task.id])
        self.assertEqual(url, f'/tasks/{self.task.id}/')

# Note: You might need to adjust imports or model field names based on your exact project structure.
# Remember to create UserProfile for users in tests if your views depend on it.
# For views requiring login, ensure self.client.login() is called in setUp.
