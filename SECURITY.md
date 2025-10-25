# Security Policy

## Supported Versions

We provide security updates for the following versions of calibre-mcp:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in calibre-mcp, please follow these steps:

### 1. **DO NOT** create a public GitHub issue

Security vulnerabilities should be reported privately to prevent exploitation.

### 2. Email Security Report

Send an email to: **security@example.com**

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes (if available)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution**: Within 30 days (depending on complexity)

### 4. What to Expect

- We will acknowledge receipt of your report
- We will investigate the vulnerability
- We will provide regular updates on our progress
- We will coordinate the release of fixes with you
- We will credit you in our security advisories (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

1. **Keep calibre-mcp updated** to the latest version
2. **Use strong authentication** for your Calibre server
3. **Limit network access** to your Calibre server
4. **Regular backups** of your library data
5. **Monitor access logs** for suspicious activity

### For Developers

1. **Input validation** - Always validate user inputs
2. **SQL injection prevention** - Use parameterized queries
3. **Authentication** - Implement proper authentication checks
4. **Authorization** - Verify user permissions for all operations
5. **Error handling** - Don't expose sensitive information in error messages

## Security Features

calibre-mcp includes several security features:

- **Input sanitization** for all user inputs
- **SQL injection protection** through parameterized queries
- **Authentication support** for Calibre server access
- **Rate limiting** to prevent abuse
- **Error handling** that doesn't expose sensitive data

## Dependencies

We regularly audit our dependencies for security vulnerabilities:

- **Automated scanning** with Dependabot
- **Manual reviews** of critical dependencies
- **Regular updates** to latest secure versions
- **Security-focused dependency choices**

## Disclosure Policy

- Vulnerabilities are disclosed after fixes are available
- We coordinate disclosure with security researchers
- Public disclosure includes:
  - Description of the vulnerability
  - Impact assessment
  - Mitigation steps
  - Credit to researchers (with permission)

## Contact

For security-related questions or concerns:
- **Email**: security@example.com
- **Response Time**: Within 48 hours

---

**Last Updated**: 2025-01-21  
**Next Review**: 2025-04-21
