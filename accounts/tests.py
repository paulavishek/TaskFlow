import json
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

# Import only accounts app models
from .models import UserProfile
# If you have team models in accounts app, include them
# from .models import Team, TeamMembership


class UserRegistrationTestCase(TestCase):
    """Test user registration functionality"""
    
    def test_user_registration_valid_data(self):
        """Test user registration with valid data"""
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check if UserProfile was created
        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'different123'
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='testuser').exists())
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user(username='existing', email='existing@example.com')
        
        response = self.client.post('/api/auth/register/', {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(username='user1', email='same@example.com')
        
        response = self.client.post('/api/auth/register/', {
            'username': 'user2',
            'email': 'same@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        self.assertEqual(response.status_code, 400)


class UserAuthenticationTestCase(TestCase):
    """Test user authentication and authorization"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_user_login_valid_credentials(self):
        """Test user login with valid credentials"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())
    
    def test_user_login_invalid_password(self):
        """Test login with invalid password"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post('/api/auth/login/', {
            'username': 'nonexistent',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 401)
    
    def test_user_logout(self):
        """Test user logout functionality"""
        # Login first
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = login_response.json()['token']
        
        # Logout
        response = self.client.post('/api/auth/logout/', 
                                  HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(response.status_code, 200)
    
    def test_password_change(self):
        """Test password change functionality"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'new_password_confirm': 'newpass456'
        })
        self.assertEqual(response.status_code, 200)
        
        # Test login with new password
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'newpass456'
        })
        self.assertEqual(response.status_code, 200)


class UserProfileTestCase(TestCase):
    """Test user profile functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Assuming UserProfile is created automatically via signals
    
    def test_profile_creation(self):
        """Test automatic profile creation"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_profile_update(self):
        """Test profile information update"""
        profile_data = {
            'bio': 'Software Developer',
            'location': 'New York',
            'timezone': 'America/New_York',
            'avatar_url': 'https://example.com/avatar.jpg'
        }
        
        for field, value in profile_data.items():
            setattr(self.user.profile, field, value)
        self.user.profile.save()
        
        self.user.profile.refresh_from_db()
        for field, value in profile_data.items():
            self.assertEqual(getattr(self.user.profile, field), value)
    
    def test_profile_api_update(self):
        """Test profile update via API"""
        self.client.force_login(self.user)
        
        response = self.client.patch('/api/profile/', {
            'bio': 'Updated bio',
            'location': 'San Francisco'
        })
        self.assertEqual(response.status_code, 200)
        
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'Updated bio')
        self.assertEqual(self.user.profile.location, 'San Francisco')


class UserPermissionsTestCase(TestCase):
    """Test user permissions and roles"""
    
    def setUp(self):
        self.regular_user = User.objects.create_user(
            username='regular',
            password='pass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
    
    def test_regular_user_permissions(self):
        """Test regular user permissions"""
        self.assertFalse(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)
        self.assertTrue(self.regular_user.is_active)
    
    def test_admin_user_permissions(self):
        """Test admin user permissions"""
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.is_active)
    
    def test_user_deactivation(self):
        """Test user account deactivation"""
        self.regular_user.is_active = False
        self.regular_user.save()
        
        # Try to login with deactivated account
        response = self.client.post('/api/auth/login/', {
            'username': 'regular',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 401)


class PasswordResetTestCase(TestCase):
    """Test password reset functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpass123'
        )
    
    @patch('django.core.mail.send_mail')
    def test_password_reset_request(self, mock_send_mail):
        """Test password reset request"""
        response = self.client.post('/api/auth/password-reset/', {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        
        # Check if email was sent
        mock_send_mail.assert_called_once()
    
    def test_password_reset_invalid_email(self):
        """Test password reset with invalid email"""
        response = self.client.post('/api/auth/password-reset/', {
            'email': 'nonexistent@example.com'
        })
        # Should still return 200 for security reasons
        self.assertEqual(response.status_code, 200)


class AccountSecurityTestCase(TestCase):
    """Test account security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_sql_injection_prevention_login(self):
        """Test SQL injection prevention in login"""
        malicious_input = "admin'; DROP TABLE auth_user; --"
        
        response = self.client.post('/api/auth/login/', {
            'username': malicious_input,
            'password': 'password'
        })
        
        # Should not cause any issues
        self.assertEqual(response.status_code, 401)
        # Verify user table still exists
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        weak_passwords = [
            '123',
            'password',
            '12345678',
            'qwerty'
        ]
        
        for weak_password in weak_passwords:
            response = self.client.post('/api/auth/register/', {
                'username': f'user_{weak_password}',
                'email': f'{weak_password}@example.com',
                'password': weak_password,
                'password_confirm': weak_password
            })
            self.assertEqual(response.status_code, 400)
    
    def test_rate_limiting_login_attempts(self):
        """Test rate limiting for login attempts"""
        # Simulate multiple failed login attempts
        for i in range(6):  # Assuming rate limit is 5 attempts
            response = self.client.post('/api/auth/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Should be rate limited after 5 attempts
        self.assertEqual(response.status_code, 429)


class APIAuthenticationTestCase(APITestCase):
    """Test API authentication"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.client = APIClient()
    
    def test_token_authentication(self):
        """Test token-based authentication"""
        # Get token
        response = self.client.post('/api/auth/login/', {
            'username': 'apiuser',
            'password': 'apipass123'
        })
        token = response.data['token']
        
        # Use token for authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_token(self):
        """Test request with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)
    
    def test_unauthenticated_request(self):
        """Test unauthenticated request to protected endpoint"""
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    import unittest
    unittest.main()
