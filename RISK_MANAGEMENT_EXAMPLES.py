"""
Example: How to Use AI-Powered Risk Management in TaskFlow

This file demonstrates how to use the new risk management features
from Django management commands or in your views.
"""

from kanban.models import Task, Board, Column
from kanban.utils.ai_utils import (
    calculate_task_risk_score,
    generate_risk_mitigation_suggestions,
    assess_task_dependencies_and_risks
)

# Example 1: Calculate Risk for a Task Programmatically
# ====================================================

def assess_task_risk_example():
    """
    Example: Calculate risk score for a task programmatically
    """
    # Task details
    task_title = "Implement Payment Gateway Integration"
    task_description = """
    Integrate Stripe payment gateway into the checkout process.
    This involves API authentication, payment processing, error handling,
    and PCI compliance considerations.
    """
    task_priority = "high"
    board_context = "E-commerce Platform - Q4 Feature Release"
    
    # Calculate risk
    risk_analysis = calculate_task_risk_score(
        task_title,
        task_description,
        task_priority,
        board_context
    )
    
    if risk_analysis:
        print("✅ Risk Analysis Complete")
        print(f"Likelihood: {risk_analysis['likelihood']['score']}/3")
        print(f"Impact: {risk_analysis['impact']['score']}/3")
        print(f"Risk Score: {risk_analysis['risk_assessment']['risk_score']}/9")
        print(f"Risk Level: {risk_analysis['risk_assessment']['risk_level']}")
        print(f"Priority: {risk_analysis['risk_assessment']['priority_ranking']}")
        print("\nKey Factors:")
        for factor in risk_analysis['likelihood']['key_factors']:
            print(f"  • {factor}")
        
        return risk_analysis
    else:
        print("❌ Failed to analyze risk")
        return None


# Example 2: Generate Mitigation Strategies
# =========================================

def get_mitigation_strategies_example(risk_analysis):
    """
    Example: Get mitigation strategies for a high-risk task
    """
    if not risk_analysis:
        print("⚠️  No risk analysis provided")
        return
    
    task_title = "Implement Payment Gateway Integration"
    task_description = """
    Integrate Stripe payment gateway into the checkout process.
    """
    risk_likelihood = risk_analysis['likelihood']['score']
    risk_impact = risk_analysis['impact']['score']
    risk_indicators = risk_analysis['risk_indicators']
    
    # Generate mitigation suggestions
    mitigation_suggestions = generate_risk_mitigation_suggestions(
        task_title,
        task_description,
        risk_likelihood,
        risk_impact,
        risk_indicators
    )
    
    if mitigation_suggestions:
        print("\n✅ Mitigation Strategies Generated")
        print(f"Found {len(mitigation_suggestions)} strategies:\n")
        
        for i, strategy in enumerate(mitigation_suggestions, 1):
            print(f"{i}. {strategy['strategy_type'].upper()}: {strategy['title']}")
            print(f"   Description: {strategy['description']}")
            print(f"   Timeline: {strategy['timeline']}")
            print(f"   Effectiveness: {strategy['estimated_effectiveness']}%")
            print(f"   Priority: {strategy['priority']}")
            print(f"   Resources: {strategy['resources_required']}")
            print()
    else:
        print("❌ Failed to generate mitigation strategies")


# Example 3: Assess Task Dependencies
# ==================================

def assess_dependencies_example():
    """
    Example: Assess cascading risks from task dependencies
    """
    board = Board.objects.first()  # Get any board
    if not board:
        print("⚠️  No board found")
        return
    
    # Get related tasks
    tasks_data = []
    for task in board.columns.first().tasks.all()[:10]:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'priority': task.priority,
            'status': task.column.name
        })
    
    if not tasks_data:
        print("⚠️  No tasks found")
        return
    
    # Assess dependencies
    dependency_analysis = assess_task_dependencies_and_risks(
        "Payment Gateway Integration",
        tasks_data
    )
    
    if dependency_analysis:
        print("✅ Dependency Analysis Complete")
        print(f"Overall Dependency Risk: {dependency_analysis.get('overall_dependency_risk', 'N/A')}")
        print(f"\nCritical Dependencies: {len(dependency_analysis.get('critical_dependencies', []))}")
        print(f"Cascading Risks: {len(dependency_analysis.get('cascading_risks', []))}")
        print(f"Bottleneck Areas: {dependency_analysis.get('bottleneck_areas', [])}")
    else:
        print("❌ Failed to assess dependencies")


# Example 4: Update Task with Risk Assessment
# ==========================================

def update_task_with_risk_example():
    """
    Example: Get a task and update it with risk assessment
    """
    try:
        # Get a task
        task = Task.objects.filter(column__board__isnull=False).first()
        if not task:
            print("⚠️  No task found")
            return
        
        print(f"📋 Assessing task: {task.title}")
        
        # Calculate risk
        risk_analysis = calculate_task_risk_score(
            task.title,
            task.description or "",
            task.priority,
            f"Board: {task.column.board.name}"
        )
        
        if risk_analysis:
            # Update task fields
            task.risk_likelihood = risk_analysis['likelihood']['score']
            task.risk_impact = risk_analysis['impact']['score']
            task.risk_score = risk_analysis['risk_assessment']['risk_score']
            task.risk_level = risk_analysis['risk_assessment']['risk_level'].lower()
            task.risk_indicators = risk_analysis['risk_indicators']
            task.risk_analysis = risk_analysis
            
            from django.utils import timezone
            task.last_risk_assessment = timezone.now()
            task.save()
            
            print(f"✅ Task updated successfully!")
            print(f"   Risk Level: {task.risk_level}")
            print(f"   Risk Score: {task.risk_score}/9")
            print(f"   Likelihood: {task.risk_likelihood}/3")
            print(f"   Impact: {task.risk_impact}/3")
        else:
            print("❌ Failed to calculate risk")
            
    except Exception as e:
        print(f"❌ Error: {e}")


# Example 5: Bulk Risk Assessment
# ==============================

def bulk_assess_risks_example():
    """
    Example: Assess risks for all high-priority tasks
    """
    board = Board.objects.first()
    if not board:
        print("⚠️  No board found")
        return
    
    # Get high-priority tasks
    high_priority_tasks = Task.objects.filter(
        column__board=board,
        priority__in=['high', 'urgent']
    )[:5]
    
    if not high_priority_tasks:
        print("⚠️  No high-priority tasks found")
        return
    
    print(f"🔍 Assessing {high_priority_tasks.count()} high-priority tasks...\n")
    
    from django.utils import timezone
    
    for task in high_priority_tasks:
        print(f"Assessing: {task.title}...", end=" ")
        
        risk_analysis = calculate_task_risk_score(
            task.title,
            task.description or "",
            task.priority,
            f"Board: {task.column.board.name}"
        )
        
        if risk_analysis:
            # Update task
            task.risk_likelihood = risk_analysis['likelihood']['score']
            task.risk_impact = risk_analysis['impact']['score']
            task.risk_score = risk_analysis['risk_assessment']['risk_score']
            task.risk_level = risk_analysis['risk_assessment']['risk_level'].lower()
            task.risk_indicators = risk_analysis['risk_indicators']
            task.risk_analysis = risk_analysis
            task.last_risk_assessment = timezone.now()
            task.save()
            
            print(f"✅ (Risk: {task.risk_level.upper()})")
        else:
            print("⚠️ Failed")
    
    print("\n✅ Bulk assessment complete!")


# Example 6: Risk Report
# ======================

def generate_risk_report_example():
    """
    Example: Generate a risk report for a board
    """
    board = Board.objects.first()
    if not board:
        print("⚠️  No board found")
        return
    
    tasks = Task.objects.filter(column__board=board)
    
    print("=" * 60)
    print(f"📊 RISK REPORT FOR BOARD: {board.name}")
    print("=" * 60)
    print()
    
    # Group by risk level
    risk_distribution = {}
    total_risk_score = 0
    
    for task in tasks:
        if task.risk_level:
            level = task.risk_level.upper()
            if level not in risk_distribution:
                risk_distribution[level] = []
            risk_distribution[level].append(task)
            if task.risk_score:
                total_risk_score += task.risk_score
    
    # Print distribution
    print("📈 Risk Distribution:")
    print("-" * 60)
    for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = len(risk_distribution.get(level, []))
        percentage = (count / len(tasks) * 100) if tasks else 0
        print(f"  {level:10} : {count:3} tasks ({percentage:5.1f}%)")
    
    print()
    print("🚨 Critical & High-Risk Tasks:")
    print("-" * 60)
    
    critical_high = risk_distribution.get('CRITICAL', []) + risk_distribution.get('HIGH', [])
    if critical_high:
        for task in critical_high:
            print(f"  • {task.title}")
            print(f"    Priority: {task.priority.upper()}")
            print(f"    Risk Score: {task.risk_score or 'N/A'}/9")
            print(f"    Assigned to: {task.assigned_to.username if task.assigned_to else 'Unassigned'}")
            print()
    else:
        print("  No critical or high-risk tasks")
    
    print("=" * 60)


# Management Command Example
# =========================

def management_command_example():
    """
    Example: Django management command to assess all tasks
    
    Usage: python manage.py assess_task_risks
    
    Add this to kanban/management/commands/assess_task_risks.py:
    """
    
    from django.core.management.base import BaseCommand
    from django.utils import timezone
    from kanban.models import Task, Board
    from kanban.utils.ai_utils import calculate_task_risk_score
    
    class Command(BaseCommand):
        help = 'Assess risks for all tasks or specific board'
        
        def add_arguments(self, parser):
            parser.add_argument(
                '--board-id',
                type=int,
                help='Specific board to assess'
            )
            parser.add_argument(
                '--priority',
                choices=['low', 'medium', 'high', 'urgent'],
                help='Only assess tasks with specific priority'
            )
        
        def handle(self, *args, **options):
            board_id = options.get('board_id')
            priority = options.get('priority')
            
            # Build query
            query = Task.objects.all()
            
            if board_id:
                query = query.filter(column__board_id=board_id)
            
            if priority:
                query = query.filter(priority=priority)
            
            self.stdout.write(f"🔍 Assessing {query.count()} tasks...")
            
            for i, task in enumerate(query, 1):
                self.stdout.write(f"[{i}] {task.title}...", ending=" ")
                
                risk_analysis = calculate_task_risk_score(
                    task.title,
                    task.description or "",
                    task.priority,
                    f"Board: {task.column.board.name}"
                )
                
                if risk_analysis:
                    task.risk_likelihood = risk_analysis['likelihood']['score']
                    task.risk_impact = risk_analysis['impact']['score']
                    task.risk_score = risk_analysis['risk_assessment']['risk_score']
                    task.risk_level = risk_analysis['risk_assessment']['risk_level'].lower()
                    task.risk_indicators = risk_analysis['risk_indicators']
                    task.risk_analysis = risk_analysis
                    task.last_risk_assessment = timezone.now()
                    task.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ ({task.risk_level.upper()})")
                    )
                else:
                    self.stdout.write(self.style.WARNING("⚠️"))
            
            self.stdout.write(self.style.SUCCESS("✅ Assessment complete!"))


# Entry Point
# ===========

if __name__ == "__main__":
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
    django.setup()
    
    print("\n🛡️  AI-Powered Risk Management Examples\n")
    print("=" * 60)
    
    # Example 1
    print("\n1️⃣  CALCULATE TASK RISK")
    print("-" * 60)
    risk_analysis = assess_task_risk_example()
    
    # Example 2
    if risk_analysis:
        print("\n2️⃣  GENERATE MITIGATION STRATEGIES")
        print("-" * 60)
        get_mitigation_strategies_example(risk_analysis)
    
    # Example 3
    print("\n3️⃣  ASSESS TASK DEPENDENCIES")
    print("-" * 60)
    assess_dependencies_example()
    
    # Example 4
    print("\n4️⃣  UPDATE TASK WITH RISK ASSESSMENT")
    print("-" * 60)
    update_task_with_risk_example()
    
    # Example 5
    print("\n5️⃣  BULK RISK ASSESSMENT")
    print("-" * 60)
    bulk_assess_risks_example()
    
    # Example 6
    print("\n6️⃣  GENERATE RISK REPORT")
    print("-" * 60)
    generate_risk_report_example()
    
    print("\n" + "=" * 60)
    print("✅ Examples complete!\n")
