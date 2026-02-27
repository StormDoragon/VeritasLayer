# Security Policy

**VeritasLayer** takes security extremely seriously — especially against adversarial AI and supply-chain attacks.

## Reporting a Vulnerability

- **GitHub Private Vulnerability Reporting**: Go to Security tab → "Report a vulnerability"
- We follow [GitHub coordinated disclosure](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository).

We will acknowledge receipt within 48 hours and aim for a fix within 30 days (or less for critical issues).

## Supported Versions

Only the latest release on `main` is supported.

## Security Features Built-In

- All commits to `main` must be **signed**
- Full branch protection + CODEOWNERS
- Dependabot + CodeQL scanning on every PR
- No untrusted actions in CI (all actions pinned by SHA)
- Adversarial robustness testing in benchmarks
- Strict input validation — zero `eval`/`exec` in production code
- Pydantic v2 strict models with `extra='forbid'` throughout

Thank you for helping keep digital trust infrastructure secure.
