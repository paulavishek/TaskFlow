from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator, RegexValidator

class Organization(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(
        max_length=100, 
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$',
                message='Enter a valid domain (e.g., example.com)'
            )
        ],
        help_text="Domain used for email validation (e.g., example.com)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_organizations')
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    is_admin = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
