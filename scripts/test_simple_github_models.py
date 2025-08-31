#!/usr/bin/env python3
"""
Simple GitHub Models API Test
"""

import os
import sys

def test_github_models():
    """Test GitHub Models API directly"""
    print('🧪 Testing GitHub Models API...')
    
    # Check token
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('❌ GITHUB_TOKEN not found')
        return False
    
    print(f'✅ GitHub Token: {token[:10]}...***')
    
    try:
        import openai
        print(f'✅ OpenAI version: {openai.__version__}')
        
        # Create client
        from openai import OpenAI
        client = OpenAI(
            api_key=token,
            base_url='https://models.github.ai/inference'
        )
        
        print('✅ GitHub Models client created')
        
        # Test simple completion
        print('🔬 Testing AI request...')
        response = client.chat.completions.create(
            model='openai/gpt-4o',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Say Hello from GitHub Models in exactly 5 words.'}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f'✅ AI Response: {result}')
        print('🎉 GitHub Models API is working!')
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    success = test_github_models()
    sys.exit(0 if success else 1)





