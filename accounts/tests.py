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
from .models import UserProfile, Organization
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


class OrganizationTestCase(TestCase):
    """Test organization management functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='orgcreator',
            email='creator@example.com',
            password='testpass123'
        )
        self.member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='testpass123'
        )
    
    def test_organization_creation_valid_domain(self):
        """Test creating organization with valid domain"""
        org = Organization.objects.create(
            name='Test Company',
            domain='example.com',
            created_by=self.user
        )
        
        self.assertEqual(org.name, 'Test Company')
        self.assertEqual(org.domain, 'example.com')
        self.assertEqual(org.created_by, self.user)
        self.assertTrue(org.created_at)
    
    def test_organization_invalid_domain(self):
        """Test organization creation with invalid domain"""
        # Test invalid domain formats
        invalid_domains = [
            'invalid',
            'invalid.',
            '.invalid',
            'invalid..com',
            'inv@lid.com',
            '123'
        ]
        
        for invalid_domain in invalid_domains:
            with self.assertRaises(ValidationError):
                org = Organization(
                    name='Test Company',
                    domain=invalid_domain,
                    created_by=self.user
                )
                org.full_clean()
    
    def test_organization_domain_validation(self):
        """Test domain validation with various formats"""
        valid_domains = [
            'example.com',
            'sub.example.com',
            'test-company.org',
            'company123.net',
            'my-company.co.uk'
        ]
        
        for valid_domain in valid_domains:
            org = Organization(
                name='Test Company',
                domain=valid_domain,
                created_by=self.user
            )
            # Should not raise ValidationError
            org.full_clean()
    
    def test_user_profile_organization_relationship(self):
        """Test UserProfile organization relationship"""
        org = Organization.objects.create(
            name='Test Company',
            domain='example.com',
            created_by=self.user
        )
        
        profile = UserProfile.objects.create(
            user=self.user,
            organization=org,
            is_admin=True
        )
        
        self.assertEqual(profile.organization, org)
        self.assertTrue(profile.is_admin)
        self.assertEqual(org.members.first(), profile)
    
    def test_organization_member_management(self):
        """Test adding and managing organization members"""
        org = Organization.objects.create(
            name='Test Company',
            domain='example.com',
            created_by=self.user
        )
        
        # Create profiles for users
        admin_profile = UserProfile.objects.create(
            user=self.user,
            organization=org,
            is_admin=True
        )
        
        member_profile = UserProfile.objects.create(
            user=self.member,
            organization=org,
            is_admin=False
        )
        
        # Test member count
        self.assertEqual(org.members.count(), 2)
        
        # Test admin and member roles
        self.assertTrue(admin_profile.is_admin)
        self.assertFalse(member_profile.is_admin)
    
    def test_organization_cascade_deletion(self):
        """Test that deleting organization cascades to profiles"""
        org = Organization.objects.create(
            name='Test Company',
            domain='example.com',
            created_by=self.user
        )
        
        profile = UserProfile.objects.create(
            user=self.user,
            organization=org
        )
        
        org_id = org.id
        profile_id = profile.id
        
        # Delete organization
        org.delete()
        
        # Check that profile is also deleted
        self.assertFalse(Organization.objects.filter(id=org_id).exists())
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())
        # But user should still exist
        self.assertTrue(User.objects.filter(id=self.user.id).exists())


class UserProfileEnhancedTestCase(TestCase):
    """Enhanced test for user profile functionality including organization"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.organization = Organization.objects.create(
            name='Test Company',
            domain='example.com',
            created_by=self.user
        )
    
    def test_profile_creation_with_organization(self):
        """Test profile creation with organization"""
        profile = UserProfile.objects.create(
            user=self.user,
            organization=self.organization,
            is_admin=True
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.organization, self.organization)
        self.assertTrue(profile.is_admin)
    
    def test_profile_picture_upload(self):
        """Test profile picture field"""
        profile = UserProfile.objects.create(
            user=self.user,
            organization=self.organization
        )
        
        # Test that profile picture field exists and is optional
        self.assertIsNone(profile.profile_picture)
        
        # Test setting profile picture path
        profile.profile_picture = 'profile_pics/test.jpg'
        profile.save()
        
        profile.refresh_from_db()
        self.assertEqual(profile.profile_picture, 'profile_pics/test.jpg')
    
    def test_profile_admin_toggle(self):
        """Test toggling admin status"""
        profile = UserProfile.objects.create(
            user=self.user,
            organization=self.organization,
            is_admin=False
        )
        
        self.assertFalse(profile.is_admin)
        
        # Toggle to admin
        profile.is_admin = True
        profile.save()
        
        profile.refresh_from_db()
        self.assertTrue(profile.is_admin)
    
    def test_profile_string_representation(self):
        """Test profile string representation"""
        profile = UserProfile.objects.create(
            user=self.user,
            organization=self.organization
        )
        
        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(profile), expected_str)


class OrganizationIntegrationTestCase(TestCase):
    """Integration tests for organization workflows"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Company',
            domain='example.com',
            created_by=self.admin_user
        )
    
    def test_complete_organization_setup(self):
        """Test complete organization setup workflow"""
        # Create admin profile
        admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            organization=self.organization,
            is_admin=True
        )
        
        # Create regular member profile
        member_profile = UserProfile.objects.create(
            user=self.regular_user,
            organization=self.organization,
            is_admin=False
        )
        
        # Verify setup
        self.assertEqual(self.organization.members.count(), 2)
        self.assertTrue(admin_profile.is_admin)
        self.assertFalse(member_profile.is_admin)
        
        # Test organization accessibility
        admin_orgs = Organization.objects.filter(members__user=self.admin_user)
        user_orgs = Organization.objects.filter(members__user=self.regular_user)
        
        self.assertIn(self.organization, admin_orgs)
        self.assertIn(self.organization, user_orgs)
    
    def test_organization_email_domain_matching(self):
        """Test email domain validation concept"""
        # Test that organization domain can be used for email validation
        org_domain = self.organization.domain
        
        # Valid email for this organization
        valid_email = f"newuser@{org_domain}"
        self.assertTrue(valid_email.endswith(org_domain))
        
        # Invalid email for this organization  
        invalid_email = "newuser@otherdomain.com"
        self.assertFalse(invalid_email.endswith(org_domain))
    
    def test_organization_member_permissions(self):
        """Test different permission levels within organization"""
        # Create profiles with different permission levels
        admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            organization=self.organization,
            is_admin=True
        )
        
        member_profile = UserProfile.objects.create(
            user=self.regular_user,
            organization=self.organization,
            is_admin=False
        )
        
        # Test admin permissions
        self.assertTrue(admin_profile.is_admin)
        self.assertEqual(admin_profile.organization, self.organization)
        
        # Test member permissions
        self.assertFalse(member_profile.is_admin)
        self.assertEqual(member_profile.organization, self.organization)
        
        # Both should be in same organization
        self.assertEqual(admin_profile.organization, member_profile.organization)


if __name__ == '__main__':
    import unittest
    unittest.main()
