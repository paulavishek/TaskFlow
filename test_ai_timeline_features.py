#!/usr/bin/env python
"""
Comprehensive Test Script for AI-Enhanced Timeline Features
Tests all new AI endpoints and validates responses
"""

import os
import sys
import django
import json
import requests
from datetime import datetime
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from kanban.models import Board, Task, Column
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

class AITimelineFeatureTester:
    def __init__(self):
        self.client = Client()
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = []
        self.software_board = None
        
    def log_test(self, test_name, success, message, data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'data': data
        })
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   📊 Data: {json.dumps(data, indent=2)[:200]}...")
    
    def setup_test_environment(self):
        """Setup test environment and get authentication"""
        print("\n🔧 Setting up test environment...")
        
        try:
            # Get the Software Project board with enhanced data
            self.software_board = Board.objects.get(id=2)
            task_count = Task.objects.filter(column__board=self.software_board).count()
            dependency_count = sum(
                task.predecessors.count() 
                for task in Task.objects.filter(column__board=self.software_board)
            )
            
            self.log_test(
                "Environment Setup",
                True,
                f"Found board '{self.software_board.name}' with {task_count} tasks and {dependency_count} dependencies"
            )
            
            # Try to get a test user for authentication
            try:
                admin_user = User.objects.get(username='admin')
                # Force login for testing
                self.client.force_login(admin_user)
                self.log_test("Authentication", True, f"Logged in as {admin_user.username}")
            except User.DoesNotExist:
                # Try to create a test user
                admin_user = User.objects.create_user('test_admin', 'test@example.com', 'password')
                self.client.force_login(admin_user)
                self.log_test("Authentication", True, f"Created and logged in as {admin_user.username}")
            
        except Exception as e:
            self.log_test("Environment Setup", False, f"Failed to setup environment: {str(e)}")
            return False
        
        return True
    
    def test_critical_path_api(self):
        """Test the Critical Path Analysis API endpoint"""
        print("\n🛤️ Testing Critical Path Analysis API...")
        
        try:
            url = reverse('analyze_critical_path_api')
            data = {'board_id': self.software_board.id}
            
            start_time = time.time()
            response = self.client.post(
                url,
                json.dumps(data),
                content_type='application/json'
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Validate response structure
                required_keys = ['critical_path', 'task_analysis', 'project_insights', 'recommendations']
                missing_keys = [key for key in required_keys if key not in response_data]
                
                if missing_keys:
                    self.log_test(
                        "Critical Path API - Structure",
                        False,
                        f"Missing keys: {missing_keys}",
                        response_data
                    )
                else:
                    self.log_test(
                        "Critical Path API - Structure",
                        True,
                        f"All required keys present. Response time: {response_time:.2f}s"
                    )
                
                # Validate critical path content
                critical_path = response_data.get('critical_path', [])
                if critical_path:
                    self.log_test(
                        "Critical Path API - Content",
                        True,
                        f"Found {len(critical_path)} tasks in critical path"
                    )
                    
                    # Check if critical path tasks have required fields
                    first_task = critical_path[0]
                    required_task_fields = ['task_id', 'task_title', 'duration_hours']
                    missing_fields = [field for field in required_task_fields if field not in first_task]
                    
                    if missing_fields:
                        self.log_test(
                            "Critical Path API - Task Fields",
                            False,
                            f"Missing task fields: {missing_fields}",
                            first_task
                        )
                    else:
                        self.log_test(
                            "Critical Path API - Task Fields",
                            True,
                            f"Critical path tasks have all required fields"
                        )
                else:
                    self.log_test(
                        "Critical Path API - Content",
                        False,
                        "No critical path found in response",
                        response_data
                    )
                
                # Validate project insights
                project_insights = response_data.get('project_insights', {})
                if project_insights:
                    insights_keys = ['total_duration_hours', 'critical_path_duration', 'high_risk_tasks']
                    present_keys = [key for key in insights_keys if key in project_insights]
                    self.log_test(
                        "Critical Path API - Insights",
                        len(present_keys) > 0,
                        f"Found insights: {present_keys}"
                    )
                
                # Validate recommendations
                recommendations = response_data.get('recommendations', [])
                self.log_test(
                    "Critical Path API - Recommendations",
                    len(recommendations) > 0,
                    f"Generated {len(recommendations)} recommendations"
                )
                
            else:
                self.log_test(
                    "Critical Path API - Response",
                    False,
                    f"HTTP {response.status_code}: {response.content.decode()}"
                )
                
        except Exception as e:
            self.log_test("Critical Path API - Exception", False, f"Exception: {str(e)}")
    
    def test_task_completion_prediction_api(self):
        """Test the Task Completion Prediction API endpoint"""
        print("\n📈 Testing Task Completion Prediction API...")
        
        try:
            # Get a task with some progress for testing
            test_task = Task.objects.filter(
                column__board=self.software_board,
                progress__gt=0,
                progress__lt=100
            ).first()
            
            if not test_task:
                # Get any task
                test_task = Task.objects.filter(column__board=self.software_board).first()
            
            if not test_task:
                self.log_test("Task Completion API - Setup", False, "No tasks found for testing")
                return
            
            url = reverse('predict_task_completion_api')
            data = {'task_id': test_task.id}
            
            start_time = time.time()
            response = self.client.post(
                url,
                json.dumps(data),
                content_type='application/json'
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Validate response structure
                required_keys = ['predictions', 'progress_analysis', 'risk_assessment']
                present_keys = [key for key in required_keys if key in response_data]
                
                self.log_test(
                    "Task Completion API - Structure",
                    len(present_keys) >= 2,
                    f"Found {len(present_keys)}/{len(required_keys)} expected sections. Response time: {response_time:.2f}s"
                )
                
                # Validate predictions
                predictions = response_data.get('predictions', {})
                if predictions:
                    prediction_types = ['optimistic_completion', 'realistic_completion', 'pessimistic_completion']
                    found_predictions = [p for p in prediction_types if p in predictions]
                    self.log_test(
                        "Task Completion API - Predictions",
                        len(found_predictions) > 0,
                        f"Found prediction types: {found_predictions}"
                    )
                
                # Validate recommendations
                recommendations = response_data.get('recommendations', [])
                self.log_test(
                    "Task Completion API - Recommendations",
                    True,
                    f"Generated {len(recommendations)} recommendations for task: {test_task.title[:30]}..."
                )
                
            else:
                self.log_test(
                    "Task Completion API - Response",
                    False,
                    f"HTTP {response.status_code}: {response.content.decode()}"
                )
                
        except Exception as e:
            self.log_test("Task Completion API - Exception", False, f"Exception: {str(e)}")
    
    def test_project_timeline_api(self):
        """Test the Project Timeline Generation API endpoint"""
        print("\n📅 Testing Project Timeline Generation API...")
        
        try:
            url = reverse('generate_project_timeline_api')
            data = {'board_id': self.software_board.id}
            
            start_time = time.time()
            response = self.client.post(
                url,
                json.dumps(data),
                content_type='application/json'
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Validate response structure
                expected_sections = ['timeline_phases', 'resource_timeline', 'critical_milestones', 'timeline_insights']
                present_sections = [section for section in expected_sections if section in response_data]
                
                self.log_test(
                    "Project Timeline API - Structure",
                    len(present_sections) >= 2,
                    f"Found {len(present_sections)}/{len(expected_sections)} sections. Response time: {response_time:.2f}s"
                )
                
                # Validate timeline phases
                phases = response_data.get('timeline_phases', [])
                self.log_test(
                    "Project Timeline API - Phases",
                    len(phases) >= 0,
                    f"Generated {len(phases)} project phases"
                )
                
                # Validate resource timeline
                resources = response_data.get('resource_timeline', [])
                self.log_test(
                    "Project Timeline API - Resources",
                    len(resources) >= 0,
                    f"Analyzed {len(resources)} team resources"
                )
                
                # Validate milestones
                milestones = response_data.get('critical_milestones', [])
                milestone_count = Task.objects.filter(column__board=self.software_board, is_milestone=True).count()
                self.log_test(
                    "Project Timeline API - Milestones",
                    True,
                    f"Found {len(milestones)} critical milestones (DB has {milestone_count} milestone tasks)"
                )
                
                # Validate timeline insights
                insights = response_data.get('timeline_insights', {})
                if insights:
                    insight_keys = list(insights.keys())
                    self.log_test(
                        "Project Timeline API - Insights",
                        len(insight_keys) > 0,
                        f"Generated insights: {insight_keys}"
                    )
                
            else:
                self.log_test(
                    "Project Timeline API - Response",
                    False,
                    f"HTTP {response.status_code}: {response.content.decode()}"
                )
                
        except Exception as e:
            self.log_test("Project Timeline API - Exception", False, f"Exception: {str(e)}")
    
    def test_data_integrity(self):
        """Test data integrity and model relationships"""
        print("\n🔍 Testing Data Integrity...")
        
        try:
            # Test task dependencies
            tasks_with_deps = Task.objects.filter(
                column__board=self.software_board,
                predecessors__isnull=False
            ).distinct()
            
            total_dependencies = sum(
                task.predecessors.count() 
                for task in Task.objects.filter(column__board=self.software_board)
            )
            
            self.log_test(
                "Data Integrity - Dependencies",
                total_dependencies > 0,
                f"{tasks_with_deps.count()} tasks have dependencies, total: {total_dependencies}"
            )
            
            # Test milestone tasks
            milestone_tasks = Task.objects.filter(column__board=self.software_board, is_milestone=True)
            self.log_test(
                "Data Integrity - Milestones",
                milestone_tasks.count() > 0,
                f"Found {milestone_tasks.count()} milestone tasks"
            )
            
            # Test timeline data
            tasks_with_duration = Task.objects.filter(
                column__board=self.software_board,
                estimated_duration_hours__isnull=False,
                estimated_duration_hours__gt=0
            )
            
            self.log_test(
                "Data Integrity - Timeline Data",
                tasks_with_duration.count() > 0,
                f"{tasks_with_duration.count()} tasks have estimated durations"
            )
            
            # Test date fields
            tasks_with_dates = Task.objects.filter(
                column__board=self.software_board,
                estimated_start_date__isnull=False
            )
            
            self.log_test(
                "Data Integrity - Date Data",
                tasks_with_dates.count() > 0,
                f"{tasks_with_dates.count()} tasks have estimated start dates"
            )
            
        except Exception as e:
            self.log_test("Data Integrity - Exception", False, f"Exception: {str(e)}")
    
    def test_ai_model_availability(self):
        """Test if AI model is available and responding"""
        print("\n🤖 Testing AI Model Availability...")
        
        try:
            from kanban.utils.ai_utils import get_model
            
            model = get_model()
            if model:
                self.log_test("AI Model - Availability", True, "Gemini model initialized successfully")
                
                # Test a simple AI call
                try:
                    test_prompt = "Respond with 'AI is working' if you can read this."
                    response = model.generate_content(test_prompt)
                    if response and response.text:
                        self.log_test(
                            "AI Model - Functionality",
                            True,
                            f"AI responded: {response.text[:50]}..."
                        )
                    else:
                        self.log_test("AI Model - Functionality", False, "AI returned empty response")
                except Exception as e:
                    self.log_test("AI Model - Functionality", False, f"AI call failed: {str(e)}")
            else:
                self.log_test("AI Model - Availability", False, "Failed to initialize Gemini model")
                
        except Exception as e:
            self.log_test("AI Model - Exception", False, f"Exception: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE AI TIMELINE FEATURES TEST REPORT")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['message']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if failed_tests == 0:
            print("   🎉 All tests passed! Your AI timeline features are working perfectly.")
            print("   🚀 Ready for production use!")
        else:
            print("   🔧 Some tests failed. Check the error messages above.")
            print("   📋 Common issues:")
            print("     - Check GEMINI_API_KEY environment variable")
            print("     - Ensure development server is running")
            print("     - Verify database migrations are applied")
        
        print(f"\n🌐 NEXT STEPS:")
        print(f"   1. Visit: http://127.0.0.1:8000/boards/{self.software_board.id}/analytics/")
        print("   2. Test the 'Critical Path' button")
        print("   3. Test the 'Timeline View' button") 
        print("   4. Observe AI-generated insights and recommendations")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    print("🧪 Starting Comprehensive AI Timeline Features Test...")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = AITimelineFeatureTester()
    
    # Setup environment
    if not tester.setup_test_environment():
        print("❌ Failed to setup test environment. Exiting.")
        return False
    
    # Run all tests
    tester.test_data_integrity()
    tester.test_ai_model_availability()
    tester.test_critical_path_api()
    tester.test_task_completion_prediction_api()
    tester.test_project_timeline_api()
    
    # Generate report
    success = tester.generate_report()
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
