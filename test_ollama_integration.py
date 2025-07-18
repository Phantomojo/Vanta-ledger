#!/usr/bin/env python3
"""
Test Ollama Integration for Vanta Ledger
========================================

Simple test script to verify Ollama and Llama2 are working with the document AI system.
"""

import requests
import json
from typing import List

class OllamaTester:
    """Test Ollama integration"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def test_connection(self) -> bool:
        """Test if Ollama is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama is running and accessible")
                return True
            else:
                print(f"❌ Ollama returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            return False
    
    def get_models(self) -> List[str]:
        """Get available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                print(f"📋 Available models: {models}")
                return models
            else:
                print(f"❌ Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return []
    
    def test_model(self, model_name: str) -> bool:
        """Test if a specific model is available"""
        try:
            payload = {
                "model": model_name,
                "prompt": "Hello, this is a test. Please respond with 'Test successful' if you can read this.",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 50
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"✅ Model '{model_name}' is working")
                print(f"   Response: {response_text[:100]}...")
                return True
            else:
                print(f"❌ Model '{model_name}' test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing model '{model_name}': {e}")
            return False
    
    def test_document_analysis(self, model_name: str) -> bool:
        """Test document analysis with LLM"""
        sample_document = """
        INVOICE
        
        Invoice Number: INV-2024-001
        Date: 2024-01-15
        Due Date: 2024-02-15
        
        CABERA ENTERPRISES
        123 Construction Street
        Nairobi, Kenya
        
        Bill To:
        Vanta Construction Ltd
        Project: Road Construction Phase 2
        
        Description:
        - Excavation work: KES 250,000
        - Material supply: KES 150,000
        - Equipment rental: KES 75,000
        
        Subtotal: KES 475,000
        VAT (16%): KES 76,000
        Total: KES 551,000
        
        Payment Terms: Net 30 days
        """
        
        prompt = f"""You are an expert business analyst. Analyze this construction invoice and provide insights.

Document Content:
{sample_document}

Please provide a brief analysis in JSON format:
{{
    "summary": "brief summary",
    "key_points": ["point1", "point2"],
    "business_insights": ["insight1"],
    "risk_assessment": "low/medium/high with reason"
}}"""
        
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"✅ Document analysis test successful with '{model_name}'")
                print(f"   Response: {response_text[:200]}...")
                
                # Try to parse JSON
                try:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        print(f"   ✅ JSON parsing successful")
                        print(f"   Summary: {parsed.get('summary', 'N/A')}")
                    else:
                        print(f"   ⚠️ JSON parsing failed, but response received")
                except:
                    print(f"   ⚠️ JSON parsing failed, but response received")
                
                return True
            else:
                print(f"❌ Document analysis test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in document analysis test: {e}")
            return False

def main():
    """Main test function"""
    print("🧪 Testing Ollama Integration for Vanta Ledger")
    print("=" * 50)
    
    tester = OllamaTester()
    
    # Test connection
    if not tester.test_connection():
        print("\n❌ Ollama is not running or not accessible")
        print("Please start Ollama with: ollama serve")
        return
    
    # Get available models
    models = tester.get_models()
    if not models:
        print("\n❌ No models found")
        print("Please install a model with: ollama pull llama2")
        return
    
    # Test llama2 model specifically
    if 'llama2' in models:
        print(f"\n🔍 Testing llama2 model...")
        if tester.test_model('llama2'):
            print(f"\n📄 Testing document analysis with llama2...")
            tester.test_document_analysis('llama2')
    else:
        print(f"\n⚠️ llama2 model not found, testing first available model...")
        if models:
            first_model = models[0]
            if tester.test_model(first_model):
                print(f"\n📄 Testing document analysis with {first_model}...")
                tester.test_document_analysis(first_model)
    
    print(f"\n🎉 Ollama integration test complete!")
    print(f"\nNext steps:")
    print(f"1. Run: python llm_enhanced_ai.py")
    print(f"2. Monitor the enhanced analysis with LLM capabilities")

if __name__ == "__main__":
    main() 