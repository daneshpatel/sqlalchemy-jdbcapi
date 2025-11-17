# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of SQLAlchemy JDBC/ODBC API seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT:

- Open a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

### Please DO:

**Report security vulnerabilities by emailing:** danesh_patel@outlook.com

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to expect:

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
2. **Assessment**: We will confirm the vulnerability and determine its severity within 7 days
3. **Fix Development**: We will work on a fix and keep you informed of progress
4. **Release**: Once a fix is ready, we will:
   - Release a security update
   - Publicly disclose the vulnerability in our CHANGELOG
   - Credit you for the discovery (unless you prefer to remain anonymous)

### Security Update Process:

- Security updates will be released as soon as possible after validation
- Users will be notified via:
  - GitHub Security Advisories
  - Release notes in CHANGELOG.md
  - PyPI release announcements

## Security Best Practices

When using SQLAlchemy JDBC/ODBC API:

1. **Keep dependencies updated**: Regularly update to the latest version
2. **Use parameterized queries**: Always use SQLAlchemy's parameter binding to prevent SQL injection
3. **Secure connection strings**: Never hardcode credentials; use environment variables or secure vaults
4. **Validate input**: Validate and sanitize all user input before using in queries
5. **Use HTTPS/TLS**: Always use encrypted connections to databases when possible
6. **Limit permissions**: Use database accounts with minimal required privileges
7. **Review JVM security**: When using JDBC, ensure your JVM security settings are appropriate
8. **Keep JVM/JDBC drivers updated**: Update Java runtime and JDBC drivers regularly

## Known Security Considerations

### JDBC Driver Security

- JDBC drivers are downloaded from Maven Central by default
- Drivers are verified using SHA-256 checksums when available
- We recommend specifying driver versions explicitly in production environments

### JVM Security

- The library uses JPype1 to interact with the JVM
- Ensure your Java runtime is kept up-to-date with security patches
- Consider JVM security policies for production deployments

### ODBC Security

- ODBC drivers should be obtained from official vendor sources
- Ensure ODBC drivers are kept up-to-date with security patches

## Third-Party Dependencies

We regularly monitor and update our dependencies. Key dependencies include:

- SQLAlchemy (>= 2.0)
- JPype1 (>= 1.5.0) for JDBC support
- pyodbc (>= 5.0.0) for ODBC support (optional)

Please review the security advisories for these dependencies as well.

## Security Hall of Fame

We appreciate security researchers who help keep our project secure. Contributors who responsibly disclose vulnerabilities will be acknowledged here (with permission).

---

Thank you for helping keep SQLAlchemy JDBC/ODBC API and our users safe!
