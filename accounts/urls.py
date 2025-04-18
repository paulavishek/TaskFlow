from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('register/<int:org_id>/', views.register_view, name='register_with_org'),
    path('organization-choice/', views.organization_choice, name='organization_choice'),
    path('join-organization/', views.join_organization, name='join_organization'),
    path('create-organization/', views.create_organization, name='create_organization'),
    path('profile/', views.profile_view, name='profile'),
    path('organization/members/', views.organization_members, name='organization_members'),
    path('organization/settings/', views.organization_settings, name='organization_settings'),
    path('organization/toggle-admin/<int:profile_id>/', views.toggle_admin, name='toggle_admin'),
    path('organization/remove-member/<int:profile_id>/', views.remove_member, name='remove_member'),
    path('organization/delete/', views.delete_organization, name='delete_organization'),
]