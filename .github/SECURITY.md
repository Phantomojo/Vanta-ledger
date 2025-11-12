# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of Vanta Ledger seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Email**: Send details to the repository maintainer (@Phantomojo)
2. **GitHub Security Advisory**: Use the [Security Advisory](../../security/advisories/new) feature
3. **Private Issue**: Request a private security issue be created

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Resolution Timeline**: Varies based on severity
  - Critical: 7 days
  - High: 30 days
  - Medium: 90 days
  - Low: Best effort

### What to Expect

After you submit a vulnerability report:

1. We will acknowledge receipt of your report
2. We will investigate and validate the vulnerability
3. We will work on a fix and keep you updated on progress
4. We will coordinate disclosure timing with you
5. We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When using Vanta Ledger, we recommend:

### Environment Variables
- Never commit `.env` files or secrets to version control
- Use strong, randomly generated passwords and API keys
- Rotate secrets regularly (at least every 90 days)
- Use different secrets for development, staging, and production

### Database Security
- Use strong database passwords (16+ characters)
- Enable SSL/TLS for database connections
- Restrict database access to specific IP addresses
- Regular backups with encryption at rest

### API Security
- Always use HTTPS in production
- Keep JWT tokens short-lived (30 minutes recommended)
- Implement proper rate limiting
- Use refresh tokens for extended sessions

### Docker/Container Security
- Keep base images updated
- Scan containers for vulnerabilities regularly
- Use non-root users in containers
- Limit container capabilities

### Dependencies
- Keep dependencies up to date
- Use `pip install -r requirements.txt -c constraints.txt` for pinned versions
- Review Dependabot alerts promptly
- Run security scans regularly (`bandit`, `safety check`)

## Security Features

Vanta Ledger includes the following security features:

- **Authentication**: JWT-based authentication with configurable expiry
- **Rate Limiting**: Configurable rate limits (100/min, 1000/hour default)
- **Password Policies**: Enforced complexity requirements
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Input Validation**: Pydantic models for all API inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS**: Configurable allowed origins
- **Audit Logging**: Comprehensive logging of security events

## Security Scanning

We use multiple security scanning tools:

- **CodeQL**: Automated code analysis for vulnerabilities
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Semgrep**: Static analysis for security patterns
- **TruffleHog**: Secret detection in code and history
- **Detect-secrets**: Pre-commit hook for secret detection

## Compliance

Vanta Ledger is designed with security and compliance in mind:

- Environment-based configuration (12-factor app)
- Encryption at rest and in transit
- Audit trails for all user actions
- Role-based access control (RBAC)
- Multi-tenant data isolation

## Security Updates

Security updates are released as soon as possible after a vulnerability is confirmed:

- Critical vulnerabilities: Immediate patch release
- High severity: Within 7 days
- Medium severity: Within 30 days
- Low severity: Included in next regular release

Subscribe to our security advisories to stay informed about security updates.

## Acknowledgments

We appreciate the security research community's efforts in responsibly disclosing vulnerabilities. Security researchers who report valid vulnerabilities will be acknowledged in our security advisories (with permission).

## Questions?

If you have questions about this security policy, please open a discussion or contact the maintainers.

---

**Last Updated**: November 12, 2025  
**Version**: 2.0.0
