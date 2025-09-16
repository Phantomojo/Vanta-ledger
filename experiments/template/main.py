#!/usr/bin/env python3
"""
Experiment Template
Description: Template for creating new experiments
Author: Your Name
Date: 2024-08-31
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add the main project to the path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend" / "src"))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_experiment() -> Dict[str, Any]:
    """Set up the experiment environment"""
    logger.info("Setting up experiment environment...")
    
    # Check if we can import Vanta Ledger modules
    try:
        from vanta_ledger.services.github_models_service import GitHubModelsService
        logger.info("✅ Successfully imported Vanta Ledger modules")
    except ImportError as e:
        logger.error(f"❌ Failed to import Vanta Ledger modules: {e}")
        return {"success": False, "error": str(e)}
    
    return {"success": True}

def run_experiment() -> Dict[str, Any]:
    """Run the main experiment"""
    logger.info("🧪 Starting experiment...")
    
    # Set up the experiment
    setup_result = setup_experiment()
    if not setup_result["success"]:
        return setup_result
    
    try:
        # Your experiment code goes here
        logger.info("Running experiment logic...")
        
        # Example: Test GitHub Models service
        from vanta_ledger.services.github_models_service import GitHubModelsService
        
        service = GitHubModelsService()
        
        # Test document analysis
        result = service.analyze_financial_document(
            document_text="Sample invoice for $1000 from ABC Company",
            document_type="invoice",
            company_id="test-company-123"
        )
        
        logger.info(f"✅ Experiment completed successfully!")
        logger.info(f"📊 Results: {result}")
        
        return {
            "success": True,
            "results": result,
            "message": "Experiment completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Experiment failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Experiment failed"
        }

def cleanup_experiment():
    """Clean up after the experiment"""
    logger.info("🧹 Cleaning up experiment...")
    # Add any cleanup code here
    logger.info("✅ Cleanup completed")

def main():
    """Main experiment function"""
    print("🧪 Vanta Ledger Experiment Template")
    print("=" * 50)
    
    # Run the experiment
    result = run_experiment()
    
    # Clean up
    cleanup_experiment()
    
    # Report results
    if result["success"]:
        print(f"🎉 Experiment completed successfully!")
        print(f"📊 Results: {result.get('results', 'No results')}")
    else:
        print(f"❌ Experiment failed: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    main()
