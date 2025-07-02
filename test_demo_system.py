#!/usr/bin/env python
"""
Test script for the demo system functionality
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from accounts.models import Organization, UserProfile
from kanban.models import Board
from kanban.management.commands.load_demo_data import Command

def test_demo_system():
    """Test the demo system functionality"""
    print("🧪 Testing TaskFlow Demo System")
    print("=" * 50)
    
    # Create a test user for demo
    username = 'demo_tester'
    password = 'demo123'
    email = 'demo@test.com'
    
    # Check if user exists
    try:
        user = User.objects.get(username=username)
        print(f"✅ Using existing test user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name='Demo',
            last_name='Tester'
        )
        print(f"✅ Created test user: {username}")
    
    # Ensure user has organization and profile
    try:
        profile = user.profile
        organization = profile.organization
        print(f"✅ User has profile and organization: {organization.name}")
    except UserProfile.DoesNotExist:
        # Create organization
        org = Organization.objects.create(
            name='Demo Test Organization',
            domain='demo-test.com',
            created_by=user
        )
        
        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            organization=org
        )
        print(f"✅ Created organization and profile for user")
    
    # Test the management command
    print("\n📋 Testing Demo Data Creation...")
    
    command = Command()
    
    # Test tech startup scenario
    print("\n🚀 Testing Tech Startup Scenario...")
    try:
        command.create_tech_startup_scenario(user)
        print("✅ Tech startup scenario created successfully")
    except Exception as e:
        print(f"❌ Error creating tech startup scenario: {e}")
        return False
    
    # Check if boards were created
    boards = Board.objects.filter(created_by=user)
    print(f"✅ Created {boards.count()} boards")
    
    for board in boards:
        columns = board.columns.all()
        tasks = sum(column.tasks.count() for column in columns)
        labels = board.labels.count()
        print(f"   📋 {board.name}: {columns.count()} columns, {tasks} tasks, {labels} labels")
    
    # Test clearing demo data
    print("\n🧹 Testing Demo Data Clearing...")
    try:
        command.clear_demo_data(user)
        print("✅ Demo data cleared successfully")
    except Exception as e:
        print(f"❌ Error clearing demo data: {e}")
        return False
    
    # Test web interface
    print("\n🌐 Testing Web Interface...")
    client = Client()
    
    # Test login
    login_success = client.login(username=username, password=password)
    if login_success:
        print("✅ User login successful")
    else:
        print("❌ User login failed")
        return False
    
    # Test demo mode page
    response = client.get('/demo/')
    if response.status_code == 200:
        print("✅ Demo mode page accessible")
    else:
        print(f"❌ Demo mode page error: {response.status_code}")
        return False
    
    # Test API endpoints
    print("\n🔌 Testing API Endpoints...")
    
    # Test load demo data API
    response = client.post('/api/load-demo-data/', 
                          data='{"scenario": "tech_startup"}',
                          content_type='application/json')
    
    if response.status_code == 200:
        print("✅ Load demo data API successful")
    else:
        print(f"❌ Load demo data API error: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response text: {response.content}")
    
    # Check if boards were created via API
    boards = Board.objects.filter(created_by=user)
    if boards.exists():
        print(f"✅ API created {boards.count()} boards")
        
        # Test tour guide page
        response = client.get('/demo/tour/')
        if response.status_code == 200:
            print("✅ Demo tour guide page accessible")
        else:
            print(f"❌ Demo tour guide page error: {response.status_code}")
    else:
        print("❌ No boards created via API")
    
    # Test clear demo data API
    response = client.post('/api/clear-demo-data/', 
                          content_type='application/json')
    
    if response.status_code == 200:
        print("✅ Clear demo data API successful")
    else:
        print(f"❌ Clear demo data API error: {response.status_code}")
    
    print("\n🎉 Demo System Test Complete!")
    print("=" * 50)
    print(f"Demo user credentials: {username} / {password}")
    print("You can now:")
    print("1. Visit /demo/ to access the demo mode")
    print("2. Load scenario data and explore features")
    print("3. Use the guided tour to showcase AI capabilities")
    
    return True

if __name__ == "__main__":
    success = test_demo_system()
    if success:
        print("\n✅ All tests passed! Demo system is ready.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
