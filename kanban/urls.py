from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Getting Started Wizard
    path('getting-started/', views.getting_started_wizard, name='getting_started_wizard'),
    path('getting-started/complete/', views.complete_wizard, name='complete_wizard'),
    path('getting-started/reset/', views.reset_wizard, name='reset_wizard'),
    path('api/wizard/create-board/', views.wizard_create_board, name='wizard_create_board'),
    path('api/wizard/create-task/', views.wizard_create_task, name='wizard_create_task'),
    
    path('boards/', views.board_list, name='board_list'),
    path('boards/create/', views.create_board, name='create_board'),    path('boards/<int:board_id>/', views.board_detail, name='board_detail'),    path('boards/<int:board_id>/analytics/', views.board_analytics, name='board_analytics'),
    path('boards/<int:board_id>/edit/', views.edit_board, name='edit_board'),
    path('boards/<int:board_id>/create-task/', views.create_task, name='create_task'),
    path('boards/<int:board_id>/columns/<int:column_id>/create-task/', views.create_task, name='create_task_in_column'),
    path('boards/<int:board_id>/create-column/', views.create_column, name='create_column'),
    path('boards/<int:board_id>/create-label/', views.create_label, name='create_label'),
    path('boards/<int:board_id>/add-member/', views.add_board_member, name='add_board_member'),
    path('boards/<int:board_id>/delete/', views.delete_board, name='delete_board'),
    path('boards/<int:board_id>/join/', views.join_board, name='join_board'),
    path('boards/<int:board_id>/export/', views.export_board, name='export_board'),
    path('boards/import/', views.import_board, name='import_board'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/move/', views.move_task, name='move_task'),
    path('tasks/<int:task_id>/update-progress/', views.update_task_progress, name='update_task_progress'),
    path('organization-boards/', views.organization_boards, name='organization_boards'),
    path('labels/<int:label_id>/delete/', views.delete_label, name='delete_label'),
    path('columns/<int:column_id>/move/left/', views.move_column, {'direction': 'left'}, name='move_column_left'),    path('columns/<int:column_id>/move/right/', views.move_column, {'direction': 'right'}, name='move_column_right'),
    path('columns/reorder/', views.reorder_columns, name='reorder_columns'),
    path('columns/reorder-multiple/', views.reorder_multiple_columns, name='reorder_multiple_columns'),
    path('columns/<int:column_id>/delete/', views.delete_column, name='delete_column'),    path('boards/<int:board_id>/add-lean-labels/', views.add_lean_labels, name='add_lean_labels'),
    
    # Test page for AI features
    path('test-ai-features/', views.test_ai_features, name='test_ai_features'),    # AI API Endpoints
    path('api/generate-task-description/', api_views.generate_task_description_api, name='generate_task_description_api'),
    path('api/summarize-comments/<int:task_id>/', api_views.summarize_comments_api, name='summarize_comments_api'),
    path('api/suggest-lss-classification/', api_views.suggest_lss_classification_api, name='suggest_lss_classification_api'),
    path('api/summarize-board-analytics/<int:board_id>/', api_views.summarize_board_analytics_api, name='summarize_board_analytics_api'),
      # New AI Enhancement API Endpoints
    path('api/suggest-task-priority/', api_views.suggest_task_priority_api, name='suggest_task_priority_api'),
    path('api/predict-deadline/', api_views.predict_deadline_api, name='predict_deadline_api'),
    path('api/recommend-columns/', api_views.recommend_columns_api, name='recommend_columns_api'),
    path('api/suggest-task-breakdown/', api_views.suggest_task_breakdown_api, name='suggest_task_breakdown_api'),
    path('api/analyze-workflow-optimization/', api_views.analyze_workflow_optimization_api, name='analyze_workflow_optimization_api'),    path('api/create-subtasks/', api_views.create_subtasks_api, name='create_subtasks_api'),
    
    # Meeting Transcript Extraction
    path('boards/<int:board_id>/meeting-transcript/', views.meeting_transcript_extraction, name='meeting_transcript_extraction'),
    path('api/extract-tasks-from-transcript/', api_views.extract_tasks_from_transcript_api, name='extract_tasks_from_transcript_api'),
    path('api/create-tasks-from-extraction/', api_views.create_tasks_from_extraction_api, name='create_tasks_from_extraction_api'),
    path('api/process-transcript-file/', api_views.process_transcript_file_api, name='process_transcript_file_api'),
]