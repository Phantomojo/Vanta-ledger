# Contributing to Vanta Ledger

Thank you for your interest in contributing to Vanta Ledger! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### Reporting Bugs
- Use the [GitHub Issues](https://github.com/yourusername/vanta-ledger/issues) page
- Include detailed steps to reproduce the bug
- Provide system information and error logs
- Use the bug report template

### Suggesting Features
- Use the [GitHub Issues](https://github.com/yourusername/vanta-ledger/issues) page
- Describe the feature and its benefits
- Consider implementation complexity
- Use the feature request template

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to your branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend development)
- PostgreSQL
- MongoDB
- Git

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/vanta-ledger.git
cd vanta-ledger

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements-hybrid.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Set up databases
createdb vanta_ledger
docker run -d --name mongodb -p 27017:27017 mongo:latest

# Run tests
cd backend
pytest
```

## 📝 Code Style Guidelines

### Python Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

### Example Python Code
```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def process_document(document_path: str, options: Optional[Dict] = None) -> Dict[str, any]:
    """
    Process a document and extract relevant information.
    
    Args:
        document_path: Path to the document file
        options: Optional processing options
        
    Returns:
        Dictionary containing extracted information
        
    Raises:
        FileNotFoundError: If document file doesn't exist
        ProcessingError: If document processing fails
    """
    try:
        # Implementation here
        result = {"status": "success", "data": {}}
        logger.info(f"Successfully processed document: {document_path}")
        return result
    except Exception as e:
        logger.error(f"Failed to process document {document_path}: {e}")
        raise ProcessingError(f"Document processing failed: {e}")
```

### JavaScript/TypeScript Code Style
- Use ESLint and Prettier
- Follow Airbnb JavaScript Style Guide
- Use TypeScript for type safety
- Write meaningful comments
- Use async/await for asynchronous operations

### Example TypeScript Code
```typescript
interface DocumentData {
  id: string;
  filename: string;
  content: string;
  metadata: Record<string, any>;
}

async function processDocument(file: File): Promise<DocumentData> {
  try {
    const content = await file.text();
    const metadata = await extractMetadata(file);
    
    return {
      id: generateId(),
      filename: file.name,
      content,
      metadata
    };
  } catch (error) {
    console.error('Failed to process document:', error);
    throw new Error('Document processing failed');
  }
}
```

## 🧪 Testing Guidelines

### Backend Testing
- Write unit tests for all functions
- Use pytest for testing framework
- Aim for 80%+ code coverage
- Test both success and error cases
- Mock external dependencies

### Example Test
```python
import pytest
from unittest.mock import Mock, patch
from app.services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    def setup_method(self):
        self.processor = DocumentProcessor()
    
    def test_process_document_success(self):
        """Test successful document processing."""
        with patch('builtins.open', mock_open(read_data='test content')):
            result = self.processor.process_document('test.pdf')
            assert result['status'] == 'success'
            assert 'content' in result
    
    def test_process_document_file_not_found(self):
        """Test document processing with missing file."""
        with pytest.raises(FileNotFoundError):
            self.processor.process_document('nonexistent.pdf')
```

### Frontend Testing
- Use Jest for unit testing
- Use React Testing Library for component testing
- Test user interactions and component behavior
- Mock API calls and external dependencies

## 📚 Documentation Guidelines

### Code Documentation
- Write clear docstrings for all functions and classes
- Include type hints
- Document parameters, return values, and exceptions
- Provide usage examples for complex functions

### API Documentation
- Document all API endpoints
- Include request/response examples
- Document error codes and messages
- Keep documentation up to date with code changes

### User Documentation
- Write clear, concise instructions
- Include screenshots where helpful
- Provide troubleshooting guides
- Keep documentation organized and searchable

## 🔒 Security Guidelines

### Code Security
- Never commit sensitive information (API keys, passwords)
- Use environment variables for configuration
- Validate and sanitize all user inputs
- Use parameterized queries for database operations
- Implement proper authentication and authorization

### Example Secure Code
```python
import os
from typing import Optional
import hashlib
import secrets

class SecurityManager:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY')
        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable is required")
    
    def hash_password(self, password: str) -> str:
        """Securely hash a password."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, hash_hex = hashed.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return secrets.compare_digest(hash_obj.hex(), hash_hex)
        except (ValueError, AttributeError):
            return False
```

## 🚀 Pull Request Process

### Before Submitting
1. Ensure your code follows the style guidelines
2. Write or update tests for your changes
3. Run all tests and ensure they pass
4. Update documentation if needed
5. Check that your changes don't break existing functionality

### Pull Request Template
```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive information included
```

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: support@vantaledger.com

### Resources
- [Project Documentation](docs/)
- [API Documentation](http://localhost:8500/docs)
- [Code Style Guide](docs/STYLE_GUIDE.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)

## 🙏 Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributor hall of fame
- GitHub contributors page

Thank you for contributing to Vanta Ledger! 🚀 