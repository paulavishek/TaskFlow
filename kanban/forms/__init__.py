from django import forms
from ..models import Board, Column, Task, TaskLabel, Comment

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TaskLabelForm(forms.ModelForm):
    class Meta:
        model = TaskLabel
        fields = ['name', 'color', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'due_date', 'assigned_to', 'labels', 'priority',
            'estimated_duration_hours', 'estimated_start_date', 'is_milestone', 'predecessors'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local',
                'title': 'When this task should be completed'
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'labels': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'estimated_duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '999',
                'placeholder': '8',
                'title': 'How many hours you estimate this task will take'
            }),
            'estimated_start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'title': 'When you plan to start working on this task'
            }),
            'is_milestone': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'title': 'Mark this task as an important project milestone'
            }),
            'predecessors': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '4',
                'title': 'Select tasks that must be completed before this task can start'
            }),
        }
        help_texts = {
            'estimated_duration_hours': 'Estimated time to complete this task (in hours)',
            'estimated_start_date': 'Planned start date for this task',
            'is_milestone': 'Check if this task represents an important project milestone',
            'predecessors': 'Tasks that must be completed before this task can start',
        }
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        if board:
            self.fields['labels'].queryset = TaskLabel.objects.filter(board=board)
            self.fields['assigned_to'].queryset = board.members.all()
            
            # For predecessors, show other tasks in the same board (excluding self)
            tasks_queryset = Task.objects.filter(column__board=board)
            if self.instance and self.instance.pk:
                # Exclude self from predecessors list
                tasks_queryset = tasks_queryset.exclude(pk=self.instance.pk)
            
            self.fields['predecessors'].queryset = tasks_queryset
            self.fields['predecessors'].widget.choices = [
                (task.id, f"{task.title} ({task.column.name})")
                for task in tasks_queryset
            ]
        
        # Add empty choice for assigned_to
        self.fields['assigned_to'].empty_label = "Not assigned"
        
        # Set default estimated duration if not set
        if not self.instance.pk and not self.initial.get('estimated_duration_hours'):
            self.fields['estimated_duration_hours'].initial = 8

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Add a comment...'}),
        }

class TaskMoveForm(forms.Form):
    column = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'class': 'form-select'}))
    position = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        if board:
            self.fields['column'].queryset = Column.objects.filter(board=board)

class TaskSearchForm(forms.Form):
    column = forms.ModelChoiceField(
        queryset=Column.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'Any Priority')] + Task.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    label = forms.ModelChoiceField(
        queryset=TaskLabel.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    label_category = forms.ChoiceField(
        choices=[
            ('', 'Any Category'),
            ('regular', 'Regular Labels'),
            ('lean', 'Lean Six Sigma Labels'),
            ('lean_va', 'Value-Added'),
            ('lean_nva', 'Necessary Non-Value-Added'),
            ('lean_waste', 'Waste/Eliminate')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    assignee = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search_term = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search tasks...'})
    )
    
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        
        if board:
            self.fields['column'].queryset = Column.objects.filter(board=board)
            self.fields['label'].queryset = TaskLabel.objects.filter(board=board)
            self.fields['assignee'].queryset = board.members.all()