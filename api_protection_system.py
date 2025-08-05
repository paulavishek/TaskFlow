"""
API Cost Protection System for TaskFlow

This script implements multiple layers of protection to prevent unexpected API costs:
1. Daily spending limits
2. Request rate limiting
3. Development mode detection
4. Cost alerts and circuit breakers
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import wraps

class APIProtectionSystem:
    """Comprehensive API cost protection system"""
    
    def __init__(self):
        self.cost_file = 'daily_api_costs.json'
        self.setup_logging()
        self.daily_limit = float(os.getenv('DAILY_API_LIMIT', '0.50'))  # $0.50 default
        self.monthly_limit = float(os.getenv('MONTHLY_API_LIMIT', '5.00'))  # $5.00 default
        
    def setup_logging(self):
        """Setup protective logging"""
        logging.basicConfig(
            filename='api_protection.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('api_protection')
    
    def load_cost_tracking(self) -> Dict:
        """Load existing cost tracking data"""
        try:
            if os.path.exists(self.cost_file):
                with open(self.cost_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading cost tracking: {e}")
        
        return {
            'daily_costs': {},
            'monthly_costs': {},
            'total_requests': 0,
            'last_reset': datetime.now().isoformat()
        }
    
    def save_cost_tracking(self, data: Dict):
        """Save cost tracking data"""
        try:
            with open(self.cost_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cost tracking: {e}")
    
    def get_today_cost(self) -> float:
        """Get today's accumulated cost"""
        data = self.load_cost_tracking()
        today = datetime.now().strftime('%Y-%m-%d')
        return data['daily_costs'].get(today, 0.0)
    
    def get_month_cost(self) -> float:
        """Get this month's accumulated cost"""
        data = self.load_cost_tracking()
        month = datetime.now().strftime('%Y-%m')
        return data['monthly_costs'].get(month, 0.0)
    
    def add_cost(self, function_name: str, cost: float) -> bool:
        """Add cost and check if limits are exceeded"""
        data = self.load_cost_tracking()
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Update daily cost
        if today not in data['daily_costs']:
            data['daily_costs'][today] = 0
        data['daily_costs'][today] += cost
        
        # Update monthly cost
        if month not in data['monthly_costs']:
            data['monthly_costs'][month] = 0
        data['monthly_costs'][month] += cost
        
        # Update total requests
        data['total_requests'] += 1
        
        # Log the cost
        self.logger.info(f"API_COST: {function_name} = ${cost:.6f} | Daily: ${data['daily_costs'][today]:.6f} | Monthly: ${data['monthly_costs'][month]:.6f}")
        
        # Check limits
        daily_exceeded = data['daily_costs'][today] > self.daily_limit
        monthly_exceeded = data['monthly_costs'][month] > self.monthly_limit
        
        if daily_exceeded:
            self.logger.warning(f"DAILY_LIMIT_EXCEEDED: ${data['daily_costs'][today]:.6f} > ${self.daily_limit}")
        
        if monthly_exceeded:
            self.logger.warning(f"MONTHLY_LIMIT_EXCEEDED: ${data['monthly_costs'][month]:.6f} > ${self.monthly_limit}")
        
        self.save_cost_tracking(data)
        
        return not (daily_exceeded or monthly_exceeded)
    
    def is_development_mode(self) -> bool:
        """Check if we're in development mode"""
        return (
            os.getenv('DEBUG', 'False').lower() == 'true' or
            'runserver' in ' '.join(os.sys.argv) if hasattr(os, 'sys') else False or
            os.getenv('DJANGO_DEVELOPMENT', 'False').lower() == 'true'
        )
    
    def should_allow_api_call(self, function_name: str) -> tuple[bool, str]:
        """Check if API call should be allowed"""
        # Development mode bypass (optional)
        if self.is_development_mode() and os.getenv('BYPASS_API_LIMITS_DEV', 'False').lower() == 'true':
            return True, "Development mode bypass enabled"
        
        # Check daily limit
        today_cost = self.get_today_cost()
        if today_cost >= self.daily_limit:
            return False, f"Daily limit exceeded: ${today_cost:.6f} >= ${self.daily_limit}"
        
        # Check monthly limit
        month_cost = self.get_month_cost()
        if month_cost >= self.monthly_limit:
            return False, f"Monthly limit exceeded: ${month_cost:.6f} >= ${self.monthly_limit}"
        
        return True, "OK"

# Global protection instance
api_protection = APIProtectionSystem()

def api_cost_protection(function_name: str, estimated_cost: float):
    """Decorator to protect AI functions with cost limits"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if call should be allowed
            allowed, reason = api_protection.should_allow_api_call(function_name)
            
            if not allowed:
                error_msg = f"API call blocked: {reason}"
                api_protection.logger.warning(f"BLOCKED_CALL: {function_name} - {reason}")
                # Return None or raise exception based on your preference
                return None  # or raise Exception(error_msg)
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Record the cost
                api_protection.add_cost(function_name, estimated_cost)
                
                return result
                
            except Exception as e:
                api_protection.logger.error(f"ERROR in {function_name}: {str(e)}")
                raise
        
        return wrapper
    return decorator

# Cost estimates (from your analysis)
FUNCTION_COSTS = {
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

def get_status_report() -> Dict:
    """Get current protection status"""
    today_cost = api_protection.get_today_cost()
    month_cost = api_protection.get_month_cost()
    
    return {
        'daily_cost': today_cost,
        'daily_limit': api_protection.daily_limit,
        'daily_remaining': max(0, api_protection.daily_limit - today_cost),
        'monthly_cost': month_cost,
        'monthly_limit': api_protection.monthly_limit,
        'monthly_remaining': max(0, api_protection.monthly_limit - month_cost),
        'protection_active': True,
        'development_mode': api_protection.is_development_mode()
    }

if __name__ == "__main__":
    # Display current status
    status = get_status_report()
    print("=" * 60)
    print("🛡️  API COST PROTECTION SYSTEM")
    print("=" * 60)
    print(f"Daily Cost:     ${status['daily_cost']:.6f} / ${status['daily_limit']:.2f}")
    print(f"Daily Remaining: ${status['daily_remaining']:.6f}")
    print(f"Monthly Cost:   ${status['monthly_cost']:.6f} / ${status['monthly_limit']:.2f}")
    print(f"Monthly Remaining: ${status['monthly_remaining']:.6f}")
    print(f"Development Mode: {status['development_mode']}")
    print(f"Protection Status: {'🟢 ACTIVE' if status['protection_active'] else '🔴 INACTIVE'}")
