# ADR-004: OAuth 2.0 for Gmail Integration

---
tags: [architecture, decision, authentication, security]
audience: [developers, architects, security]
last_updated: 2025-08-07
next_review: 2026-08-07
owner: development_team
status: accepted
---

## Status
Accepted

## Context
The system needs to send emails on behalf of users for job applications. This requires:
- Secure authentication with Gmail/Google accounts
- Permission to send emails from user accounts
- Compliance with Google's security standards
- User consent and control over access
- Ability to revoke access when needed
- Enterprise-grade security practices

## Decision
We will implement OAuth 2.0 authentication flow using Google's official libraries for Gmail integration, specifically using the Gmail API with appropriate scopes for sending emails.

## Consequences

### Positive Consequences
- **Security**: Industry-standard OAuth 2.0 provides secure authentication
- **User Control**: Users maintain control and can revoke access anytime
- **Google Compliance**: Meets Google's security and privacy requirements
- **No Password Storage**: Never need to store user email passwords
- **Scoped Access**: Granular permissions (send-only access, no read access)
- **Official Libraries**: Using Google's official Python libraries ensures compatibility
- **Audit Trail**: Google provides audit logs for sent emails

### Negative Consequences
- **Complexity**: OAuth flow is more complex than simple authentication
- **User Experience**: Requires additional consent flow for users
- **Token Management**: Need to securely store and refresh OAuth tokens
- **Google Dependency**: Tied to Google's OAuth implementation and policies

## Alternatives Considered

### Alternative 1: SMTP with App Passwords
- **Description**: Use SMTP with Google App Passwords for email sending
- **Pros**: Simpler implementation, direct SMTP access
- **Cons**: Less secure, Google deprecating app passwords, no audit trail
- **Decision**: Rejected due to security concerns and Google's deprecation timeline

### Alternative 2: Service Account Authentication
- **Description**: Use Google Service Account for centralized email sending
- **Pros**: Simpler management, centralized control
- **Cons**: All emails sent from single account, less personalization, potential spam issues
- **Decision**: Rejected due to personalization requirements and deliverability concerns

### Alternative 3: Third-Party Email Service
- **Description**: Use services like SendGrid, Mailgun, or Amazon SES
- **Pros**: Designed for transactional email, good deliverability, analytics
- **Cons**: Additional cost, emails not from user's account, less personal touch
- **Decision**: Rejected due to requirement for emails to come from user's Gmail account

### Alternative 4: IMAP/SMTP with User Credentials
- **Description**: Store encrypted user credentials for direct email access
- **Pros**: Full email access, simple implementation
- **Cons**: Major security risk, credential storage issues, violates best practices
- **Decision**: Rejected due to security risks and compliance concerns

## Implementation Notes
- Use Google's official `google-auth-oauthlib` and `google-api-python-client` libraries
- Implement secure token storage with encryption
- Set up token refresh mechanisms for long-term access
- Use minimal required scopes (Gmail send only)
- Implement proper error handling for expired/revoked tokens
- Add user-friendly consent flow with clear permission explanations
- Store OAuth state securely to prevent CSRF attacks

## References
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Python Auth Libraries](https://google-auth.readthedocs.io/)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)

## Related Decisions
- [ADR-001: PostgreSQL as Primary Database](001-database-choice.md) - Storage for OAuth tokens
- [ADR-003: Google Gemini for AI Analysis](003-ai-integration-approach.md) - Google ecosystem integration