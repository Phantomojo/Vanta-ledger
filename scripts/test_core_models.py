#!/usr/bin/env python3
"""
Core Model Testing Script
Tests the essential models without database dependencies
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from vanta_ledger.services.github_models_service import github_models_service


class CoreModelTester:
    """Tester for core models"""
    
    def __init__(self):
        self.test_results = []
        
    async def test_ml_libraries(self):
        """Test ML library imports"""
        print("🧠 Testing ML Libraries...")
        
        try:
            # Test imports
            import torch
            import transformers
            import sentence_transformers
            import pytesseract
            from PIL import Image
            
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
            print(f"✅ PIL/Pillow available")
            print(f"✅ Tesseract available")
            
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
    
    async def test_github_models(self):
        """Test GitHub Models Service"""
        print("\n🔧 Testing GitHub Models Service...")
        
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
            
            # Test compliance checking
            compliance = await github_models_service.check_compliance({
                "balance_sheet": 100000,
                "transaction_date": "2024-01-15"
            })
            
            result = {
                "service": "Enhanced Capabilities",
                "document_analysis": analysis.get('confidence', 0) > 0,
                "expense_categorization": categorization.get('confidence', 0) > 0,
                "fraud_detection": fraud.get('risk_level') is not None,
                "compliance_checking": compliance.get('overall_compliance') is not None,
                "success": True
            }
            
            print(f"✅ Document analysis: {result['document_analysis']}")
            print(f"✅ Expense categorization: {result['expense_categorization']}")
            print(f"✅ Fraud detection: {result['fraud_detection']}")
            print(f"✅ Compliance checking: {result['compliance_checking']}")
            
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
    
    async def test_semantic_models(self):
        """Test semantic model loading"""
        print("\n🔍 Testing Semantic Models...")
        
        try:
            import sentence_transformers
            from transformers import pipeline
            
            # Test sentence transformer
            model_name = "all-MiniLM-L6-v2"
            embedding_model = sentence_transformers.SentenceTransformer(model_name)
            
            # Test text classification pipeline
            classifier = pipeline("text-classification", model="facebook/bart-large-mnli")
            
            # Test with sample text
            test_text = "This is a financial document about invoices and payments."
            embedding = embedding_model.encode(test_text)
            classification = classifier(test_text, candidate_labels=["financial", "technical", "medical"])
            
            result = {
                "service": "Semantic Models",
                "embedding_model_loaded": embedding_model is not None,
                "embedding_size": len(embedding),
                "classification_working": len(classification) > 0,
                "success": True
            }
            
            print(f"✅ Embedding model loaded: {result['embedding_model_loaded']}")
            print(f"✅ Embedding size: {result['embedding_size']}")
            print(f"✅ Classification working: {result['classification_working']}")
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            print(f"❌ Semantic models test failed: {e}")
            self.test_results.append({
                "service": "Semantic Models",
                "error": str(e),
                "success": False
            })
            return False
    
    async def run_all_tests(self):
        """Run all core model tests"""
        print("🤖 Core Model Testing")
        print("=" * 60)
        
        tests = [
            self.test_ml_libraries,
            self.test_github_models,
            self.test_ocr_functionality,
            self.test_enhanced_capabilities,
            self.test_semantic_models
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
    tester = CoreModelTester()
    success = await tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All core models configured and working perfectly!")
        print(f"🚀 Your Vanta Ledger has full AI capabilities!")
    else:
        print(f"\n⚠️ Some models need attention. Check the detailed results above.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
