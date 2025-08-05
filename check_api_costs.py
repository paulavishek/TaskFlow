#!/usr/bin/env python3
"""
API Cost Monitor for TaskFlow
Run this script to check your daily API costs
"""

import os
import sys
from datetime import datetime

def check_daily_costs():
    """Check today's API costs from log file"""
    try:
        if os.path.exists('api_costs.log'):
            print("=" * 50)
            print("API COST MONITOR - TaskFlow")
            print("=" * 50)
            
            with open('api_costs.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            today = datetime.now().strftime('%Y-%m-%d')
            today_calls = [line for line in lines if today in line]
            
            if today_calls:
                print(f"Today's Activity ({today}):")
                print(f"Total API calls: {len(today_calls)}")
                print("\nRecent calls:")
                for call in today_calls[-5:]:  # Last 5 calls
                    print(f"  {call.strip()}")
            else:
                print(f"No API calls found for today ({today})")
                
            print(f"\nTotal logged calls: {len(lines)}")
            
        else:
            print("No API cost log found yet.")
            print("Log file will be created when you use AI features.")
            
    except Exception as e:
        print(f"Error checking costs: {e}")

if __name__ == "__main__":
    check_daily_costs()
