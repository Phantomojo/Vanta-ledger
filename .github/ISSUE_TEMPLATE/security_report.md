---
name: 🔒 Security Vulnerability Report
about: Report a security vulnerability (for non-security bugs, use Bug Report)
title: '[SECURITY] '
labels: 'security'
assignees: 'Phantomojo'
---

## ⚠️ IMPORTANT: Do Not Disclose Publicly

**If this is a security vulnerability, please DO NOT create a public issue.**

Instead, please:
1. Use GitHub's [Security Advisory](../../security/advisories/new) feature, or
2. Email the maintainers directly
3. Request this issue be made private

If you've already created this public issue and it contains sensitive information, please:
- Delete it immediately
- Report via private channels instead

---

## 🔒 Security Vulnerability Details

### Vulnerability Type
<!-- Check all that apply -->
- [ ] SQL Injection
- [ ] Cross-Site Scripting (XSS)
- [ ] Authentication Bypass
- [ ] Authorization Issue
- [ ] Sensitive Data Exposure
- [ ] Cryptographic Failure
- [ ] Injection Flaw
- [ ] Insecure Deserialization
- [ ] Security Misconfiguration
- [ ] Vulnerable Dependencies
- [ ] Other (please describe)

### Severity Assessment
<!-- Your assessment of severity -->
- [ ] Critical (immediate action required)
- [ ] High (serious impact)
- [ ] Medium (moderate impact)
- [ ] Low (minimal impact)

### Affected Component
<!-- Which part of the system is affected? -->
- [ ] Backend API
- [ ] Frontend
- [ ] Database
- [ ] Authentication
- [ ] Authorization
- [ ] File Upload
- [ ] AI/ML Components
- [ ] Docker/Infrastructure
- [ ] Other: ___________

### Affected Version(s)
<!-- Which version(s) are affected? -->
Version: 

### Description
<!-- Clear description of the vulnerability -->


### Steps to Reproduce
<!-- Detailed steps to reproduce the vulnerability -->
1. 
2. 
3. 

### Proof of Concept
<!-- If safe to share, provide PoC code or screenshots -->
```python
# PoC code here
```

### Impact
<!-- What could an attacker achieve with this vulnerability? -->


### Suggested Fix
<!-- If you have suggestions for fixing the vulnerability -->


### Environment
- **OS**: 
- **Python Version**: 
- **Vanta Ledger Version**: 
- **Deployment**: (Docker/Local/Cloud)

### Additional Context
<!-- Any additional information -->


---

## Confidentiality Notice

By submitting this report, you agree to:
- Not disclose the vulnerability publicly until a fix is released
- Allow reasonable time for the maintainers to address the issue
- Coordinate disclosure timing with the project maintainers

We commit to:
- Acknowledge your report within 48 hours
- Keep you updated on fix progress
- Credit you in the security advisory (if desired)
- Work with you on coordinated disclosure
