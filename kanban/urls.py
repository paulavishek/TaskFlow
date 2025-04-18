from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('boards/', views.board_list, name='board_list'),
    path('boards/<int:board_id>/', views.board_detail, name='board_detail'),
    path('boards/<int:board_id>/analytics/', views.board_analytics, name='board_analytics'),
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
    path('columns/<int:column_id>/move/left/', views.move_column, {'direction': 'left'}, name='move_column_left'),
    path('columns/<int:column_id>/move/right/', views.move_column, {'direction': 'right'}, name='move_column_right'),
    path('columns/reorder/', views.reorder_columns, name='reorder_columns'),
    path('columns/reorder-multiple/', views.reorder_multiple_columns, name='reorder_multiple_columns'),
    path('columns/<int:column_id>/delete/', views.delete_column, name='delete_column'),
]