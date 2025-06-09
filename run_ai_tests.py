#!/usr/bin/env python
"""
Test runner for AI features in TaskFlow

This script runs the test cases specifically for the AI features.
It is useful for quick testing of just the AI functionality without
running the entire test suite.

Usage:
    python run_ai_tests.py
"""

import os
import sys
import django
from django.test.runner import DiscoverRunner

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

# Custom test runner that only runs AI feature tests
class AITestRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = ['kanban.tests_ai_features']
        return super().build_suite(test_labels, extra_tests, **kwargs)

if __name__ == "__main__":
    print("\n🤖 Running AI Feature Tests for TaskFlow 🤖\n")
    
    # Run the tests
    test_runner = AITestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(['kanban.tests_ai_features'])
    
    # Exit with appropriate status code
    sys.exit(bool(failures))
