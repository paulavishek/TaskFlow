"""
Tests for AI-powered features in TaskFlow.

This module contains test cases for all AI features integrated with Google Generative AI (Gemini).
"""
import json
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from .models import Board, Column, Task, Comment
from accounts.models import Organization, UserProfile
from kanban.api_views import (
    generate_task_description_api, 
    summarize_comments_api,
    board_analytics_insights_api,
    suggest_lss_classification_api
)
from kanban.utils.ai_utils import (
    generate_task_description,
    summarize_comments,
    generate_analytics_insights,
    suggest_lean_classification
)


class AIUtilsTestCase(TestCase):
    """Test the AI utility functions directly."""
    
    @patch('kanban.utils.ai_utils.get_model')
    def test_generate_task_description(self, mock_get_model):
        """Test the task description generation function."""
        # Setup mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "**Objective:** Test objective\n\n**Checklist:**\n- [ ] Step 1\n- [ ] Step 2"
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # Call function
        result = generate_task_description("Test Task")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertIn("Objective", result)
        self.assertIn("Checklist", result)
        mock_model.generate_content.assert_called_once()
    
    @patch('kanban.utils.ai_utils.get_model')
    def test_summarize_comments(self, mock_get_model):
        """Test the comment summarization function."""
        # Setup mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a summary of the comments."
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # Test data
        comments = [
            {
                'user': 'user1',
                'content': 'First comment',
                'created_at': '2023-01-01 10:00'
            },
            {
                'user': 'user2',
                'content': 'Second comment',
                'created_at': '2023-01-02 11:00'
            }
        ]
        
        # Call function
        result = summarize_comments(comments)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result, "This is a summary of the comments.")
        mock_model.generate_content.assert_called_once()
    
    @patch('kanban.utils.ai_utils.get_model')
    def test_generate_analytics_insights(self, mock_get_model):
        """Test the analytics insights generation function."""
        # Setup mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Analytics insights: Performance is good."
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # Test data
        analytics_data = {
            'total_tasks': 10,
            'completed_tasks': 5,
            'in_progress': 3,
            'blocked': 2,
            'avg_completion_time': '2 days',
            'task_distribution': {'To Do': 2, 'In Progress': 3, 'Done': 5}
        }
        
        # Call function
        result = generate_analytics_insights(analytics_data)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result, "Analytics insights: Performance is good.")
        mock_model.generate_content.assert_called_once()
    
    @patch('kanban.utils.ai_utils.get_model')
    def test_suggest_lean_classification(self, mock_get_model):
        """Test the Lean Six Sigma classification suggestion function."""
        # Setup mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "classification": "Value-Added",
            "justification": "This task directly contributes to customer value."
        })
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # Call function
        result = suggest_lean_classification("Test title", "Test description")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertIn('classification', result)
        self.assertIn('justification', result)
        self.assertEqual(result['classification'], 'Value-Added')
        mock_model.generate_content.assert_called_once()
    
    @patch('kanban.utils.ai_utils.get_model')
    def test_error_handling_when_model_fails(self, mock_get_model):
        """Test error handling when the model fails."""
        # Setup mock to return None
        mock_get_model.return_value = None
        
        # Call functions and check they handle errors gracefully
        self.assertIsNone(generate_task_description("Test Task"))
        self.assertIsNone(summarize_comments([{'user': 'test', 'content': 'content', 'created_at': 'now'}]))
        self.assertIsNone(generate_analytics_insights({'total_tasks': 10}))
        self.assertIsNone(suggest_lean_classification("Test title", "Test description"))


class AIAPIViewsTestCase(TestCase):
    """Test the AI API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create an organization
        self.organization = Organization.objects.create(
            name='Test Org',
            domain='testorg.com',
            created_by=self.user
        )
        
        # Create user profile
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            organization=self.organization
        )
        
        # Create a board
        self.board = Board.objects.create(
            name='Test Board',
            organization=self.organization,
            created_by=self.user
        )
        
        # Create a column
        self.column = Column.objects.create(
            name='Test Column',
            board=self.board
        )
        
        # Create a task
        self.task = Task.objects.create(
            title='Test Task',
            column=self.column,
            created_by=self.user
        )
        
        # Create some comments
        self.comment1 = Comment.objects.create(
            task=self.task,
            user=self.user,
            content='This is the first comment'
        )
        self.comment2 = Comment.objects.create(
            task=self.task,
            user=self.user,
            content='This is the second comment'
        )
        
        # Setup the request factory
        self.factory = RequestFactory()
    
    @patch('kanban.api_views.generate_task_description')
    def test_generate_task_description_api(self, mock_generate):
        """Test the task description generation API."""
        # Setup mock
        mock_generate.return_value = "**Objective:** Test objective\n\n**Checklist:**\n- [ ] Step 1\n- [ ] Step 2"
        
        # Create request
        url = reverse('generate_task_description_api')
        request = self.factory.post(
            url,
            data=json.dumps({'title': 'Test Task'}),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call the API view
        response = generate_task_description_api(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('description', content)
        self.assertIn('Objective', content['description'])
        mock_generate.assert_called_once_with('Test Task')
    
    @patch('kanban.api_views.summarize_comments')
    def test_summarize_comments_api(self, mock_summarize):
        """Test the comment summarization API."""
        # Setup mock
        mock_summarize.return_value = "Summary of comments"
        
        # Create request
        url = reverse('summarize_comments_api', kwargs={'task_id': self.task.id})
        request = self.factory.get(url)
        request.user = self.user
        
        # Call the API view
        response = summarize_comments_api(request, self.task.id)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('summary', content)
        self.assertEqual(content['summary'], "Summary of comments")
        mock_summarize.assert_called_once()
    
    @patch('kanban.api_views.generate_analytics_insights')
    def test_board_analytics_insights_api(self, mock_insights):
        """Test the board analytics insights API."""
        # Setup mock
        mock_insights.return_value = "Analytics insights: Workflow is efficient."
        
        # Create request
        url = reverse('board_analytics_insights_api', kwargs={'board_id': self.board.id})
        request = self.factory.get(url)
        request.user = self.user
        
        # Call the API view
        response = board_analytics_insights_api(request, self.board.id)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('insights', content)
        self.assertEqual(content['insights'], "Analytics insights: Workflow is efficient.")
        mock_insights.assert_called_once()
    
    @patch('kanban.api_views.suggest_lean_classification')
    def test_suggest_lean_classification_api(self, mock_classify):
        """Test the LSS classification API."""
        # Setup mock
        mock_classify.return_value = {
            "classification": "Value-Added",
            "justification": "This task directly contributes to customer value."
        }
        
        # Create request
        url = reverse('suggest_lss_classification_api')
        request = self.factory.post(
            url,
            data=json.dumps({
                'title': 'Test Task',
                'description': 'Test description'
            }),
            content_type='application/json'
        )
        request.user = self.user
        
        # Call the API view
        response = suggest_lss_classification_api(request)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('classification', content)
        self.assertIn('justification', content)
        mock_classify.assert_called_once()
    
    def test_api_authentication_required(self):
        """Test that API endpoints require authentication."""
        # Create an anonymous user
        from django.contrib.auth.models import AnonymousUser
        anonymous = AnonymousUser()
        
        # Test task description API
        url = reverse('generate_task_description_api')
        request = self.factory.post(
            url,
            data=json.dumps({'title': 'Test Task'}),
            content_type='application/json'
        )
        request.user = anonymous
        
        # This should redirect to login since @login_required is used
        response = generate_task_description_api(request)
        self.assertEqual(response.status_code, 302)  # 302 is redirect status code
    
    def test_board_access_restriction(self):
        """Test that users cannot access boards they don't have permission for."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create request from the other user
        url = reverse('board_analytics_insights_api', kwargs={'board_id': self.board.id})
        request = self.factory.get(url)
        request.user = other_user
        
        # Call the API view
        response = board_analytics_insights_api(request, self.board.id)
        
        # Assertions - should get an access denied error
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertIn('error', content)
        self.assertIn('Access denied', content['error'])


class JavaScriptIntegrationTestCase(TestCase):
    """
    Test the frontend JavaScript integration with the AI features.
    
    These tests verify that the JavaScript functions correctly call the API endpoints
    and handle responses appropriately.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = self.client_class()
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create an organization
        self.organization = Organization.objects.create(
            name='Test Org',
            domain='testorg.com',
            created_by=self.user
        )
        
        # Create user profile
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            organization=self.organization
        )
        
        # Create a board
        self.board = Board.objects.create(
            name='Test Board',
            organization=self.organization,
            created_by=self.user
        )
        
        # Create a column
        self.column = Column.objects.create(
            name='Test Column',
            board=self.board
        )
        
        # Create a task
        self.task = Task.objects.create(
            title='Test Task',
            column=self.column,
            created_by=self.user
        )
        
        # Login the user
        self.client.login(username='testuser', password='testpass123')
    
    @patch('kanban.api_views.generate_task_description')
    def test_task_description_endpoint(self, mock_generate):
        """Test that the task description API endpoint is accessible via HTTP."""
        # Setup mock
        mock_generate.return_value = "**Objective:** Test\n\n**Checklist:**\n- [ ] Item 1"
        
        # Make the request
        url = reverse('generate_task_description_api')
        response = self.client.post(
            url,
            data=json.dumps({'title': 'Test Task'}),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('description', content)
    
    @patch('kanban.api_views.summarize_comments')
    def test_comments_summary_endpoint(self, mock_summarize):
        """Test that the comments summary API endpoint is accessible via HTTP."""
        # Setup mock
        mock_summarize.return_value = "Summary of the comments"
        
        # Make the request
        url = reverse('summarize_comments_api', kwargs={'task_id': self.task.id})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('summary', content)
    
    @patch('kanban.api_views.generate_analytics_insights')
    def test_board_analytics_endpoint(self, mock_insights):
        """Test that the board analytics API endpoint is accessible via HTTP."""
        # Setup mock
        mock_insights.return_value = "Analytics insights: All good!"
        
        # Make the request
        url = reverse('board_analytics_insights_api', kwargs={'board_id': self.board.id})
        response = self.client.get(url)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('insights', content)
    
    @patch('kanban.api_views.suggest_lean_classification')
    def test_lss_classification_endpoint(self, mock_classify):
        """Test that the LSS classification API endpoint is accessible via HTTP."""
        # Setup mock
        mock_classify.return_value = {
            "classification": "Value-Added",
            "justification": "This task directly contributes to customer value."
        }
        
        # Make the request
        url = reverse('suggest_lss_classification_api')
        response = self.client.post(
            url,
            data=json.dumps({
                'title': 'Test Task',
                'description': 'Test description'
            }),
            content_type='application/json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertIn('classification', content)
        self.assertIn('justification', content)
