#!/usr/bin/env python3
"""
Session-Based API Cost Manager

This script manages session-based API costs that reset with each new development session.
"""

import json
import os
import sys
import tempfile
from datetime import datetime

def get_current_session_files():
    """Find the current session's files"""
    temp_dir = tempfile.gettempdir()
    session_files = []
    
    # Find all TaskFlow session files
    for filename in os.listdir(temp_dir):
        if filename.startswith('taskflow_session_') and filename.endswith('.json'):
            filepath = os.path.join(temp_dir, filename)
            session_files.append((filepath, os.path.getctime(filepath)))
    
    if not session_files:
        return None, None
    
    # Sort by creation time and get the most recent
    session_files.sort(key=lambda x: x[1], reverse=True)
    cost_file = session_files[0][0]
    
    # Find corresponding log file
    log_file = cost_file.replace('.json', '.log')
    if not os.path.exists(log_file):
        log_file = None
    
    return cost_file, log_file

def check_session_status():
    """Check current session API cost status"""
    print("=" * 70)
    print("🆕 SESSION-BASED API COST PROTECTION STATUS")
    print("=" * 70)
    
    try:
        # Import the session protection system
        sys.path.append('.')
        from session_protection import get_session_status
        
        status = get_session_status()
        
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🆔 Session ID: {status['session_id']}")
        print(f"⏱️  Session Started: {status['session_start'][:19] if status['session_start'] else 'Unknown'}")
        print()
        print("💰 SESSION COST SUMMARY:")
        print(f"   Current Session: ${status['session_cost']:.6f} / ${status['session_limit']:.2f}")
        print(f"   Remaining Budget: ${status['session_remaining']:.6f}")
        print(f"   Total API Calls: {status['total_api_calls']}")
        print()
        print("🔒 PROTECTION STATUS:")
        session_pct = (status['session_cost'] / status['session_limit']) * 100
        print(f"   Session Protection: {'🟢 OK' if status['session_remaining'] > 0 else '🔴 LIMIT REACHED'}")
        print(f"   Development Mode:   {'🟡 YES' if status['development_mode'] else '🟢 NO'}")
        print()
        print("📊 SESSION USAGE:")
        print(f"   Usage Percentage: {session_pct:.1f}%")
        
        # Warnings
        if session_pct > 75:
            print("⚠️  WARNING: Approaching session limit!")
        elif session_pct > 50:
            print("ℹ️  INFO: Over halfway through session budget")
        
        # Recent calls
        if status['recent_calls']:
            print()
            print("📋 RECENT API CALLS:")
            for call in status['recent_calls']:
                timestamp = call['timestamp'][:19]
                function = call['function']
                cost = call['cost']
                print(f"   {timestamp} | {function:<25} | ${cost:.6f}")
        else:
            print()
            print("📋 No API calls made in this session yet")
        
        print()
        print("🆕 SESSION BENEFITS:")
        print("   ✅ Fresh start with $0.00 each session")
        print("   ✅ No carryover costs from previous sessions")
        print("   ✅ Clean slate for testing and development")
        print(f"   ✅ Session files: {os.path.basename(status['cost_file'])}")
        
    except ImportError:
        print("❌ Session protection system not found. Please set up session_protection.py first.")
    except Exception as e:
        print(f"❌ Error checking session status: {e}")

def reset_session():
    """Start a fresh session by removing current session files"""
    print("🔄 Starting Fresh Session...")
    
    try:
        cost_file, log_file = get_current_session_files()
        
        if cost_file and os.path.exists(cost_file):
            # Show current session info before reset
            with open(cost_file, 'r') as f:
                data = json.load(f)
            
            session_cost = data.get('session_costs', 0.0)
            total_calls = data.get('total_requests', 0)
            
            print(f"📊 Previous session summary:")
            print(f"   Session Cost: ${session_cost:.6f}")
            print(f"   Total API Calls: {total_calls}")
            
            # Remove session files
            os.remove(cost_file)
            print(f"✅ Removed session cost file: {os.path.basename(cost_file)}")
            
            if log_file and os.path.exists(log_file):
                os.remove(log_file)
                print(f"✅ Removed session log file: {os.path.basename(log_file)}")
        else:
            print("ℹ️  No current session files found")
        
        print("🆕 Fresh session will be created on next API call")
        print("💰 Session costs reset to $0.00")
        
    except Exception as e:
        print(f"❌ Error resetting session: {e}")

def show_session_history():
    """Show history of recent sessions"""
    print("📚 Session History")
    print("-" * 40)
    
    try:
        temp_dir = tempfile.gettempdir()
        session_files = []
        
        # Find all TaskFlow session files
        for filename in os.listdir(temp_dir):
            if filename.startswith('taskflow_session_') and filename.endswith('.json'):
                filepath = os.path.join(temp_dir, filename)
                session_files.append((filepath, os.path.getctime(filepath)))
        
        if not session_files:
            print("ℹ️  No session history found")
            return
        
        # Sort by creation time (newest first)
        session_files.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Found {len(session_files)} recent sessions:")
        print()
        
        for i, (filepath, created_time) in enumerate(session_files[:10]):  # Show last 10
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                session_id = data.get('session_id', 'Unknown')
                session_cost = data.get('session_costs', 0.0)
                total_calls = data.get('total_requests', 0)
                created_str = datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')
                
                status = "🟢 Current" if i == 0 else "📁 Archived"
                print(f"{status} {session_id}")
                print(f"   Created: {created_str}")
                print(f"   Cost: ${session_cost:.6f}")
                print(f"   API Calls: {total_calls}")
                print()
                
            except Exception as e:
                print(f"⚠️  Error reading {os.path.basename(filepath)}: {e}")
        
    except Exception as e:
        print(f"❌ Error reading session history: {e}")

def set_session_limits():
    """Set new session limits"""
    print("⚙️  Setting Session Limits")
    print("-" * 30)
    
    try:
        current_daily = os.getenv('DAILY_API_LIMIT', '0.50')
        print(f"Current session limit: ${current_daily}")
        print()
        
        new_limit = input("Enter new session limit (USD): $").strip()
        
        if not new_limit:
            print("ℹ️  No changes made")
            return
        
        new_limit = float(new_limit)
        
        # Update environment file
        env_content = f"""# Session-Based API Protection Configuration
DAILY_API_LIMIT={new_limit}
MONTHLY_API_LIMIT={new_limit * 10}
BYPASS_API_LIMITS_DEV=false
DJANGO_DEVELOPMENT=true
"""
        
        with open('.env.protection', 'w') as f:
            f.write(env_content)
        
        print(f"✅ Updated session limit to: ${new_limit:.2f}")
        print("ℹ️  Restart your Django server to apply changes")
        print("ℹ️  New sessions will use the updated limit")
        
    except ValueError:
        print("❌ Invalid input. Please enter a numeric value.")
    except Exception as e:
        print(f"❌ Error setting limits: {e}")

def main():
    """Main command interface for session-based cost management"""
    if len(sys.argv) < 2:
        print("Usage: python session_cost_manager.py <command>")
        print("Commands:")
        print("  status   - Check current session status")
        print("  reset    - Start a fresh session (reset costs to $0)")
        print("  history  - Show recent session history")
        print("  limits   - Set new session limits")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        check_session_status()
    elif command == 'reset':
        reset_session()
    elif command == 'history':
        show_session_history()
    elif command == 'limits':
        set_session_limits()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
