# 🧪 Experiments Directory

Welcome to the **Experiments** directory! This is your safe space for testing new ideas, features, and concepts related to Vanta Ledger.

## 🎯 **Purpose**

This directory is designed for:
- **Testing new features** before they go to production
- **Prototyping AI models** and integrations
- **Experimenting with new technologies**
- **Learning and educational purposes**
- **Community contributions** and ideas

## 🛡️ **Safety Guidelines**

### **✅ What You CAN Do**
- Create new experiment directories
- Test new features and ideas
- Share your experiments with the community
- Use the Vanta Ledger API for testing
- Create educational content and tutorials

### **❌ What You CANNOT Do**
- Modify the main codebase directly
- Commit secrets or credentials
- Upload malicious code
- Violate security best practices
- Affect production systems

## 📁 **Directory Structure**

```
experiments/
├── README.md                    # This file
├── template/                    # Experiment template
│   ├── README.md               # Experiment description
│   ├── main.py                 # Main experiment code
│   ├── requirements.txt        # Dependencies
│   └── tests/                  # Experiment tests
├── your-experiment/            # Your experiment here
└── community/                  # Community experiments
```

## 🚀 **Getting Started**

### **1. Create Your Experiment**
```bash
# Copy the template
cp -r experiments/template experiments/my-awesome-experiment

# Navigate to your experiment
cd experiments/my-awesome-experiment

# Customize the files
# - Update README.md with your experiment description
# - Modify main.py with your code
# - Update requirements.txt with your dependencies
```

### **2. Experiment Template Structure**
```python
# main.py
"""
My Awesome Experiment
Description: What this experiment does
Author: Your Name
Date: 2024-08-31
"""

import os
import sys
from pathlib import Path

# Add the main project to the path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend" / "src"))

from vanta_ledger.services.github_models_service import GitHubModelsService

def run_experiment():
    """Run the experiment"""
    print("🧪 Running My Awesome Experiment...")
    
    # Your experiment code here
    try:
        # Example: Test GitHub Models service
        service = GitHubModelsService()
        result = service.analyze_financial_document(
            document_text="Sample invoice for $1000",
            document_type="invoice",
            company_id="test-company"
        )
        print(f"✅ Experiment result: {result}")
        
    except Exception as e:
        print(f"❌ Experiment failed: {e}")
    
    print("🎉 Experiment completed!")

if __name__ == "__main__":
    run_experiment()
```

### **3. Requirements File**
```txt
# requirements.txt
# Add your experiment-specific dependencies here
# The main project dependencies are already available

# Example:
# requests>=2.31.0
# pandas>=2.0.0
# matplotlib>=3.7.0
```

### **4. README Template**
```markdown
# My Awesome Experiment

## Description
Brief description of what this experiment does.

## Purpose
Why this experiment was created and what it aims to achieve.

## Setup
How to set up and run this experiment.

## Results
What the experiment discovered or demonstrated.

## Files
- `main.py`: Main experiment code
- `requirements.txt`: Dependencies
- `tests/`: Test files

## Author
Your Name - Date
```

## 🔒 **Security Best Practices**

### **1. Environment Variables**
```python
# ✅ Good: Use environment variables
import os
api_key = os.getenv("EXPERIMENT_API_KEY")

# ❌ Bad: Hardcoded secrets
api_key = "your-secret-key-here"
```

### **2. Input Validation**
```python
# ✅ Good: Validate inputs
def process_data(data: str) -> str:
    if not data or len(data) > 1000:
        raise ValueError("Invalid input")
    return data.strip()

# ❌ Bad: No validation
def process_data(data: str) -> str:
    return data  # Dangerous!
```

### **3. Error Handling**
```python
# ✅ Good: Proper error handling
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return None
```

## 🧪 **Running Experiments**

### **1. Local Development**
```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install experiment dependencies
pip install -r experiments/my-experiment/requirements.txt

# Run the experiment
python experiments/my-experiment/main.py
```

### **2. Testing**
```bash
# Run experiment tests
pytest experiments/my-experiment/tests/

# Run security scan on experiment
bandit -r experiments/my-experiment/
```

## 📊 **Sharing Your Experiments**

### **1. Documentation**
- Write clear README files
- Include setup instructions
- Document your findings
- Add code comments

### **2. Testing**
- Write tests for your experiments
- Ensure they don't break the main codebase
- Follow security best practices

### **3. Contributing**
- Submit pull requests for your experiments
- Share your findings with the community
- Help others learn from your work

## 🎯 **Experiment Ideas**

### **AI/ML Experiments**
- Test new AI models with Vanta Ledger
- Experiment with different prompt strategies
- Try new document processing techniques
- Test performance optimizations

### **Integration Experiments**
- Test new API integrations
- Experiment with different databases
- Try new authentication methods
- Test scalability improvements

### **Feature Experiments**
- Prototype new features
- Test user interface improvements
- Experiment with new workflows
- Test accessibility features

## 🔍 **Monitoring and Logging**

### **1. Logging**
```python
import logging

# Set up logging for your experiment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use logging in your experiment
logger.info("Starting experiment...")
logger.error("Something went wrong: %s", error)
```

### **2. Metrics**
```python
import time
from datetime import datetime

# Track experiment performance
start_time = time.time()
# ... your experiment code ...
end_time = time.time()

print(f"Experiment took {end_time - start_time:.2f} seconds")
```

## 🎉 **Community Guidelines**

### **1. Be Respectful**
- Respect other contributors
- Provide constructive feedback
- Help others learn

### **2. Be Safe**
- Follow security guidelines
- Test your experiments thoroughly
- Don't expose sensitive information

### **3. Be Helpful**
- Share your knowledge
- Document your work
- Help others with their experiments

## 📚 **Resources**

### **1. Documentation**
- [Vanta Ledger API Documentation](docs/API.md)
- [Security Guidelines](docs/SECURITY.md)
- [Development Guide](docs/DEVELOPMENT.md)

### **2. Examples**
- Check the `examples/` directory for working examples
- Look at existing experiments for inspiration
- Review the main codebase for patterns

### **3. Community**
- [GitHub Issues](https://github.com/Phantomojo/Vanta-ledger/issues)
- [GitHub Discussions](https://github.com/Phantomojo/Vanta-ledger/discussions)
- [Security Policy](SECURITY.md)

---

**Happy Experimenting! 🧪✨**

Remember: This is a safe space for learning and innovation. Don't be afraid to try new things, but always follow security best practices!
