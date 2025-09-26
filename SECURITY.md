# Security Policy

## Supported Versions

We support the latest released version of statdesign with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in statdesign, please report it privately to the maintainers:

1. **Do not** open a public issue
2. Email the maintainers at [security contact]
3. Include a clear description of the vulnerability
4. Provide steps to reproduce if possible

We will respond to security reports within 48 hours and work to resolve critical issues promptly.

## Security Considerations

- statdesign performs mathematical calculations and does not handle sensitive data directly
- The CLI tool processes user inputs and should be used with trusted data sources
- When using in production environments, ensure proper input validation
- Keep dependencies up to date using `pip install --upgrade statdesign`