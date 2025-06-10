#!/usr/bin/env python
"""
Quick test script to verify AI API endpoints are working correctly
"""

import requests
import json

def test_ai_api():
    """Test the AI API endpoints directly"""
    
    base_url = "http://127.0.0.1:8000"
    
    # First, let's try to get the login page to get CSRF token
    session = requests.Session()
    
    # Get login page
    login_page = session.get(f"{base_url}/accounts/login/")
    print(f"Login page status: {login_page.status_code}")
    
    # Extract CSRF token
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    print(f"CSRF token extracted: {csrf_token[:20]}...")
      # Login as admin
    login_data = {
        'username': 'admin',
        'password': 'adminpass123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(f"{base_url}/accounts/login/", data=login_data)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response URL: {login_response.url}")
    
    if login_response.status_code == 302 or 'dashboard' in login_response.url:
        print("✅ Login successful!")
    elif login_response.status_code == 200 and 'login' not in login_response.url:
        print("✅ Login successful!")
    else:
        print("❌ Login failed!")
        print(f"Response content: {login_response.text[:500]}")
        return
    
    # Test AI API endpoint
    ai_url = f"{base_url}/api/generate-task-description/"    # Get CSRF token for API call
    dashboard_page = session.get(f"{base_url}/dashboard/")
    soup = BeautifulSoup(dashboard_page.content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        csrf_token = csrf_input['value']
    else:
        # Try to get from meta tag
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta:
            csrf_token = csrf_meta['content']
        else:
            # Use session cookies - Django should handle CSRF automatically
            csrf_token = session.cookies.get('csrftoken', 'no-csrf-token-found')
            print(f"Using CSRF token from cookies: {csrf_token[:20]}...")
    
    ai_data = {
        'title': 'Create user authentication system'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': f"{base_url}/dashboard/"
    }
    
    print(f"\nTesting AI API endpoint: {ai_url}")
    print(f"Request data: {ai_data}")
    
    ai_response = session.post(ai_url, json=ai_data, headers=headers)
    print(f"AI API response status: {ai_response.status_code}")
    print(f"AI API response headers: {dict(ai_response.headers)}")
    
    if ai_response.status_code == 200:
        print("✅ AI API endpoint is working!")
        try:
            response_data = ai_response.json()
            print(f"Response data: {response_data}")
        except:
            print(f"Response text: {ai_response.text}")
    else:
        print(f"❌ AI API failed with status {ai_response.status_code}")
        print(f"Response: {ai_response.text}")

if __name__ == "__main__":
    try:
        import requests
        from bs4 import BeautifulSoup
        test_ai_api()
    except ImportError as e:
        print(f"Missing required packages: {e}")
        print("Install with: pip install requests beautifulsoup4")
