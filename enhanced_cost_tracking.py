"""
Enhanced Cost Tracking for TaskFlow AI Features

This script shows how to add cost logging to your existing AI functions.
Run this to see how to modify your ai_utils.py for better cost tracking.
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime

# Cost estimates per function (from your analysis)
AI_FUNCTION_COSTS = {
    'generate_task_description': 0.000101,
    'summarize_comments': 0.000097,
    'suggest_lean_classification': 0.000045,
    'summarize_board_analytics': 0.000240,
    'suggest_task_priority': 0.000090,
    'predict_realistic_deadline': 0.000109,
    'recommend_board_columns': 0.000142,
    'suggest_task_breakdown': 0.000176,
    'analyze_workflow_optimization': 0.000232,
    'analyze_critical_path': 0.000285,
    'extract_tasks_from_transcript': 0.000232,
    'enhance_task_description': 0.000139,
}

class APILogger:
    """Class to handle API cost logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('api_costs')
        self.setup_logging()
        self.daily_costs = {}
    
    def setup_logging(self):
        """Setup logging configuration"""
        if not self.logger.handlers:
            # Create file handler
            handler = logging.FileHandler('api_costs.log')
            handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_api_call(self, function_name: str, success: bool = True, 
                     actual_cost: Optional[float] = None):
        """Log an API call with cost estimation"""
        estimated_cost = AI_FUNCTION_COSTS.get(function_name, 0.001)
        cost = actual_cost if actual_cost else estimated_cost
        
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.daily_costs:
            self.daily_costs[today] = 0
        self.daily_costs[today] += cost
        
        status = "SUCCESS" if success else "FAILED"
        
        self.logger.info(
            f"API_CALL | {function_name} | {status} | "
            f"Cost: ${cost:.6f} | Daily Total: ${self.daily_costs[today]:.6f}"
        )
        
        # Log warning if daily costs exceed threshold
        if self.daily_costs[today] > 0.10:  # $0.10 threshold
            self.logger.warning(
                f"COST_ALERT | Daily costs exceeded $0.10: ${self.daily_costs[today]:.6f}"
            )
    
    def get_daily_summary(self) -> Dict:
        """Get summary of today's costs"""
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            'date': today,
            'total_cost': self.daily_costs.get(today, 0),
            'cost_formatted': f"${self.daily_costs.get(today, 0):.6f}"
        }

# Global logger instance
api_logger = APILogger()

def enhanced_ai_wrapper(function_name: str):
    """Decorator to add cost logging to AI functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                api_logger.log_api_call(function_name, success=True)
                return result
            except Exception as e:
                api_logger.log_api_call(function_name, success=False)
                raise e
        return wrapper
    return decorator

# Example of how to modify your existing functions:
def show_enhanced_function_example():
    """Show how to enhance existing AI functions with cost logging"""
    
    example_code = '''
# In your kanban/utils/ai_utils.py, modify functions like this:

from .enhanced_cost_tracking import api_logger

def generate_task_description(title: str) -> Optional[str]:
    """
    Generate a detailed task description with cost logging
    """
    try:
        # Log the start of API call
        api_logger.log_api_call("generate_task_description", success=True)
        
        model = get_model()
        if not model:
            return None
            
        prompt = f"""
        Based on this task title: "{title}", generate a detailed task description 
        with an objective and a checklist of smaller steps.
        
        Format your response like this (in Markdown):
        
        **Objective:** [Brief description of what this task aims to accomplish]
        
        **Checklist:**
        - [ ] First subtask
        - [ ] Second subtask
        - [ ] Third subtask
        (and so on)
        
        Keep it concise but thorough. Include approximately 4-6 subtasks.
        """
        
        response = model.generate_content(prompt)
        if response:
            return response.text.strip()
        return None
        
    except Exception as e:
        # Log the failed API call
        api_logger.log_api_call("generate_task_description", success=False)
        logger.error(f"Error generating task description: {str(e)}")
        return None

# Similarly for other functions:
def summarize_board_analytics(analytics_data: Dict) -> Optional[str]:
    try:
        api_logger.log_api_call("summarize_board_analytics", success=True)
        
        # ... existing implementation ...
        
    except Exception as e:
        api_logger.log_api_call("summarize_board_analytics", success=False)
        logger.error(f"Error summarizing board analytics: {str(e)}")
        return None
'''
    
    print("=" * 80)
    print("🔧 HOW TO ENHANCE YOUR AI FUNCTIONS WITH COST TRACKING")
    print("=" * 80)
    print(example_code)

def create_cost_monitoring_script():
    """Create a script to monitor API costs"""
    
    monitoring_script = '''
#!/usr/bin/env python3
"""
API Cost Monitor for TaskFlow
Run this script to check your daily API costs
"""

import os
import sys
sys.path.append('.')

def check_daily_costs():
    """Check today's API costs"""
    try:
        from enhanced_cost_tracking import api_logger
        
        summary = api_logger.get_daily_summary()
        print(f"📊 Today's API Costs ({summary['date']}):")
        print(f"💰 Total: {summary['cost_formatted']}")
        
        # Read recent log entries
        if os.path.exists('api_costs.log'):
            with open('api_costs.log', 'r') as f:
                lines = f.readlines()
                recent_calls = lines[-10:]  # Last 10 calls
                
            print("\\n🔍 Recent API Calls:")
            for call in recent_calls:
                print(f"  {call.strip()}")
        else:
            print("\\n📝 No API cost log found yet.")
            
    except Exception as e:
        print(f"Error checking costs: {e}")

if __name__ == "__main__":
    check_daily_costs()
'''
    
    with open('check_api_costs.py', 'w') as f:
        f.write(monitoring_script)
    
    print("✅ Created check_api_costs.py - run this to monitor your daily costs")

def main():
    """Main function to demonstrate cost tracking setup"""
    print("=" * 80)
    print("🚀 TASKFLOW API COST TRACKING SETUP")
    print("=" * 80)
    print()
    
    print("📋 WHAT THIS SCRIPT PROVIDES:")
    print("• Enhanced logging for all AI API calls")
    print("• Real-time cost tracking and alerts")
    print("• Daily cost summaries")
    print("• Integration with your existing AI functions")
    print()
    
    print("🔧 IMPLEMENTATION STEPS:")
    print("1. Add the APILogger class to your project")
    print("2. Modify your AI functions to use api_logger.log_api_call()")
    print("3. Monitor costs with the generated scripts")
    print("4. Set up daily cost alerts")
    print()
    
    # Show example
    show_enhanced_function_example()
    
    # Create monitoring script
    create_cost_monitoring_script()
    
    print("\n" + "=" * 80)
    print("✅ COST TRACKING SETUP COMPLETE")
    print("=" * 80)
    print("Now you can:")
    print("• Track exactly which AI features are costing money")
    print("• Get daily cost summaries")
    print("• Receive alerts when costs exceed thresholds")
    print("• Analyze usage patterns to optimize costs")

if __name__ == "__main__":
    main()
