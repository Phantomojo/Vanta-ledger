#!/usr/bin/env python3
"""
Debug script to understand Paperless-ngx API response
"""

import requests
import json

def debug_paperless():
    """Debug Paperless-ngx API response"""
    
    username = "Mike"
    password = "106730!@#"
    base_url = "http://localhost:8000"
    auth_url = f"{base_url}/api/token/"
    
    print("🔍 Debugging Paperless-ngx API...")
    print(f"URL: {auth_url}")
    print(f"Username: {username}")
    print("-" * 50)
    
    try:
        # Test authentication
        auth_data = {
            'username': username,
            'password': password
        }
        
        print("1. Sending authentication request...")
        response = requests.post(auth_url, data=auth_data)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"   Response Length: {len(response.text)}")
        print(f"   Raw Response: {repr(response.text)}")
        
        if response.status_code == 200:
            print("\n2. Trying to parse JSON...")
            try:
                data = response.json()
                print(f"   Parsed JSON: {json.dumps(data, indent=2)}")
                
                # Check for different possible token field names
                possible_token_fields = ['access', 'token', 'access_token', 'auth_token']
                token_found = False
                
                for field in possible_token_fields:
                    if field in data:
                        print(f"   ✅ Found token in field '{field}': {data[field][:20]}...")
                        token_found = True
                        break
                
                if not token_found:
                    print(f"   ⚠️  No token field found. Available fields: {list(data.keys())}")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
                print(f"   Response is not valid JSON")
        
        # Test documents endpoint directly
        print("\n3. Testing documents endpoint...")
        docs_url = f"{base_url}/api/documents/"
        docs_response = requests.get(docs_url)
        print(f"   Status Code: {docs_response.status_code}")
        print(f"   Response: {docs_response.text[:200]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_paperless() 