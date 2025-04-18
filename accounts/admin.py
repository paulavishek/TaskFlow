from django.contrib import admin
from .models import Organization, UserProfile

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain', 'created_at', 'created_by')
    search_fields = ('name', 'domain')
    list_filter = ('created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'is_admin')
    list_filter = ('is_admin', 'organization')
    search_fields = ('user__username', 'user__email', 'organization__name')
