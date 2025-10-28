from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from kanban.models import Board
from accounts.models import Organization
from .models import AIAssistantSession, AIAssistantMessage, UserPreference


class AIAssistantModelTest(TestCase):
    """Test AI Assistant models"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.organization = Organization.objects.create(name='Test Org', owner=self.user)
        self.board = Board.objects.create(
            name='Test Board',
            organization=self.organization,
            created_by=self.user
        )
    
    def test_create_session(self):
        """Test creating an AI Assistant session"""
        session = AIAssistantSession.objects.create(
            user=self.user,
            board=self.board,
            title='Test Session'
        )
        self.assertEqual(session.title, 'Test Session')
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
    
    def test_create_message(self):
        """Test creating a message in a session"""
        session = AIAssistantSession.objects.create(
            user=self.user,
            board=self.board,
            title='Test Session'
        )
        message = AIAssistantMessage.objects.create(
            session=session,
            role='user',
            content='Test message'
        )
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.role, 'user')
        self.assertEqual(message.session, session)
    
    def test_user_preference_creation(self):
        """Test creating user preferences"""
        pref = UserPreference.objects.create(
            user=self.user,
            preferred_model='gemini',
            theme='dark'
        )
        self.assertEqual(pref.preferred_model, 'gemini')
        self.assertEqual(pref.theme, 'dark')
        self.assertTrue(pref.enable_web_search)


class AIAssistantViewTest(TestCase):
    """Test AI Assistant views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.organization = Organization.objects.create(name='Test Org', owner=self.user)
        self.board = Board.objects.create(
            name='Test Board',
            organization=self.organization,
            created_by=self.user
        )
    
    def test_welcome_view_authenticated(self):
        """Test welcome page for authenticated user"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ai_assistant:welcome'))
        self.assertEqual(response.status_code, 200)
    
    def test_welcome_view_unauthenticated(self):
        """Test welcome page redirects for unauthenticated user"""
        response = self.client.get(reverse('ai_assistant:welcome'))
        self.assertEqual(response.status_code, 302)  # Redirect
