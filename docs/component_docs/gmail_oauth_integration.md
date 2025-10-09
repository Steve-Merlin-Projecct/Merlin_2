---
title: Gmail OAuth Integration Documentation
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: reference
status: active
tags:
- gmail
- oauth
- integration
---

# Gmail OAuth Integration Documentation

**Status:** Fully Operational  
**Last Updated:** July 23, 2025  
**Version:** 2.14 (Enhanced Robustness)

## Overview

The Gmail OAuth integration provides secure, automated email sending capabilities for the job application system using Google's official OAuth 2.0 flow and Gmail API. The system sends emails from `1234.S.t.e.v.e.Glen@gmail.com` with full attachment support and enterprise-grade robustness features.

## How OAuth Works

### OAuth 2.0 Flow Architecture

The system uses Google's official `google-auth-oauthlib` and `google-api-python-client` libraries following the InstalledAppFlow pattern:

1. **Credentials Setup**: Client ID and Client Secret stored in `storage/oauth_credentials.json`
2. **Authorization URL Generation**: System generates Google authorization URL with required scopes
3. **User Consent**: User authorizes Gmail access through Google's consent screen
4. **Token Exchange**: Authorization code exchanged for access/refresh tokens
5. **Token Storage**: Tokens saved to `storage/gmail_token.json` for reuse
6. **API Access**: Tokens used to authenticate Gmail API requests

### Required Scopes
- `https://www.googleapis.com/auth/gmail.send` - Send emails on behalf of user

### Token Management
- **Access Tokens**: Short-lived (1 hour), used for API requests
- **Refresh Tokens**: Long-lived, used to generate new access tokens
- **Automatic Refresh**: System automatically refreshes expired tokens

## Implementation Files

### Core Components

**`modules/email_integration/gmail_oauth_official.py`**
- Main OAuth manager using official Google libraries
- Handles complete OAuth flow and token management
- Provides Gmail service creation and email sending

**`modules/email_integration/gmail_enhancements.py`**
- Enhanced robustness features (100% test success rate)
- Email validation, attachment checking, error handling
- Retry mechanisms with exponential backoff
- Connection health monitoring

**`modules/email_integration/email_api.py`**
- Flask Blueprint providing REST API endpoints
- OAuth status checking and email sending endpoints
- Protected with authentication requirements

### Configuration Files

**`storage/oauth_credentials.json`**
```json
{
  "client_id": "your-google-client-id",
  "client_secret": "your-google-client-secret",
  "redirect_uris": ["http://localhost"]
}
```

**`storage/gmail_token.json`** (Auto-generated)
```json
{
  "token": "access-token",
  "refresh_token": "refresh-token",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "client-id",
  "client_secret": "client-secret",
  "scopes": ["https://www.googleapis.com/auth/gmail.send"],
  "expiry": "2025-07-24T12:00:00Z"
}
```

## Current Operational Status

### Authentication Status
- **Gmail Account**: 1234.S.t.e.v.e.Glen@gmail.com
- **OAuth Status**: Authenticated and operational
- **Token Status**: Valid with automatic refresh
- **Last Verified**: July 23, 2025

### Verified Functionality
- **Basic Email Sending**: ✅ Confirmed (Message ID: 1983525fe6f29567)
- **Email with Attachments**: ✅ Confirmed (Message ID: 19835288f91730b5)
- **Enhanced Robustness**: ✅ Confirmed (Message ID: 198352e9445146a1)
- **Error Handling**: ✅ 100% test success rate
- **Production Scenarios**: ✅ 75% success rate

### API Endpoints
- `GET /api/email/oauth-status` - Check OAuth authentication status
- `POST /api/email/send` - Send email with optional attachments
- `POST /api/email/test` - Send test email for verification

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "OAuth credentials not configured"
**Cause**: Missing or invalid `storage/oauth_credentials.json`

**Solution**:
1. Verify Google Cloud Console project has Gmail API enabled
2. Create OAuth 2.0 client credentials (Desktop Application type)
3. Download credentials and save as `storage/oauth_credentials.json`
4. Ensure redirect URI is exactly `http://localhost`

#### 2. "Authentication failed" or "Unauthorized"
**Cause**: Expired or invalid tokens

**Solution**:
1. Delete `storage/gmail_token.json`
2. Run OAuth flow again: `oauth_manager.get_authorization_url()`
3. Complete authorization and exchange code for new tokens
4. Verify with `oauth_manager.get_oauth_status()`

#### 3. "Quota exceeded" errors
**Cause**: Gmail API rate limits exceeded

**Solution**:
1. Check Google Cloud Console quotas
2. Implement delays between email sends
3. Consider upgrading quotas if needed
4. Use retry mechanism with exponential backoff

#### 4. "Invalid To header" errors
**Cause**: Invalid email address format

**Solution**:
1. Use enhanced email validation: `EmailValidator.is_valid_email()`
2. Sanitize emails: `EmailValidator.sanitize_email()`
3. Check for injection attempts (newlines, special characters)

#### 5. "Attachment too large" errors
**Cause**: Attachments exceed Gmail's 25MB limit

**Solution**:
1. Use attachment validation: `AttachmentValidator.validate_attachment()`
2. Compress large files before sending
3. Consider using cloud storage links for large files

### Diagnostic Commands

**Check OAuth Status**:
```python
from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager
oauth_manager = get_gmail_oauth_manager()
status = oauth_manager.get_oauth_status()
print(status)
```

**Test Connection Health**:
```python
from modules.email_integration.gmail_enhancements import GmailConnectionHealthChecker
health_checker = GmailConnectionHealthChecker(oauth_manager)
health = health_checker.check_connection_health()
print(health)
```

**Send Test Email**:
```python
from modules.email_integration.gmail_enhancements import get_enhanced_gmail_sender
sender = get_enhanced_gmail_sender()
result = sender.send_job_application_email_enhanced(
    to_email="test@example.com",
    subject="Test",
    body="Test message",
    attachments=None
)
print(result)
```

### Log File Locations

- **Gmail Errors**: `storage/logs/gmail_errors.log`
- **Application Logs**: Check Flask application logs
- **OAuth Debug**: Enable logging in OAuth manager for detailed flow

### Google Cloud Console References

**Required APIs**:
- Gmail API (enabled)
- Google+ API (for user profile access)

**OAuth 2.0 Configuration**:
- Application type: Desktop Application
- Authorized redirect URIs: `http://localhost`
- Scopes: `https://www.googleapis.com/auth/gmail.send`

**Quota Monitoring**:
- Navigate to "APIs & Services" > "Quotas"
- Monitor Gmail API usage
- Set up alerts for quota limits

## Security Considerations

### Token Security
- Tokens stored locally in `storage/` directory
- Access tokens expire automatically (1 hour)
- Refresh tokens used for re-authentication
- Never log or expose tokens in plain text

### Input Validation
- All email addresses validated with RFC-compliant regex
- Subject lines sanitized to prevent injection
- Attachments validated for size and type
- User input sanitized before API calls

### Error Handling
- Errors categorized by type (quota, network, auth, validation)
- Sensitive information excluded from error messages
- Comprehensive logging for debugging
- User-friendly error messages provided

## Maintenance Guidelines

### Regular Maintenance
1. **Monitor Token Expiry**: Tokens refresh automatically but monitor for issues
2. **Check API Quotas**: Review usage in Google Cloud Console monthly
3. **Update Dependencies**: Keep Google client libraries updated
4. **Test Email Sending**: Monthly verification emails recommended

### Emergency Recovery
1. **Complete Re-authorization**: Delete all tokens and re-run OAuth flow
2. **Credential Rotation**: Generate new client ID/secret if compromised
3. **Backup Authentication**: Keep backup Gmail account configured
4. **Alternative Sending**: Consider SMTP fallback for critical emails

## Future Enhancements

### Planned Improvements
- Multiple Gmail account support
- Email template management
- Advanced attachment handling
- Bulk email sending optimization
- Enhanced monitoring and alerting

### Integration Opportunities
- Calendar integration for interview scheduling
- Drive integration for document storage
- Sheets integration for application tracking
- Meet integration for video interviews

## Support Resources

### Google Documentation
- [Gmail API Overview](https://developers.google.com/gmail/api/guides)
- [OAuth 2.0 for Installed Applications](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)

### Library Documentation
- [google-auth-oauthlib](https://google-auth-oauthlib.readthedocs.io/)
- [google-api-python-client](https://github.com/googleapis/google-api-python-client)

### Project-Specific Help
- Review archived setup scripts: `archived_files/scripts/oauth_setup/`
- Check enhancement tests: `test_enhanced_gmail_robustness.py`
- Examine production tests: `tests/test_gmail_production_scenarios.py`

---

**Last Verification**: System operational with enhanced robustness features  
**Contact**: Review project documentation or Google Cloud Console for configuration issues