#!/usr/bin/env python3
"""
Simple test script to connect to Paperless-ngx
"""

import requests
import json

def test_connection():
    """Test connection to Paperless-ngx"""
    
    # Paperless-ngx credentials
    username = "Mike"
    password = "106730!@#"  # Your password with special characters
    
    # API endpoints
    base_url = "http://localhost:8000"
    auth_url = f"{base_url}/api/token/"
    docs_url = f"{base_url}/api/documents/"
    
    print("🔐 Testing Paperless-ngx Connection...")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    try:
        # Step 1: Get authentication token
        print("1. Getting authentication token...")
        auth_data = {
            'username': username,
            'password': password
        }
        
        response = requests.post(auth_url, data=auth_data)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Authentication successful!")
            print(f"   Response: {response.text[:100]}...")
            
            try:
                token_data = response.json()
                access_token = token_data.get('token') or token_data.get('access')
                if access_token:
                    print(f"   Token: {access_token[:20]}...")
                else:
                    print(f"   ⚠️  No token in response")
                    print(f"   Full response: {response.text}")
                    return False
            except Exception as e:
                print(f"   ⚠️  Could not parse JSON response: {e}")
                print(f"   Raw response: {response.text}")
                return False
            
            # Step 2: Get documents
            print("\n2. Getting documents...")
            headers = {
                'Authorization': f'Token {access_token}'
            }
            
            print(f"   Using headers: {headers}")
            docs_response = requests.get(docs_url, headers=headers)
            print(f"   Status Code: {docs_response.status_code}")
            
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
                total_docs = docs_data.get('count', 0)
                print(f"   ✅ Documents retrieved successfully!")
                print(f"   Total Documents: {total_docs}")
                
                # Show first few documents
                results = docs_data.get('results', [])
                print(f"\n3. Sample Documents:")
                for i, doc in enumerate(results[:5]):
                    print(f"   {i+1}. {doc.get('title', 'No title')} (ID: {doc.get('id')})")
                
                return True
            else:
                print(f"   ❌ Failed to get documents: {docs_response.text}")
                return False
        else:
            print(f"   ❌ Authentication failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 Connection test successful! Ready to import documents.")
    else:
        print("\n❌ Connection test failed. Please check your credentials and Paperless-ngx status.") 