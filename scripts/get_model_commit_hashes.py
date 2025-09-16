#!/usr/bin/env python3
"""
Script to get the actual commit hashes for Hugging Face models to fix B615 security issues.

This script fetches the actual commit hashes for the models used in the codebase
so we can pin to specific commits instead of using branch names like "main".
"""

import requests
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_model_commit_hash(model_name: str) -> str:
    """Get the latest commit hash for a Hugging Face model."""
    try:
        # Use Hugging Face Hub API to get model info
        url = f"https://huggingface.co/api/models/{model_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        model_info = response.json()
        
        # Get the latest commit hash
        if 'sha' in model_info:
            return model_info['sha']
        elif 'lastModified' in model_info:
            # If no sha, try to get from the repository
            repo_url = f"https://huggingface.co/api/repos/{model_name}"
            repo_response = requests.get(repo_url, timeout=10)
            repo_response.raise_for_status()
            repo_info = repo_response.json()
            if 'sha' in repo_info:
                return repo_info['sha']
        
        logger.warning(f"Could not get commit hash for {model_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting commit hash for {model_name}: {e}")
        return None

def get_models_from_code() -> list:
    """Extract model names from the codebase."""
    models = []
    
    # Check llm_integration.py for model paths
    llm_file = Path(__file__).parent.parent / "backend/src/vanta_ledger/agents/llm_integration.py"
    if llm_file.exists():
        with open(llm_file, 'r') as f:
            content = f.read()
            # Look for model_path assignments
            lines = content.split('\n')
            for line in lines:
                if 'model_path' in line and '=' in line:
                    # Extract the model name
                    if '"' in line:
                        start = line.find('"') + 1
                        end = line.find('"', start)
                        if start > 0 and end > start:
                            model_name = line[start:end]
                            if '/' in model_name and not model_name.startswith('./'):
                                models.append(model_name)
    
    # Check advanced_document_processor.py for hardcoded models
    doc_file = Path(__file__).parent.parent / "backend/src/vanta_ledger/services/advanced_document_processor.py"
    if doc_file.exists():
        with open(doc_file, 'r') as f:
            content = f.read()
            # Look for hardcoded model names
            if 'microsoft/layoutlmv3-base' in content:
                models.append('microsoft/layoutlmv3-base')
    
    return list(set(models))  # Remove duplicates

def main():
    """Main function."""
    logger.info("Getting commit hashes for Hugging Face models...")
    
    models = get_models_from_code()
    logger.info(f"Found models: {models}")
    
    commit_hashes = {}
    
    for model in models:
        logger.info(f"Getting commit hash for {model}...")
        commit_hash = get_model_commit_hash(model)
        if commit_hash:
            commit_hashes[model] = commit_hash
            logger.info(f"✅ {model}: {commit_hash}")
        else:
            logger.warning(f"❌ Could not get commit hash for {model}")
    
    # Save results
    results_file = Path(__file__).parent.parent / "model_commit_hashes.json"
    with open(results_file, 'w') as f:
        json.dump(commit_hashes, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")
    
    # Generate replacement script
    replacement_script = Path(__file__).parent.parent / "scripts/apply_commit_hashes.py"
    with open(replacement_script, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""Script to apply commit hashes to fix B615 security issues."""\n\n')
        f.write('import json\n')
        f.write('from pathlib import Path\n\n')
        f.write('def apply_commit_hashes():\n')
        f.write('    """Apply commit hashes to model loading code."""\n')
        f.write('    with open("model_commit_hashes.json", "r") as f:\n')
        f.write('        commit_hashes = json.load(f)\n\n')
        
        for model, commit_hash in commit_hashes.items():
            f.write(f'    # Replace {model} with commit hash {commit_hash}\n')
            f.write(f'    # TODO: Update code to use revision="{commit_hash}" for {model}\n\n')
    
    logger.info(f"Replacement script created at {replacement_script}")
    
    print("\n" + "="*60)
    print("MODEL COMMIT HASHES")
    print("="*60)
    for model, commit_hash in commit_hashes.items():
        print(f"{model}: {commit_hash}")
    print("="*60)

if __name__ == "__main__":
    main()
