# Secrets Management Guide

This document outlines how to manage secrets for the Merlin job application system.

## Required Secrets

### Local Development
Create a `.env` file in the project root (already in `.gitignore`):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/database_name

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Apify (Job Scraping)
APIFY_API_TOKEN=your_apify_token_here

# Gmail OAuth
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# API Security
WEBHOOK_API_KEY=your_webhook_api_key_here

# Optional: Flask
FLASK_SECRET_KEY=your_random_secret_key_here
```

### GitHub Secrets (For Future CI/CD)
If you decide to add automated deployments, configure these in:
**Settings → Secrets and variables → Actions**

- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini AI API key
- `APIFY_API_TOKEN` - Apify job scraper token
- `GMAIL_CLIENT_ID` - Gmail OAuth client ID
- `GMAIL_CLIENT_SECRET` - Gmail OAuth client secret
- `WEBHOOK_API_KEY` - API authentication key

## Security Best Practices

1. **Never commit secrets to git**
   - `.gitignore` is configured to block common secret files
   - Review changes before committing

2. **Rotate secrets regularly**
   - Change API keys every 90 days
   - Rotate after any suspected compromise

3. **Use environment-specific secrets**
   - Different keys for development/production
   - Never use production secrets in development

4. **Generate strong secrets**
   ```bash
   # Generate a random secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Backup secrets securely**
   - Use a password manager (1Password, Bitwarden, etc.)
   - Never store in plain text files

## How to Load Secrets in Python

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access secrets
database_url = os.environ.get('DATABASE_URL')
gemini_key = os.environ.get('GEMINI_API_KEY')
```

## Checking for Leaked Secrets

```bash
# GitHub now has push protection enabled
# It will block pushes containing secrets

# To manually check for secrets before committing:
git diff --cached | grep -i "api_key\|secret\|password\|token"
```

## Getting API Keys

- **Gemini**: https://ai.google.dev/
- **Apify**: https://console.apify.com/account/integrations
- **Gmail OAuth**: https://console.cloud.google.com/apis/credentials
