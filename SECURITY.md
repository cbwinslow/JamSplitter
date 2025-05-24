# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take all security vulnerabilities seriously. If you discover a security vulnerability in JamSplitter, please follow these steps:

1. **Do not** create a public GitHub issue for security vulnerabilities.
2. Email your findings to [security@example.com](mailto:security@example.com) with a detailed description of the vulnerability.
3. Include steps to reproduce the issue, if possible.
4. We will acknowledge your email within 48 hours.
5. We will work on a fix and keep you updated on our progress.
6. Once the issue is resolved, we will release a security update and credit you in the release notes (unless you prefer to remain anonymous).

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.0 → 1.0.1). We recommend always running the latest patch version of the software.

## Security Best Practices

When using JamSplitter, please follow these security best practices:

1. **Never** commit API keys or sensitive information to version control.
2. Use environment variables or a secure secret management system for sensitive configuration.
3. Keep your dependencies up to date.
4. Run the application with the minimum required permissions.
5. Use HTTPS for all API communications.

## Dependency Security

We regularly update our dependencies to address known security vulnerabilities. You can check for known vulnerabilities in our dependencies using:

```bash
pip install safety
safety check
```

## Reporting Security Issues in Dependencies

If you discover a security vulnerability in one of our dependencies, please report it to the maintainers of that project. If the vulnerability affects JamSplitter, please also report it to us following the process above.
