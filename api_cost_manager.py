#!/usr/bin/env python3
"""
API Cost Management Commands

Simple commands to manage and monitor API costs.
Run these commands to check status and manage your protection system.
"""

import json
import os
import sys
from datetime import datetime

def check_status():
    """Check current API cost status"""
    print("=" * 60)
    print("🛡️  API COST PROTECTION STATUS")
    print("=" * 60)
    
    try:
        # Try to import the protection system
        sys.path.append('.')
        from api_protection_system import get_status_report
        
        status = get_status_report()
        
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("💰 COST SUMMARY:")
        print(f"   Daily:   ${status['daily_cost']:.6f} / ${status['daily_limit']:.2f}")
        print(f"   Monthly: ${status['monthly_cost']:.6f} / ${status['monthly_limit']:.2f}")
        print()
        print("🔒 PROTECTION STATUS:")
        print(f"   Daily Protection:   {'🟢 OK' if status['daily_remaining'] > 0 else '🔴 LIMIT REACHED'}")
        print(f"   Monthly Protection: {'🟢 OK' if status['monthly_remaining'] > 0 else '🔴 LIMIT REACHED'}")
        print(f"   Development Mode:   {'🟡 YES' if status['development_mode'] else '🟢 NO'}")
        
        # Usage percentage
        daily_pct = (status['daily_cost'] / status['daily_limit']) * 100
        monthly_pct = (status['monthly_cost'] / status['monthly_limit']) * 100
        
        print()
        print("📊 USAGE PERCENTAGE:")
        print(f"   Daily:   {daily_pct:.1f}%")
        print(f"   Monthly: {monthly_pct:.1f}%")
        
        # Warnings
        if daily_pct > 75:
            print("⚠️  WARNING: Approaching daily limit!")
        if monthly_pct > 75:
            print("⚠️  WARNING: Approaching monthly limit!")
            
    except ImportError:
        print("❌ Protection system not found. Please set up api_protection_system.py first.")
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def reset_daily():
    """Reset daily costs (use carefully!)"""
    print("🔄 Resetting daily costs...")
    
    try:
        cost_file = 'daily_api_costs.json'
        if os.path.exists(cost_file):
            with open(cost_file, 'r') as f:
                data = json.load(f)
            
            today = datetime.now().strftime('%Y-%m-%d')
            if today in data.get('daily_costs', {}):
                old_cost = data['daily_costs'][today]
                data['daily_costs'][today] = 0
                
                with open(cost_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"✅ Reset daily cost from ${old_cost:.6f} to $0.000000")
            else:
                print("ℹ️  No daily costs to reset")
        else:
            print("ℹ️  No cost tracking file found")
            
    except Exception as e:
        print(f"❌ Error resetting daily costs: {e}")

def set_limits():
    """Set new cost limits"""
    print("⚙️  Setting API Cost Limits")
    print("-" * 30)
    
    try:
        daily = input("Enter daily limit (USD, current: $0.50): $").strip()
        monthly = input("Enter monthly limit (USD, current: $5.00): $").strip()
        
        daily = float(daily) if daily else 0.50
        monthly = float(monthly) if monthly else 5.00
        
        # Update environment file
        env_content = f"""# API Cost Protection Limits
DAILY_API_LIMIT={daily}
MONTHLY_API_LIMIT={monthly}
BYPASS_API_LIMITS_DEV=false
DJANGO_DEVELOPMENT=true
"""
        
        with open('.env.protection', 'w') as f:
            f.write(env_content)
        
        print(f"✅ Updated limits: Daily=${daily:.2f}, Monthly=${monthly:.2f}")
        print("ℹ️  Restart your Django server to apply changes")
        
    except ValueError:
        print("❌ Invalid input. Please enter numeric values.")
    except Exception as e:
        print(f"❌ Error setting limits: {e}")

def show_recent_calls():
    """Show recent API calls from log"""
    print("📋 Recent API Calls")
    print("-" * 30)
    
    try:
        if os.path.exists('api_protection.log'):
            with open('api_protection.log', 'r') as f:
                lines = f.readlines()
            
            recent = lines[-20:]  # Last 20 lines
            
            if recent:
                for line in recent:
                    if 'API_COST:' in line:
                        print(f"  {line.strip()}")
            else:
                print("ℹ️  No recent API calls found")
        else:
            print("ℹ️  No protection log file found")
            
    except Exception as e:
        print(f"❌ Error reading log: {e}")

def main():
    """Main command interface"""
    if len(sys.argv) < 2:
        print("Usage: python api_cost_manager.py <command>")
        print("Commands:")
        print("  status  - Check current cost status")
        print("  reset   - Reset daily costs")
        print("  limits  - Set new cost limits")
        print("  recent  - Show recent API calls")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        check_status()
    elif command == 'reset':
        reset_daily()
    elif command == 'limits':
        set_limits()
    elif command == 'recent':
        show_recent_calls()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
