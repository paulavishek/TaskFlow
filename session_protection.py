"""
Session-Based API Protection System for TaskFlow

This system provides fresh cost tracking for each development session,
preventing previous session costs from affecting current billing.
"""

import os
import json
import logging
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import wraps

class SessionBasedAPIProtection:
    """Session-based API cost protection that resets each time you start working"""
    
    def __init__(self):
        # Use session-specific temporary files
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.cost_file = os.path.join(tempfile.gettempdir(), f'taskflow_session_{self.session_id}.json')
        self.session_log = os.path.join(tempfile.gettempdir(), f'taskflow_session_{self.session_id}.log')
        
        self.setup_logging()
        self.daily_limit = float(os.getenv('DAILY_API_LIMIT', '0.50'))
        self.monthly_limit = float(os.getenv('MONTHLY_API_LIMIT', '5.00'))
        
        # Initialize fresh session
        self.initialize_fresh_session()
        
    def initialize_fresh_session(self):
        """Initialize a completely fresh session with zero costs"""
        self.logger.info(f"🆕 STARTING FRESH SESSION: {self.session_id}")
        self.logger.info(f"📊 Session limits: Daily=${self.daily_limit:.2f}, Monthly=${self.monthly_limit:.2f}")
        
        # Clean up old session files (optional - keeps last 5 sessions)
        self.cleanup_old_sessions()
        
        # Create fresh cost tracking
        fresh_data = {
            'session_id': self.session_id,
            'session_start': datetime.now().isoformat(),
            'session_costs': 0.0,
            'api_calls': [],
            'total_requests': 0,
            'daily_limit': self.daily_limit,
            'monthly_limit': self.monthly_limit
        }
        
        self.save_cost_tracking(fresh_data)
        self.logger.info("✅ Fresh session initialized - all costs reset to $0.00")
        
    def cleanup_old_sessions(self):
        """Clean up old session files (keep last 5 sessions)"""
        try:
            temp_dir = tempfile.gettempdir()
            session_files = []
            
            # Find all TaskFlow session files
            for filename in os.listdir(temp_dir):
                if filename.startswith('taskflow_session_'):
                    filepath = os.path.join(temp_dir, filename)
                    session_files.append((filepath, os.path.getctime(filepath)))
            
            # Sort by creation time and keep only the 5 most recent
            session_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old files (keep 5 most recent)
            for filepath, _ in session_files[5:]:
                try:
                    os.remove(filepath)
                    self.logger.info(f"🧹 Cleaned up old session file: {os.path.basename(filepath)}")
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up old sessions: {e}")
        
    def setup_logging(self):
        """Setup session-specific logging"""
        # Create a session-specific logger
        logger = logging.getLogger(f'session_protection_{self.session_id}')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler for session log
        file_handler = logging.FileHandler(self.session_log)
        file_handler.setLevel(logging.INFO)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - SESSION - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self.logger = logger
    
    def load_cost_tracking(self) -> Dict:
        """Load session cost tracking data"""
        try:
            if os.path.exists(self.cost_file):
                with open(self.cost_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading session cost tracking: {e}")
        
        # Return fresh session data if loading fails
        return {
            'session_id': self.session_id,
            'session_start': datetime.now().isoformat(),
            'session_costs': 0.0,
            'api_calls': [],
            'total_requests': 0,
            'daily_limit': self.daily_limit,
            'monthly_limit': self.monthly_limit
        }
    
    def save_cost_tracking(self, data: Dict):
        """Save session cost tracking data"""
        try:
            with open(self.cost_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving session cost tracking: {e}")
    
    def get_session_cost(self) -> float:
        """Get current session's accumulated cost"""
        data = self.load_cost_tracking()
        return data.get('session_costs', 0.0)
    
    def add_cost(self, function_name: str, cost: float) -> bool:
        """Add cost to current session and check limits"""
        data = self.load_cost_tracking()
        
        # Update session cost
        data['session_costs'] = data.get('session_costs', 0.0) + cost
        data['total_requests'] = data.get('total_requests', 0) + 1
        
        # Add to call history
        if 'api_calls' not in data:
            data['api_calls'] = []
        
        call_record = {
            'timestamp': datetime.now().isoformat(),
            'function': function_name,
            'cost': cost,
            'session_total': data['session_costs']
        }
        data['api_calls'].append(call_record)
        
        # Log the cost
        self.logger.info(f"💰 API_CALL: {function_name} = ${cost:.6f} | Session Total: ${data['session_costs']:.6f}")
        
        # Check limits (use session cost for both daily and monthly since it's per-session)
        daily_exceeded = data['session_costs'] > self.daily_limit
        
        if daily_exceeded:
            self.logger.warning(f"🚨 SESSION_LIMIT_EXCEEDED: ${data['session_costs']:.6f} > ${self.daily_limit}")
            self.logger.warning("🛑 ALL FURTHER API CALLS BLOCKED FOR THIS SESSION")
        
        self.save_cost_tracking(data)
        
        return not daily_exceeded
    
    def is_development_mode(self) -> bool:
        """Check if we're in development mode"""
        return (
            os.getenv('DEBUG', 'False').lower() == 'true' or
            'runserver' in ' '.join(os.sys.argv) if hasattr(os, 'sys') else False or
            os.getenv('DJANGO_DEVELOPMENT', 'False').lower() == 'true'
        )
    
    def should_allow_api_call(self, function_name: str) -> tuple[bool, str]:
        """Check if API call should be allowed in this session"""
        # Development mode bypass (optional)
        if self.is_development_mode() and os.getenv('BYPASS_API_LIMITS_DEV', 'False').lower() == 'true':
            return True, "Development mode bypass enabled"
        
        # Check session limit (using daily limit as session limit)
        session_cost = self.get_session_cost()
        if session_cost >= self.daily_limit:
            return False, f"Session limit exceeded: ${session_cost:.6f} >= ${self.daily_limit}"
        
        return True, "OK"
    
    def get_session_summary(self) -> Dict:
        """Get comprehensive session summary"""
        data = self.load_cost_tracking()
        session_cost = data.get('session_costs', 0.0)
        
        return {
            'session_id': self.session_id,
            'session_start': data.get('session_start'),
            'session_cost': session_cost,
            'session_limit': self.daily_limit,
            'session_remaining': max(0, self.daily_limit - session_cost),
            'total_api_calls': data.get('total_requests', 0),
            'recent_calls': data.get('api_calls', [])[-5:],  # Last 5 calls
            'protection_active': True,
            'development_mode': self.is_development_mode(),
            'cost_file': self.cost_file,
            'log_file': self.session_log
        }

# Global session-based protection instance
session_protection = SessionBasedAPIProtection()

def session_api_protection(function_name: str, estimated_cost: float):
    """Decorator to protect AI functions with session-based cost limits"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if call should be allowed
            allowed, reason = session_protection.should_allow_api_call(function_name)
            
            if not allowed:
                error_msg = f"API call blocked: {reason}"
                session_protection.logger.warning(f"🚫 BLOCKED_CALL: {function_name} - {reason}")
                # Return None instead of making API call
                return None
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Record the cost only if the call was successful
                if result is not None:
                    session_protection.add_cost(function_name, estimated_cost)
                
                return result
                
            except Exception as e:
                session_protection.logger.error(f"❌ ERROR in {function_name}: {str(e)}")
                raise
        
        return wrapper
    return decorator

# Cost estimates (same as before)
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

def get_session_status() -> Dict:
    """Get current session protection status"""
    return session_protection.get_session_summary()

if __name__ == "__main__":
    # Display current session status
    status = get_session_status()
    print("=" * 70)
    print("🆕 SESSION-BASED API COST PROTECTION")
    print("=" * 70)
    print(f"Session ID:      {status['session_id']}")
    print(f"Session Started: {status['session_start']}")
    print(f"Session Cost:    ${status['session_cost']:.6f} / ${status['session_limit']:.2f}")
    print(f"Session Remaining: ${status['session_remaining']:.6f}")
    print(f"Total API Calls: {status['total_api_calls']}")
    print(f"Development Mode: {status['development_mode']}")
    print(f"Protection Status: {'🟢 ACTIVE' if status['protection_active'] else '🔴 INACTIVE'}")
    print()
    print(f"📁 Session Files:")
    print(f"   Cost Tracking: {status['cost_file']}")
    print(f"   Session Log:   {status['log_file']}")
    print()
    if status['recent_calls']:
        print("📋 Recent API Calls:")
        for call in status['recent_calls']:
            print(f"   {call['timestamp'][:19]} | {call['function']} | ${call['cost']:.6f}")
    else:
        print("📋 No API calls made in this session yet")
