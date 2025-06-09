import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

# Import kanban app models
from .models import (
    KanbanBoard, Column, Card, Comment, Attachment,
    CardHistory, Label, CardLabel, BoardMember
)
# Import from other apps as needed
from accounts.models import UserProfile


class KanbanBoardTestCase(TestCase):
    """Test kanban board functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='boardowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collab@example.com',
            password='testpass123'
        )
    
    def test_board_creation(self):
        """Test creating a new kanban board"""
        board = KanbanBoard.objects.create(
            name='Project Alpha',
            description='Main project board',
            owner=self.user
        )
        
        self.assertEqual(board.name, 'Project Alpha')
        self.assertEqual(board.owner, self.user)
        self.assertTrue(board.created_at)
        self.assertFalse(board.is_archived)
        self.assertEqual(board.visibility, 'private')  # Default visibility
    
    def test_board_name_validation(self):
        """Test board name validation"""
        # Test empty name
        with self.assertRaises(ValidationError):
            board = KanbanBoard(name='', owner=self.user)
            board.full_clean()
        
        # Test name too long (assuming max_length=100)
        with self.assertRaises(ValidationError):
            board = KanbanBoard(name='x' * 101, owner=self.user)
            board.full_clean()
    
    def test_board_slug_generation(self):
        """Test automatic slug generation"""
        board = KanbanBoard.objects.create(
            name='Project Alpha Board',
            owner=self.user
        )
        
        self.assertEqual(board.slug, 'project-alpha-board')
    
    def test_board_member_management(self):
        """Test adding and removing board members"""
        board = KanbanBoard.objects.create(
            name='Team Board',
            owner=self.user
        )
        
        # Add collaborator
        member = BoardMember.objects.create(
            board=board,
            user=self.collaborator,
            role='member'
        )
        
        self.assertEqual(member.role, 'member')
        self.assertTrue(board.members.filter(user=self.collaborator).exists())
        
        # Test member permissions
        self.assertTrue(board.can_view(self.collaborator))
        self.assertTrue(board.can_edit(self.collaborator))
        self.assertFalse(board.can_admin(self.collaborator))
    
    def test_board_archiving(self):
        """Test board archiving functionality"""
        board = KanbanBoard.objects.create(
            name='Old Project',
            owner=self.user
        )
        
        board.archive()
        
        self.assertTrue(board.is_archived)
        self.assertIsNotNone(board.archived_at)
    
    def test_board_deletion_cascade(self):
        """Test that deleting a board cascades properly"""
        board = KanbanBoard.objects.create(
            name='Test Board',
            owner=self.user
        )
        
        column = Column.objects.create(
            board=board,
            name='To Do',
            position=1
        )
        
        card = Card.objects.create(
            column=column,
            title='Test Card'
        )
        
        board_id = board.id
        board.delete()
        
        self.assertFalse(KanbanBoard.objects.filter(id=board_id).exists())
        self.assertFalse(Column.objects.filter(board_id=board_id).exists())
        self.assertFalse(Card.objects.filter(column__board_id=board_id).exists())


class ColumnManagementTestCase(TestCase):
    """Test column/stage management"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.board = KanbanBoard.objects.create(
            name='Test Board',
            owner=self.user
        )
    
    def test_column_creation(self):
        """Test creating columns with proper ordering"""
        col1 = Column.objects.create(
            board=self.board,
            name='Backlog',
            position=1,
            wip_limit=10
        )
        col2 = Column.objects.create(
            board=self.board,
            name='In Progress',
            position=2,
            wip_limit=5
        )
        
        self.assertEqual(col1.position, 1)
        self.assertEqual(col2.position, 2)
        self.assertEqual(col1.wip_limit, 10)
        self.assertEqual(col2.wip_limit, 5)
    
    def test_column_ordering(self):
        """Test column position management"""
        col1 = Column.objects.create(board=self.board, name='Col1', position=1)
        col2 = Column.objects.create(board=self.board, name='Col2', position=2)
        col3 = Column.objects.create(board=self.board, name='Col3', position=3)
        
        # Get columns in order
        columns = Column.objects.filter(board=self.board).order_by('position')
        self.assertEqual(list(columns), [col1, col2, col3])
    
    def test_column_reordering(self):
        """Test reordering columns"""
        col1 = Column.objects.create(board=self.board, name='Col1', position=1)
        col2 = Column.objects.create(board=self.board, name='Col2', position=2)
        col3 = Column.objects.create(board=self.board, name='Col3', position=3)
        
        # Move col3 to position 1
        col3.move_to_position(1)
        
        col1.refresh_from_db()
        col2.refresh_from_db()
        col3.refresh_from_db()
        
        # Check new positions
        self.assertEqual(col3.position, 1)
        self.assertEqual(col1.position, 2)
        self.assertEqual(col2.position, 3)
    
    def test_wip_limit_enforcement(self):
        """Test Work In Progress limit enforcement"""
        column = Column.objects.create(
            board=self.board,
            name='In Progress',
            position=1,
            wip_limit=2
        )
        
        # Create cards up to WIP limit
        card1 = Card.objects.create(column=column, title='Card 1')
        card2 = Card.objects.create(column=column, title='Card 2')
        
        # Verify WIP limit check
        self.assertTrue(column.is_at_wip_limit())
        self.assertFalse(column.can_add_card())
        
        # Attempt to exceed WIP limit should raise validation error
        with self.assertRaises(ValidationError):
            card3 = Card.objects.create(column=column, title='Card 3')
            column.validate_wip_limit()
    
    def test_column_deletion_with_cards(self):
        """Test column deletion behavior when it contains cards"""
        column = Column.objects.create(board=self.board, name='Test Column', position=1)
        card = Card.objects.create(column=column, title='Test Card')
        
        # Should not be able to delete column with cards
        with self.assertRaises(ValidationError):
            column.delete()
        
        # After moving cards, deletion should work
        card.delete()
        column.delete()
        
        self.assertFalse(Column.objects.filter(id=column.id).exists())


class CardManagementTestCase(TestCase):
    """Test card/task management functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.assignee = User.objects.create_user(username='assignee', password='pass123')
        self.board = KanbanBoard.objects.create(name='Test Board', owner=self.user)
        self.column = Column.objects.create(
            board=self.board,
            name='To Do',
            position=1
        )
    
    def test_card_creation(self):
        """Test creating cards with all fields"""
        card = Card.objects.create(
            column=self.column,
            title='Implement Feature X',
            description='Detailed description of the feature',
            assignee=self.assignee,
            priority='high',
            story_points=8,
            due_date=datetime.now() + timedelta(days=7)
        )
        
        self.assertEqual(card.title, 'Implement Feature X')
        self.assertEqual(card.assignee, self.assignee)
        self.assertEqual(card.priority, 'high')
        self.assertEqual(card.story_points, 8)
        self.assertTrue(card.created_at)
        self.assertIsNone(card.started_at)
        self.assertIsNone(card.completed_at)
    
    def test_card_validation(self):
        """Test card field validation"""
        # Test invalid priority
        with self.assertRaises(ValidationError):
            card = Card(
                column=self.column,
                title='Invalid Priority Card',
                priority='invalid_priority'
            )
            card.full_clean()
        
        # Test negative story points
        with self.assertRaises(ValidationError):
            card = Card(
                column=self.column,
                title='Invalid Story Points',
                story_points=-1
            )
            card.full_clean()
        
        # Test empty title
        with self.assertRaises(ValidationError):
            card = Card(
                column=self.column,
                title=''
            )
            card.full_clean()
    
    def test_card_movement_tracking(self):
        """Test tracking card movement through columns"""
        card = Card.objects.create(
            column=self.column,
            title='Moving Card'
        )
        
        # Create next column
        next_column = Column.objects.create(
            board=self.board,
            name='In Progress',
            position=2
        )
        
        # Move card
        card.move_to_column(next_column, moved_by=self.user)
        
        self.assertEqual(card.column, next_column)
        self.assertIsNotNone(card.started_at)
        
        # Check history was created
        history = CardHistory.objects.filter(card=card).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.action, 'moved')
        self.assertEqual(history.user, self.user)
    
    def test_card_lifecycle_timestamps(self):
        """Test card lifecycle timestamp management"""
        card = Card.objects.create(column=self.column, title='Lifecycle Card')
        
        # Initially no timestamps except created_at
        self.assertIsNotNone(card.created_at)
        self.assertIsNone(card.started_at)
        self.assertIsNone(card.completed_at)
        
        # Move to "In Progress" column
        progress_column = Column.objects.create(
            board=self.board,
            name='In Progress',
            position=2,
            is_start_column=True
        )
        card.move_to_column(progress_column, self.user)
        
        self.assertIsNotNone(card.started_at)
        self.assertIsNone(card.completed_at)
        
        # Move to "Done" column
        done_column = Column.objects.create(
            board=self.board,
            name='Done',
            position=3,
            is_done_column=True
        )
        card.move_to_column(done_column, self.user)
        
        self.assertIsNotNone(card.completed_at)
    
    def test_card_blocking(self):
        """Test card blocking functionality"""
        card = Card.objects.create(
            column=self.column,
            title='Potentially Blocked Card'
        )
        
        # Block the card
        card.set_blocked(True, 'Waiting for external API', self.user)
        
        self.assertTrue(card.is_blocked)
        self.assertEqual(card.blocked_reason, 'Waiting for external API')
        self.assertIsNotNone(card.blocked_at)
        self.assertEqual(card.blocked_by, self.user)
        
        # Unblock the card
        card.set_blocked(False, reason='Issue resolved', user=self.user)
        
        self.assertFalse(card.is_blocked)
        self.assertIsNone(card.blocked_reason)
        self.assertIsNone(card.blocked_at)
    
    def test_card_time_calculations(self):
        """Test card time metric calculations"""
        # Create card with specific timestamps
        start_time = datetime.now() - timedelta(days=5)
        end_time = datetime.now()
        
        card = Card.objects.create(
            column=self.column,
            title='Timed Card',
            started_at=start_time,
            completed_at=end_time
        )
        
        # Test cycle time calculation
        cycle_time = card.calculate_cycle_time()
        self.assertEqual(cycle_time.days, 5)
        
        # Test lead time calculation (from creation to completion)
        lead_time = card.calculate_lead_time()
        self.assertIsNotNone(lead_time)
    
    def test_card_position_management(self):
        """Test card position within columns"""
        card1 = Card.objects.create(column=self.column, title='Card 1', position=1)
        card2 = Card.objects.create(column=self.column, title='Card 2', position=2)
        card3 = Card.objects.create(column=self.column, title='Card 3', position=3)
        
        # Move card3 to position 1
        card3.move_to_position(1)
        
        card1.refresh_from_db()
        card2.refresh_from_db()
        card3.refresh_from_db()
        
        self.assertEqual(card3.position, 1)
        self.assertEqual(card1.position, 2)
        self.assertEqual(card2.position, 3)


class CardLabelsTestCase(TestCase):
    """Test card labeling functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.board = KanbanBoard.objects.create(name='Test Board', owner=self.user)
        self.column = Column.objects.create(board=self.board, name='Test', position=1)
        self.card = Card.objects.create(column=self.column, title='Test Card')
    
    def test_label_creation(self):
        """Test creating labels for boards"""
        label = Label.objects.create(
            board=self.board,
            name='Bug',
            color='#ff0000',
            description='Bug reports'
        )
        
        self.assertEqual(label.name, 'Bug')
        self.assertEqual(label.color, '#ff0000')
        self.assertEqual(label.board, self.board)
    
    def test_card_label_assignment(self):
        """Test assigning labels to cards"""
        bug_label = Label.objects.create(board=self.board, name='Bug', color='#ff0000')
        urgent_label = Label.objects.create(board=self.board, name='Urgent', color='#ff9900')
        
        # Assign labels to card
        CardLabel.objects.create(card=self.card, label=bug_label)
        CardLabel.objects.create(card=self.card, label=urgent_label)
        
        # Check labels are assigned
        self.assertEqual(self.card.labels.count(), 2)
        self.assertTrue(self.card.labels.filter(name='Bug').exists())
        self.assertTrue(self.card.labels.filter(name='Urgent').exists())
    
    def test_label_filtering(self):
        """Test filtering cards by labels"""
        bug_label = Label.objects.create(board=self.board, name='Bug', color='#ff0000')
        feature_label = Label.objects.create(board=self.board, name='Feature', color='#00ff00')
        
        card1 = Card.objects.create(column=self.column, title='Bug Card')
        card2 = Card.objects.create(column=self.column, title='Feature Card')
        
        CardLabel.objects.create(card=card1, label=bug_label)
        CardLabel.objects.create(card=card2, label=feature_label)
        
        # Filter by bug label
        bug_cards = Card.objects.filter(cardlabel__label=bug_label)
        self.assertEqual(bug_cards.count(), 1)
        self.assertEqual(bug_cards.first(), card1)


class CommentAndAttachmentTestCase(TestCase):
    """Test card comments and attachments"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.other_user = User.objects.create_user(username='other', password='pass123')
        self.board = KanbanBoard.objects.create(name='Test Board', owner=self.user)
        self.column = Column.objects.create(board=self.board, name='Test', position=1)
        self.card = Card.objects.create(column=self.column, title='Test Card')
    
    def test_comment_creation(self):
        """Test adding comments to cards"""
        comment = Comment.objects.create(
            card=self.card,
            author=self.user,
            content='This is a test comment'
        )
        
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.card, self.card)
        self.assertTrue(comment.created_at)
    
    def test_comment_editing(self):
        """Test editing comments"""
        comment = Comment.objects.create(
            card=self.card,
            author=self.user,
            content='Original comment'
        )
        
        # Edit comment
        comment.content = 'Edited comment'
        comment.save()
        
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Edited comment')
        self.assertIsNotNone(comment.updated_at)
    
    def test_comment_permissions(self):
        """Test comment editing permissions"""
        comment = Comment.objects.create(
            card=self.card,
            author=self.user,
            content='User comment'
        )
        
        # Author should be able to edit
        self.assertTrue(comment.can_edit(self.user))
        
        # Other users should not be able to edit
        self.assertFalse(comment.can_edit(self.other_user))
    
    def test_attachment_upload(self):
        """Test file attachment to cards"""
        attachment = Attachment.objects.create(
            card=self.card,
            filename='test_document.pdf',
            file_size=1024000,  # 1MB
            uploaded_by=self.user,
            file_path='/uploads/test_document.pdf'
        )
        
        self.assertEqual(attachment.filename, 'test_document.pdf')
        self.assertEqual(attachment.file_size, 1024000)
        self.assertEqual(attachment.uploaded_by, self.user)
    
    def test_attachment_validation(self):
        """Test file attachment validation"""
        # Test file size limit (assuming 10MB limit)
        with self.assertRaises(ValidationError):
            attachment = Attachment(
                card=self.card,
                filename='large_file.zip',
                file_size=11 * 1024 * 1024,  # 11MB
                uploaded_by=self.user
            )
            attachment.full_clean()


class KanbanAPITestCase(APITestCase):
    """Test kanban REST API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.board = KanbanBoard.objects.create(
            name='API Test Board',
            owner=self.user
        )
    
    def test_boards_list_api(self):
        """Test boards list API endpoint"""
        response = self.client.get('/api/kanban/boards/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Test Board')
    
    def test_board_creation_api(self):
        """Test board creation via API"""
        data = {
            'name': 'New API Board',
            'description': 'Created via API',
            'visibility': 'public'
        }
        
        response = self.client.post('/api/kanban/boards/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New API Board')
        self.assertEqual(response.data['visibility'], 'public')
    
    def test_column_creation_api(self):
        """Test column creation via API"""
        data = {
            'name': 'API Column',
            'board': self.board.id,
            'position': 1,
            'wip_limit': 5
        }
        
        response = self.client.post('/api/kanban/columns/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Column')
        self.assertEqual(response.data['wip_limit'], 5)
    
    def test_card_creation_api(self):
        """Test card creation via API"""
        column = Column.objects.create(
            board=self.board,
            name='Test Column',
            position=1
        )
        
        data = {
            'title': 'API Created Card',
            'description': 'Created via API',
            'column': column.id,
            'priority': 'medium',
            'story_points': 5
        }
        
        response = self.client.post('/api/kanban/cards/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'API Created Card')
        self.assertEqual(response.data['priority'], 'medium')
    
    def test_card_movement_api(self):
        """Test moving cards via API"""
        column1 = Column.objects.create(board=self.board, name='Col1', position=1)
        column2 = Column.objects.create(board=self.board, name='Col2', position=2)
        
        card = Card.objects.create(column=column1, title='Moving Card')
        
        # Move card to column2
        response = self.client.patch(
            f'/api/kanban/cards/{card.id}/move/',
            {'column': column2.id, 'position': 1}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        card.refresh_from_db()
        self.assertEqual(card.column, column2)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to boards"""
        other_user = User.objects.create_user(username='other', password='pass123')
        private_board = KanbanBoard.objects.create(
            name='Private Board',
            owner=other_user,
            visibility='private'
        )
        
        response = self.client.get(f'/api/kanban/boards/{private_board.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class KanbanIntegrationTestCase(TestCase):
    """Integration tests for complete kanban workflows"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.team_lead = User.objects.create_user(username='teamlead', password='pass123')
        
        self.board = KanbanBoard.objects.create(
            name='Integration Board',
            owner=self.team_lead
        )
        
        # Add user as board member
        BoardMember.objects.create(
            board=self.board,
            user=self.user,
            role='member'
        )
        
        self.setup_workflow()
    
    def setup_workflow(self):
        """Setup a complete kanban workflow"""
        self.backlog = Column.objects.create(
            board=self.board, 
            name='Backlog', 
            position=1
        )
        self.todo = Column.objects.create(
            board=self.board, 
            name='To Do', 
            position=2
        )
        self.progress = Column.objects.create(
            board=self.board, 
            name='In Progress', 
            position=3, 
            wip_limit=3,
            is_start_column=True
        )
        self.review = Column.objects.create(
            board=self.board, 
            name='Review', 
            position=4
        )
        self.done = Column.objects.create(
            board=self.board, 
            name='Done', 
            position=5,
            is_done_column=True
        )
    
    def test_complete_card_workflow(self):
        """Test complete card workflow from creation to completion"""
        # Create card in backlog
        card = Card.objects.create(
            column=self.backlog,
            title='Feature Implementation',
            description='Implement new feature',
            story_points=8,
            priority='high'
        )
        
        self.assertEqual(card.column, self.backlog)
        self.assertIsNone(card.started_at)
        
        # Move through workflow
        card.move_to_column(self.todo, self.user)
        self.assertEqual(card.column, self.todo)
        
        card.move_to_column(self.progress, self.user)
        self.assertEqual(card.column, self.progress)
        self.assertIsNotNone(card.started_at)
        
        card.move_to_column(self.review, self.user)
        self.assertEqual(card.column, self.review)
        
        card.move_to_column(self.done, self.team_lead)
        self.assertEqual(card.column, self.done)
        self.assertIsNotNone(card.completed_at)
        
        # Verify complete history
        history_count = CardHistory.objects.filter(card=card).count()
        self.assertEqual(history_count, 4)  # 4 moves
    
    def test_wip_limit_workflow(self):
        """Test WIP limit enforcement in workflow"""
        # Fill progress column to WIP limit
        for i in range(3):
            card = Card.objects.create(
                column=self.progress,
                title=f'Card {i+1}'
            )
        
        # Try to add another card
        with self.assertRaises(ValidationError):
            card = Card.objects.create(
                column=self.progress,
                title='Exceeding Card'
            )
            self.progress.validate_wip_limit()
    
    def test_collaboration_workflow(self):
        """Test team collaboration on cards"""
        card = Card.objects.create(
            column=self.todo,
            title='Collaboration Card',
            assignee=self.user
        )
        
        # Team lead adds comment
        comment = Comment.objects.create(
            card=card,
            author=self.team_lead,
            content='Please prioritize this task'
        )
        
        # User responds
        response = Comment.objects.create(
            card=card,
            author=self.user,
            content='Will work on this next'
        )
        
        # Move card and add attachment
        card.move_to_column(self.progress, self.user)
        
        attachment = Attachment.objects.create(
            card=card,
            filename='implementation_plan.pdf',
            uploaded_by=self.user
        )
        
        # Verify collaboration elements
        self.assertEqual(card.comments.count(), 2)
        self.assertEqual(card.attachments.count(), 1)
        self.assertTrue(CardHistory.objects.filter(card=card).exists())


if __name__ == '__main__':
    import unittest
    unittest.main()
