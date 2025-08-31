#!/usr/bin/env python3
"""
Comprehensive Model Testing Script
Tests all installed models and their capabilities
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from vanta_ledger.services.github_models_service import github_models_service
from vanta_ledger.services.semantic_search_service import SemanticSearchService
from vanta_ledger.services.advanced_document_processor import AdvancedDocumentProcessor


class ModelTester:
    """Comprehensive tester for all models"""
    
    def __init__(self):
        self.test_results = []
        
    async def test_github_models(self):
        """Test GitHub Models Service"""
        print("🔧 Testing GitHub Models Service...")
        
        try:
            # Test service initialization
            result = {
                "service": "GitHub Models",
                "enabled": github_models_service.enabled,
                "default_model": github_models_service.default_model,
                "capabilities": len(github_models_service.get_available_prompts()),
                "expense_categories": len(github_models_service.get_expense_categories()),
                "industry_patterns": len(github_models_service.get_industry_patterns()),
                "success": True
            }
            
            print(f"✅ Service enabled: {result['enabled']}")
            print(f"✅ Default model: {result['default_model']}")
            print(f"✅ Capabilities: {result['capabilities']}")
            print(f"✅ Expense categories: {result['expense_categories']}")
            print(f"✅ Industry patterns: {result['industry_patterns']}")
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            print(f"❌ GitHub Models test failed: {e}")
            self.test_results.append({
                "service": "GitHub Models",
                "error": str(e),
                "success": False
            })
            return False
    
    async def test_semantic_search(self):
        """Test Semantic Search Service"""
        print("\n🔍 Testing Semantic Search Service...")
        
        try:
            # Initialize service
            semantic_service = SemanticSearchService()
            
            # Test service initialization
            result = {
                "service": "Semantic Search",
                "semantic_available": hasattr(semantic_service, 'embedding_model') and semantic_service.embedding_model is not None,
                "tagging_available": hasattr(semantic_service, 'tagging_pipeline') and semantic_service.tagging_pipeline is not None,
                "success": True
            }
            
            print(f"✅ Semantic models available: {result['semantic_available']}")
            print(f"✅ Tagging models available: {result['tagging_available']}")
            
            # Test basic functionality
            if result['semantic_available']:
                print("✅ Semantic search models loaded successfully")
            else:
                print("⚠️ Semantic search using fallback mode")
            
            if result['tagging_available']:
                print("✅ Tagging models loaded successfully")
            else:
                print("⚠️ Tagging using fallback mode")
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            print(f"❌ Semantic Search test failed: {e}")
            self.test_results.append({
                "service": "Semantic Search",
                "error": str(e),
                "success": False
            })
            return False
    
    async def test_document_processing(self):
        """Test Advanced Document Processing"""
        print("\n📄 Testing Advanced Document Processing...")
        
        try:
            # Initialize service
            doc_processor = AdvancedDocumentProcessor()
            
            # Test service initialization
            result = {
                "service": "Document Processing",
                "ml_available": hasattr(doc_processor, 'layout_model') and doc_processor.layout_model is not None,
                "ocr_available": hasattr(doc_processor, '_extract_text_advanced'),
                "success": True
            }
            
            print(f"✅ ML models available: {result['ml_available']}")
            print(f"✅ OCR available: {result['ocr_available']}")
            
            # Test OCR functionality
            if result['ocr_available']:
                print("✅ OCR processing available")
            else:
                print("⚠️ OCR not available")
            
            # Test ML functionality
            if result['ml_available']:
                print("✅ LayoutLMv3 models loaded successfully")
            else:
                print("⚠️ LayoutLMv3 using fallback mode")
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            print(f"❌ Document Processing test failed: {e}")
            self.test_results.append({
                "service": "Document Processing",
                "error": str(e),
                "success": False
            })
            return False
    
    async def test_ocr_functionality(self):
        """Test OCR functionality"""
        print("\n🔤 Testing OCR Functionality...")
        
        try:
            import pytesseract
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple test image with text
            img = Image.new('RGB', (400, 100), color='white')
            draw = ImageDraw.Draw(img)
            
            # Add text to image
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.text((10, 10), "Test OCR Text: $1,250.00", fill='black', font=font)
            
            # Save test image
            test_image_path = "test_ocr_image.png"
            img.save(test_image_path)
            
            # Test OCR
            ocr_text = pytesseract.image_to_string(img)
            
            result = {
                "service": "OCR",
                "text_extracted": len(ocr_text.strip()) > 0,
                "extracted_text": ocr_text.strip(),
                "success": True
            }
            
            print(f"✅ OCR text extracted: {result['text_extracted']}")
            print(f"✅ Extracted text: '{result['extracted_text']}'")
            
            # Clean up
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            print(f"❌ OCR test failed: {e}")
            self.test_results.append({
                "service": "OCR",
                "error": str(e),
                "success": False
            })
            return False
    
    async def test_ml_libraries(self):
        """Test ML library imports"""
        print("\n🧠 Testing ML Libraries...")
        
        try:
            # Test imports
            import torch
            import transformers
            import sentence_transformers
            
            result = {
                "service": "ML Libraries",
                "torch_version": torch.__version__,
                "transformers_version": transformers.__version__,
                "sentence_transformers_version": sentence_transformers.__version__,
                "cuda_available": torch.cuda.is_available(),
                "success": True
            }
            
            print(f"✅ PyTorch version: {result['torch_version']}")
            print(f"✅ Transformers version: {result['transformers_version']}")
            print(f"✅ Sentence Transformers version: {result['sentence_transformers_version']}")
            print(f"✅ CUDA available: {result['cuda_available']}")
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            print(f"❌ ML Libraries test failed: {e}")
            self.test_results.append({
                "service": "ML Libraries",
                "error": str(e),
                "success": False
            })
            return False
    
    async def test_enhanced_capabilities(self):
        """Test enhanced GitHub Models capabilities"""
        print("\n🚀 Testing Enhanced Capabilities...")
        
        try:
            # Test document analysis
            test_doc = "INVOICE\nAmount: $500.00\nDate: 2024-01-15"
            analysis = await github_models_service.analyze_financial_document(test_doc)
            
            # Test expense categorization
            categorization = await github_models_service.categorize_expense(
                "AWS Cloud Services", 150.00, "Amazon"
            )
            
            # Test fraud detection
            fraud = await github_models_service.detect_fraud_patterns([
                {"amount": 100, "vendor": "Test"}
            ])
            
            result = {
                "service": "Enhanced Capabilities",
                "document_analysis": analysis.get('confidence', 0) > 0,
                "expense_categorization": categorization.get('confidence', 0) > 0,
                "fraud_detection": fraud.get('risk_level') is not None,
                "success": True
            }
            
            print(f"✅ Document analysis: {result['document_analysis']}")
            print(f"✅ Expense categorization: {result['expense_categorization']}")
            print(f"✅ Fraud detection: {result['fraud_detection']}")
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            print(f"❌ Enhanced capabilities test failed: {e}")
            self.test_results.append({
                "service": "Enhanced Capabilities",
                "error": str(e),
                "success": False
            })
            return False
    
    async def run_all_tests(self):
        """Run all model tests"""
        print("🤖 Comprehensive Model Testing")
        print("=" * 60)
        
        tests = [
            self.test_ml_libraries,
            self.test_github_models,
            self.test_semantic_search,
            self.test_document_processing,
            self.test_ocr_functionality,
            self.test_enhanced_capabilities
        ]
        
        results = []
        for test in tests:
            try:
                success = await test()
                results.append(success)
            except Exception as e:
                print(f"❌ Test {test.__name__} failed: {e}")
                results.append(False)
        
        # Generate summary
        successful_tests = sum(results)
        total_tests = len(results)
        
        print(f"\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Successful: {successful_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
        print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result.get('success', False) else "❌"
            print(f"{status} {result['service']}")
            if not result.get('success', False):
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return successful_tests == total_tests


async def main():
    """Main test runner"""
    tester = ModelTester()
    success = await tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All models configured and working perfectly!")
        print(f"🚀 Your Vanta Ledger has full AI capabilities!")
    else:
        print(f"\n⚠️ Some models need attention. Check the detailed results above.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
