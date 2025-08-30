# 🤝 Contributing to Vanta Ledger

## 🎯 Welcome Contributors!

Thank you for your interest in contributing to **Vanta Ledger**! This guide explains how you can help improve the platform while maintaining our commitment to data privacy.

## 🔒 Important: Code vs. Data

**Vanta Ledger follows a clear separation:**
- **✅ Code**: Open source and freely available for contribution
- **🔒 Data**: Private and protected - never exposed or shared
- **🎯 Goal**: Improve the platform while protecting user privacy

## 🚀 How to Contribute

### **1. 🐛 Report Bugs**
- **GitHub Issues**: Use the Issues tab to report bugs
- **Bug Template**: Fill out the bug report template completely
- **Reproduction Steps**: Include clear steps to reproduce the issue
- **Environment**: Specify your OS, Python version, and setup

### **2. 💡 Suggest Features**
- **Feature Requests**: Submit ideas via GitHub Issues
- **Use Case**: Explain the problem you're solving
- **Priority**: Indicate if it's a nice-to-have or critical feature
- **Mockups**: Include wireframes or examples if possible

### **3. 🔧 Submit Code Changes**
- **Fork & Clone**: Fork the repository and clone locally
- **Feature Branch**: Create a branch for your changes
- **Code Standards**: Follow our coding guidelines
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs for new features

### **4. 📚 Improve Documentation**
- **README Updates**: Fix typos, clarify instructions
- **API Docs**: Improve endpoint documentation
- **Examples**: Add usage examples and tutorials
- **Translations**: Help with internationalization

### **5. 🧪 Testing & Quality**
- **Test Coverage**: Improve test coverage
- **Performance**: Optimize slow operations
- **Security**: Report security vulnerabilities privately
- **Accessibility**: Improve UI/UX accessibility

## 🛠️ Development Setup

### **Prerequisites**
```bash
# Required
- Python 3.11+
- Git
- Docker (optional)

# Recommended
- VS Code or PyCharm
- Pre-commit hooks
- Virtual environment
```

### **Repository Structure**
Understanding the project structure will help you contribute effectively:
```
vanta-ledger/
├── backend/src/vanta_ledger/    # Main application code
│   ├── routes/                  # API endpoints
│   ├── services/                # Business logic
│   ├── models/                  # Data models
│   └── utils/                   # Utility functions
├── frontend/frontend-web/       # React/TypeScript frontend
├── config/                      # Configuration files
│   ├── requirements.txt         # Python dependencies
│   ├── docker-compose.yml       # Container setup
│   └── pyproject.toml          # Project configuration
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── infrastructure/              # Infrastructure components
└── tests/                       # Test suites
```

### **Local Setup**
```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/vanta-ledger.git
cd vanta-ledger

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r config/requirements.txt
pip install -r config/requirements-dev.txt

# 4. Setup pre-commit hooks
pre-commit install

# 5. Run tests
pytest tests/ -v
```

## 📋 Code Standards

### **Python Style Guide**
- **Formatting**: Use Black (line length: 88)
- **Imports**: Use isort for import sorting
- **Linting**: Pass flake8 checks
- **Type Hints**: Use mypy-compatible type hints
- **Docstrings**: Follow Google docstring format

### **Commit Messages**
```
type(scope): brief description

- Use conventional commit format
- Types: feat, fix, docs, style, refactor, test, chore
- Scope: api, ui, auth, docs, etc.
- Description: imperative mood, no period

Examples:
feat(auth): add OAuth2 support for Google
fix(api): resolve user creation race condition
docs(readme): update installation instructions
```

### **Pull Request Guidelines**
- **Title**: Clear, descriptive title
- **Description**: Explain what and why, not how
- **Linked Issues**: Reference related issues
- **Screenshots**: Include UI changes if applicable
- **Tests**: Ensure all tests pass
- **Documentation**: Update relevant docs

## 🔍 Code Review Process

### **Review Checklist**
- [ ] Code follows style guidelines
- [ ] Tests pass and coverage is maintained
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance impact considered
- [ ] Backward compatibility maintained

### **Review Timeline**
- **Initial Review**: Within 48 hours
- **Follow-up**: Within 24 hours of changes
- **Merge**: After approval and CI passes

## 🚨 Security & Privacy

### **Security Guidelines**
- **Never commit**: API keys, passwords, or sensitive data
- **Use environment variables**: For configuration
- **Report vulnerabilities**: Privately to security@vanta-ledger.com
- **Follow OWASP**: Web application security best practices

### **Data Privacy Rules**
- **No user data**: In code, logs, or examples
- **Anonymized testing**: Use fake data for tests
- **Privacy-first design**: Consider privacy in all changes
- **GDPR compliance**: Respect data protection regulations

## 🎉 Recognition

### **Contributor Benefits**
- **GitHub Profile**: Your contributions are visible
- **Release Notes**: Credit in changelog
- **Community**: Join our contributor community
- **Learning**: Gain experience with enterprise software

### **Contributor Levels**
- **Bronze**: 1-5 contributions
- **Silver**: 6-20 contributions  
- **Gold**: 21+ contributions
- **Platinum**: Major features or long-term support

## 📞 Getting Help

### **Support Channels**
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Email**: contributors@vanta-ledger.com
- **Documentation**: Check existing docs first

### **Community Guidelines**
- **Be respectful**: Treat others with kindness
- **Stay on topic**: Keep discussions relevant
- **Help others**: Answer questions when you can
- **Follow rules**: Respect repository guidelines

## 📅 Contribution Calendar

We encourage regular contributions! Set goals like:
- **Monthly**: 1-2 small improvements
- **Quarterly**: 1 medium feature
- **Annually**: 1 major contribution

---

**🤝 Together, we're building the future of financial management!**

*Questions? Open an issue or reach out to our team.* 