from django.core.management.base import BaseCommand
from kanban.models import Board, TaskLabel

class Command(BaseCommand):
    help = 'Adds predefined Lean Six Sigma labels to all boards'

    def add_arguments(self, parser):
        parser.add_argument('--board_id', type=int, help='The ID of the board to add labels to (optional)')

    def handle(self, *args, **options):
        # Define the Lean Six Sigma labels
        lean_labels = [
            {'name': 'Value-Added', 'color': '#28a745', 'category': 'lean'},  # Green
            {'name': 'Necessary NVA', 'color': '#ffc107', 'category': 'lean'},  # Yellow
            {'name': 'Waste/Eliminate', 'color': '#dc3545', 'category': 'lean'}  # Red
        ]
        
        # Get boards to update
        if options['board_id']:
            boards = Board.objects.filter(id=options['board_id'])
            if not boards.exists():
                self.stdout.write(self.style.ERROR(f"Board with ID {options['board_id']} not found"))
                return
        else:
            boards = Board.objects.all()
        
        # Add labels to each board
        labels_created = 0
        for board in boards:
            for label_data in lean_labels:
                # Check if label already exists
                if not TaskLabel.objects.filter(
                    name=label_data['name'],
                    board=board,
                    category='lean'
                ).exists():
                    TaskLabel.objects.create(
                        name=label_data['name'],
                        color=label_data['color'],
                        category='lean',
                        board=board
                    )
                    labels_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"Added {labels_created} Lean Six Sigma labels to {boards.count()} boards")
        )
