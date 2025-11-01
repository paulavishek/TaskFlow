from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    # Category Management
    path('categories/', views.WikiCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.WikiCategoryCreateView.as_view(), name='category_create'),
    
    # Page Management
    path('', views.WikiPageListView.as_view(), name='page_list'),
    path('category/<int:category_id>/', views.WikiPageListView.as_view(), name='page_list_by_category'),
    path('create/', views.WikiPageCreateView.as_view(), name='page_create'),
    path('page/<slug:slug>/', views.WikiPageDetailView.as_view(), name='page_detail'),
    path('page/<slug:slug>/edit/', views.WikiPageUpdateView.as_view(), name='page_edit'),
    path('page/<slug:slug>/delete/', views.WikiPageDeleteView.as_view(), name='page_delete'),
    path('page/<slug:slug>/history/', views.wiki_page_history, name='page_history'),
    path('page/<slug:slug>/restore/<int:version_number>/', views.wiki_page_restore, name='page_restore'),
    
    # Wiki Links
    path('page/<slug:slug>/link/', views.WikiLinkCreateView.as_view(), name='link_create'),
    path('quick-link/<str:content_type>/<int:object_id>/', views.quick_link_wiki, name='quick_link'),
    
    # Search
    path('search/', views.wiki_search, name='search'),
    
    # Meeting Notes
    path('meeting-notes/', views.meeting_notes_list, name='meeting_notes_list'),
    path('meeting-notes/create/', views.meeting_notes_create, name='meeting_notes_create'),
    path('meeting-notes/<int:pk>/', views.meeting_notes_detail, name='meeting_notes_detail'),
]
