from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ..models import Organization, UserProfile

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password',
            'id': 'password-field'
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'new-password1-field',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'new-password2-field',
            'placeholder': 'Confirm New Password'
        })
    )

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'domain']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example.com'}),
        }

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password1-field'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password2-field'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.organization:
            domain = email.split('@')[-1]
            if domain != self.organization.domain:
                raise ValidationError(f"Email must belong to the {self.organization.domain} domain.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            if self.organization:
                UserProfile.objects.create(
                    user=user,
                    organization=self.organization,
                    is_admin=False
                )
        
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

class OrganizationSettingsForm(forms.ModelForm):
    """
    A form for admins to update organization settings.
    Domain changes require careful validation to not break existing accounts.
    """
    class Meta:
        model = Organization
        fields = ['name', 'domain']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'domain': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'example.com'
            }),
        }
        
    def clean_domain(self):
        """
        Ensure domain changes don't invalidate existing user emails.
        """
        domain = self.cleaned_data.get('domain')
        if self.instance and self.instance.pk:
            # This is an existing organization
            if domain != self.instance.domain:
                # Check if there are users with emails that wouldn't match the new domain
                profiles = UserProfile.objects.filter(organization=self.instance)
                for profile in profiles:
                    email_domain = profile.user.email.split('@')[-1]
                    if email_domain != domain:
                        raise ValidationError(
                            f"Cannot change domain to {domain} as user {profile.user.username} " +
                            f"has an email with domain {email_domain}. All user emails must match " +
                            "the organization domain."
                        )
        return domain

class JoinOrganizationForm(forms.Form):
    organization_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter organization name'}),
        max_length=100,
        required=True,
        help_text="Enter the exact name of the organization you want to join"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email address'}),
        help_text="Your email must match the organization's domain"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        organization_name = cleaned_data.get('organization_name')
        email = cleaned_data.get('email')
        
        if organization_name and email:
            try:
                # Try to find the organization by name
                organization = Organization.objects.get(name=organization_name)
                
                # Check if email domain matches organization domain
                email_domain = email.split('@')[-1]
                if email_domain != organization.domain:
                    raise ValidationError(
                        f"Your email domain ({email_domain}) does not match the organization's domain ({organization.domain}). "
                        "Please use your organization email or contact your administrator."
                    )
                
                # Store the organization instance for later use in the view
                cleaned_data['organization'] = organization
                
            except Organization.DoesNotExist:
                raise ValidationError(f"Organization '{organization_name}' not found. Please check the spelling.")
                
        return cleaned_data