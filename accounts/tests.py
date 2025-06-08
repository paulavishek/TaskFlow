from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Organization, UserProfile
from django.core.exceptions import ValidationError
from django.forms import ValidationError as FormValidationError


class OrganizationModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', password='password', email='admin@example.com')
    
    def test_organization_creation(self):
        """Test creating an organization with valid data"""
        org = Organization.objects.create(
            name='Test Organization',
            domain='example.com',
            created_by=self.user
        )
        self.assertEqual(org.name, 'Test Organization')
        self.assertEqual(org.domain, 'example.com')
        self.assertEqual(org.created_by, self.user)
        self.assertEqual(str(org), 'Test Organization')
    
    def test_organization_domain_validation(self):
        """Test domain validation in Organization model"""
        with self.assertRaises(ValidationError):
            org = Organization(
                name='Invalid Domain Org',
                domain='not-a-valid-domain',
                created_by=self.user
            )
            org.full_clean()  # This should raise ValidationError due to invalid domain


class UserProfileModelTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin_user = User.objects.create_user(username='adminuser', password='password')
        self.org = Organization.objects.create(
            name='Test Org',
            domain='testorg.com',
            created_by=self.admin_user
        )
    
    def test_user_profile_creation(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            organization=self.org,
            is_admin=False
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.organization, self.org)
        self.assertFalse(profile.is_admin)
        self.assertEqual(str(profile), "testuser's Profile")
    
    def test_admin_user_profile(self):
        """Test creating an admin user profile"""
        admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            organization=self.org,
            is_admin=True
        )
        self.assertTrue(admin_profile.is_admin)


class LoginViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(username='testlogin', email='login@example.com', password='password123')
        self.org = Organization.objects.create(name='Login Test Org', domain='example.com', created_by=self.user)
        UserProfile.objects.create(user=self.user, organization=self.org)
    
    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_successful_login(self):
        """Test login with correct credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testlogin',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_failed_login(self):
        """Test login with incorrect credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testlogin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Remains on login page
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_redirect_if_already_authenticated(self):
        """Test that authenticated users are redirected from login page"""
        self.client.login(username='testlogin', password='password123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('dashboard'))


class RegistrationViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.admin_user = User.objects.create_user(username='orgadmin', password='adminpass')
        self.org = Organization.objects.create(
            name='Sign Up Test Org',
            domain='signup.com',
            created_by=self.admin_user
        )
    
    def test_registration_page_loads(self):
        """Test that registration page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_successful_registration(self):
        """Test successful registration with valid data"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        })
        self.assertRedirects(response, reverse('login'))  # Should redirect to login
        self.assertTrue(User.objects.filter(username='newuser').exists())
    def test_organization_specific_registration(self):
        """Test registration for a specific organization"""
        org_register_url = reverse('register_with_org', args=[self.org.id])
        response = self.client.post(org_register_url, {
            'username': 'orguser',
            'email': 'orguser@signup.com',  # Must match org domain
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='orguser').exists())
    
    def test_invalid_email_domain_for_organization(self):
        """Test registration fails with wrong email domain for org"""
        org_register_url = reverse('register_with_org', args=[self.org.id])
        response = self.client.post(org_register_url, {
            'username': 'wrongdomain',
            'email': 'user@wrongdomain.com',  # Doesn't match org domain
            'password1': 'securepassword123',
            'password2': 'securepassword123'
        })
        self.assertEqual(response.status_code, 200)  # Form reloads with error
        self.assertFalse(User.objects.filter(username='wrongdomain').exists())


class OrganizationManagementTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user and organization
        self.admin_user = User.objects.create_user(username='orgadminuser', password='adminpass')
        self.regular_user = User.objects.create_user(username='regularuser', password='userpass')
        self.org = Organization.objects.create(
            name='Management Org',
            domain='management.com',
            created_by=self.admin_user
        )
        
        # Create admin profile
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            organization=self.org,
            is_admin=True
        )
        
        # Create regular user profile
        self.user_profile = UserProfile.objects.create(
            user=self.regular_user,
            organization=self.org,
            is_admin=False
        )
        
        # Create URL for organization settings
        self.org_settings_url = reverse('organization_settings')
        
        # Create a user without organization profile for testing join flow
        self.new_user = User.objects.create_user(
            username='newuser',
            password='newpass',
            email='newuser@example.com'
        )
        
        self.org_choice_url = reverse('organization_choice')
        self.create_org_url = reverse('create_organization')
        self.join_org_url = reverse('join_organization')
    
    def test_organization_choice_view(self):
        """Test organization choice view for new users"""
        self.client.login(username='newuser', password='newpass')
        response = self.client.get(self.org_choice_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/organization_choice.html')
    
    def test_redirect_if_already_has_organization(self):
        """Test users with existing profiles are redirected"""
        self.client.login(username='regularuser', password='userpass')
        response = self.client.get(self.org_choice_url)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_create_organization_view(self):
        """Test create organization process"""
        self.client.login(username='newuser', password='newpass')
        response = self.client.get(self.create_org_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/create_organization.html')
        
        # Test creating a new organization
        response = self.client.post(self.create_org_url, {
            'name': 'New Test Organization',
            'domain': 'newtestorg.com'
        })
        self.assertRedirects(response, reverse('dashboard'))
        
        # Check org was created and profile assigned
        new_org = Organization.objects.get(name='New Test Organization')
        self.assertEqual(new_org.domain, 'newtestorg.com')
        self.assertEqual(new_org.created_by, self.new_user)
        
        # Check user profile was created with admin privileges
        user_profile = UserProfile.objects.get(user=self.new_user)
        self.assertEqual(user_profile.organization, new_org)
        self.assertTrue(user_profile.is_admin)
    
    def test_join_organization_view_get(self):
        """Test join organization page loads"""
        self.client.login(username='newuser', password='newpass')
        response = self.client.get(self.join_org_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/join_organization.html')
    
    def test_organization_settings_access(self):
        """Test organization settings access permissions"""
        # Admin can access
        self.client.login(username='orgadminuser', password='adminpass')
        response = self.client.get(self.org_settings_url)
        self.assertEqual(response.status_code, 200)
        
        # Non-admin cannot access
        self.client.login(username='regularuser', password='userpass')
        response = self.client.get(self.org_settings_url)
        self.assertNotEqual(response.status_code, 200)  # Should be redirected or access denied


class LogoutViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='logoutuser', password='logoutpass')
        self.logout_url = reverse('logout')
    
    def test_logout_redirects_to_login(self):
        """Test logout redirects to login page"""
        self.client.login(username='logoutuser', password='logoutpass')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
