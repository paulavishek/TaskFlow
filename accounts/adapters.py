from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Organization, UserProfile
import re


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter for regular account signup"""
    
    def clean_email(self, email):
        """
        Validates the email and checks if it matches an organization domain
        """
        email = super().clean_email(email)
        
        # Extract domain from email
        domain = email.split('@')[-1].lower()
        
        # Check if there's an organization with this domain
        try:
            organization = Organization.objects.get(domain=domain)
            # Store organization in session for later use
            if hasattr(self.request, 'session'):
                self.request.session['signup_organization_id'] = organization.id
        except Organization.DoesNotExist:
            # If no organization exists with this domain, user can still sign up
            # but will need to create or join an organization later
            pass
        
        return email


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter for social account signup (Google OAuth)"""
    
    def pre_social_login(self, request, sociallogin):
        """
        Called just after a user successfully authenticates via a social provider,
        but before the login is processed.
        """
        # Get the user's email from Google
        if sociallogin.account.provider == 'google':
            email = sociallogin.account.extra_data.get('email')
            if email:
                # Check if user already exists
                try:
                    user = User.objects.get(email=email)
                    # Connect the social account to existing user
                    sociallogin.connect(request, user)
                except User.DoesNotExist:
                    pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social account user.
        """
        user = super().save_user(request, sociallogin, form)
        
        if sociallogin.account.provider == 'google':
            # Get user's email domain
            email = user.email
            domain = email.split('@')[-1].lower()
              # Try to find an organization with this domain
            try:
                organization = Organization.objects.get(domain=domain)
                
                # Create user profile and assign to organization
                UserProfile.objects.create(
                    user=user,
                    organization=organization,
                    is_admin=False  # New Google users are not admins by default
                )
                
            except Organization.DoesNotExist:
                # If no organization exists, the user will be redirected to create/join one
                pass
            except Organization.MultipleObjectsReturned:
                # If multiple organizations with same domain, use the first one (oldest)
                organization = Organization.objects.filter(domain=domain).order_by('created_at').first()
                UserProfile.objects.create(
                    user=user,
                    organization=organization,
                    is_admin=False
                )
        
        return user
    
    def populate_username(self, request, user):
        """
        Generate a unique username from the user's email or Google profile
        """
        if hasattr(user, 'socialaccount_set'):
            social_account = user.socialaccount_set.first()
            if social_account and social_account.provider == 'google':
                # Try to use the name from Google profile
                extra_data = social_account.extra_data
                given_name = extra_data.get('given_name', '')
                family_name = extra_data.get('family_name', '')
                
                if given_name and family_name:
                    base_username = f"{given_name.lower()}.{family_name.lower()}"
                else:
                    # Fallback to email prefix
                    base_username = user.email.split('@')[0].lower()
                
                # Clean username (remove special characters except dots)
                base_username = re.sub(r'[^a-z0-9.]', '', base_username)
                
                # Ensure username is unique
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user.username = username
        
        return super().populate_username(request, user)
        """
        Saves a newly signed up social account user.
        """
        user = super().save_user(request, sociallogin, form)
        
        if sociallogin.account.provider == 'google':
            # Get user's email domain
            email = user.email
            domain = email.split('@')[-1].lower()
            
            # Try to find an organization with this domain
            try:
                organization = Organization.objects.get(domain=domain)
                
                # Create user profile and assign to organization
                UserProfile.objects.create(
                    user=user,
                    organization=organization,
                    is_admin=False  # New Google users are not admins by default
                )
                
            except Organization.DoesNotExist:
                # If no organization exists, the user will be redirected to create/join one
                # We'll handle this in the login redirect
                pass
        
        return user
    
    def get_login_redirect_url(self, request):
        """
        Custom redirect after social login based on user's organization status
        """
        try:
            # Check if user has a profile/organization
            profile = request.user.profile
            # User has organization, redirect to dashboard
            return '/dashboard/'
        except (AttributeError, UserProfile.DoesNotExist):
            # User doesn't have organization, redirect to organization choice
            return '/accounts/social-signup-complete/'
    
    def populate_username(self, request, user):
        """
        Generate a unique username from the user's email or Google profile
        """
        if hasattr(user, 'socialaccount_set'):
            social_account = user.socialaccount_set.first()
            if social_account and social_account.provider == 'google':
                # Try to use the name from Google profile
                extra_data = social_account.extra_data
                given_name = extra_data.get('given_name', '')
                family_name = extra_data.get('family_name', '')
                
                if given_name and family_name:
                    base_username = f"{given_name.lower()}.{family_name.lower()}"
                else:
                    # Fallback to email prefix
                    base_username = user.email.split('@')[0].lower()
                
                # Clean username (remove special characters except dots)
                base_username = re.sub(r'[^a-z0-9.]', '', base_username)
                
                # Ensure username is unique
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user.username = username
        
        return super().populate_username(request, user)
