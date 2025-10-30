from django import forms
from .models import TaskThreadComment, ChatRoom, ChatMessage
from django.contrib.auth.models import User


class TaskThreadCommentForm(forms.ModelForm):
    """Form for adding real-time comments to tasks"""
    
    class Meta:
        model = TaskThreadComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment... (use @username to mention someone)',
                'style': 'resize: vertical;'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = 'Comment'


class ChatRoomForm(forms.ModelForm):
    """Form for creating/editing chat rooms"""
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Add members to this room'
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Room name (e.g., #frontend-team)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What is this room about?'
            })
        }
    
    def __init__(self, *args, board=None, **kwargs):
        super().__init__(*args, **kwargs)
        if board:
            # Only show members that are part of the board
            self.fields['members'].queryset = board.members.all() if hasattr(board, 'members') else User.objects.all()


class ChatMessageForm(forms.ModelForm):
    """Form for sending messages in a chat room"""
    
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type a message... (use @username to mention)',
                'autocomplete': 'off'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = ''


class MentionForm(forms.Form):
    """Form for autocomplete mentions"""
    search = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Search users...',
            'autocomplete': 'off'
        })
    )
