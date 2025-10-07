# Google Drive API Setup Guide

**Version:** 1.0
**Last Updated:** October 6, 2025
**Time Required:** 15-20 minutes

This guide will walk you through setting up Google Drive API integration for the Merlin Job Application System. Follow each step carefully.

---

## Prerequisites

- Google Account
- Access to Google Cloud Console
- Python 3.11+ installed
- Merlin project set up locally

---

## Step 1: Install Required Python Libraries

First, install the Google API client libraries:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Verify installation:**
```bash
python -c "from googleapiclient.discovery import build; print('✓ Google API libraries installed')"
```

---

## Step 2: Create Google Cloud Project

### 2.1 Go to Google Cloud Console

1. Open your browser and navigate to: https://console.cloud.google.com/
2. Sign in with your Google account

### 2.2 Create New Project

1. Click the project dropdown at the top of the page (next to "Google Cloud")
2. Click "**NEW PROJECT**" button
3. Enter project details:
   - **Project name:** `Merlin-Job-Application` (or your preferred name)
   - **Organization:** Leave as "No organization" (unless you have a specific org)
4. Click "**CREATE**"
5. Wait for project creation (10-30 seconds)
6. Select your new project from the project dropdown

---

## Step 3: Enable Google Drive API

### 3.1 Navigate to APIs & Services

1. In Google Cloud Console, click the **☰ menu** (top left)
2. Go to: **APIs & Services** → **Library**

### 3.2 Enable the API

1. In the search bar, type: `Google Drive API`
2. Click on "**Google Drive API**" from results
3. Click the blue "**ENABLE**" button
4. Wait for API to be enabled (5-10 seconds)

---

## Step 4: Create OAuth 2.0 Credentials

### 4.1 Configure OAuth Consent Screen

1. Go to: **APIs & Services** → **OAuth consent screen**
2. Select user type:
   - Choose "**External**" (unless you have Google Workspace)
   - Click "**CREATE**"

3. Fill in App information:
   - **App name:** `Merlin Job Application System`
   - **User support email:** [Your email address]
   - **Developer contact information:** [Your email address]
4. Click "**SAVE AND CONTINUE**"

5. Scopes screen:
   - Click "**ADD OR REMOVE SCOPES**"
   - Scroll down and manually add: `https://www.googleapis.com/auth/drive.file`
   - Or search for ".../auth/drive.file" in the filter
   - Check the box next to this scope
   - Click "**UPDATE**"
   - Click "**SAVE AND CONTINUE**"

6. Test users screen:
   - Click "**+ ADD USERS**"
   - Add your Gmail address (the one you'll use for storage)
   - Click "**ADD**"
   - Click "**SAVE AND CONTINUE**"

7. Summary screen:
   - Review your settings
   - Click "**BACK TO DASHBOARD**"

### 4.2 Create OAuth Client ID

1. Go to: **APIs & Services** → **Credentials**
2. Click "**+ CREATE CREDENTIALS**" at the top
3. Select "**OAuth client ID**"
4. Configure the client:
   - **Application type:** Desktop app
   - **Name:** `Merlin Desktop Client`
5. Click "**CREATE**"
6. You'll see a dialog "OAuth client created"

### 4.3 Download Credentials

1. Click "**DOWNLOAD JSON**" button in the dialog
2. Save the file (it will be named something like `client_secret_XXX.json`)
3. Click "**OK**" to close the dialog

---

## Step 5: Configure Merlin Project

### 5.1 Move Credentials File

1. Locate the downloaded JSON file
2. Rename it to: `google_drive_credentials.json`
3. Move it to your Merlin project:
   ```bash
   mv ~/Downloads/client_secret_*.json /workspace/.trees/replit-storage-replacement/storage/google_drive_credentials.json
   ```

### 5.2 Verify File Location

```bash
ls -la /workspace/.trees/replit-storage-replacement/storage/google_drive_credentials.json
```

You should see the file listed.

### 5.3 Update Environment Variables

1. Create or update your `.env` file:
   ```bash
   cd /workspace/.trees/replit-storage-replacement
   cp .env.example .env  # If .env doesn't exist
   ```

2. Edit `.env` file and set these variables:
   ```bash
   # Storage Configuration
   STORAGE_BACKEND=google_drive
   APP_VERSION=4.1

   # Google Drive Configuration
   GOOGLE_DRIVE_CREDENTIALS_PATH=./storage/google_drive_credentials.json
   GOOGLE_DRIVE_TOKEN_PATH=./storage/google_drive_token.json
   ```

3. Save the file

---

## Step 6: First-Time Authentication

### 6.1 Run Authentication Flow

The first time you use Google Drive storage, you need to authenticate:

```bash
cd /workspace/.trees/replit-storage-replacement

python -c "
import os
os.environ['STORAGE_BACKEND'] = 'google_drive'
os.environ['APP_VERSION'] = '4.1'
os.environ['GOOGLE_DRIVE_CREDENTIALS_PATH'] = './storage/google_drive_credentials.json'
os.environ['GOOGLE_DRIVE_TOKEN_PATH'] = './storage/google_drive_token.json'

from modules.storage import get_storage_backend
storage = get_storage_backend()
print('✓ Google Drive storage initialized successfully')
"
```

### 6.2 Complete OAuth Flow

1. **Browser window will open automatically**
2. You'll see a Google sign-in page
3. **Select your Google account** (must be the test user you added earlier)
4. You may see a warning: "Google hasn't verified this app"
   - Click "**Advanced**"
   - Click "**Go to Merlin Job Application System (unsafe)**"
   - This is safe - it's your own app
5. Grant permissions:
   - Review the permissions requested
   - Click "**Allow**"
6. You'll see "The authentication flow has completed"
7. **Close the browser tab**
8. Return to your terminal

### 6.3 Verify Success

You should see in your terminal:
```
✓ Google Drive storage initialized successfully
```

Check that token file was created:
```bash
ls -la ./storage/google_drive_token.json
```

---

## Step 7: Test Google Drive Upload

### 7.1 Run Test Upload

```bash
python -c "
import os
os.environ['STORAGE_BACKEND'] = 'google_drive'
os.environ['APP_VERSION'] = '4.1'

from modules.storage import get_storage_backend

storage = get_storage_backend()

# Create test file
test_content = b'This is a test document for Google Drive integration'
result = storage.save('test_document.txt', test_content)

print('✓ Upload successful!')
print(f'  File ID: {result[\"google_drive_file_id\"]}')
print(f'  Link: {result[\"google_drive_link\"]}')
print(f'  Folder: {result[\"folder_path\"]}')
"
```

### 7.2 Verify in Google Drive

1. Open Google Drive in your browser: https://drive.google.com
2. Look for a folder named "**Merlin Documents**"
3. Inside, you should see a folder "**v4.1**"
4. Inside that, you should see: `merlin_v4.1_test_document.txt`
5. Click on it to verify the content

**✓ Success!** Google Drive integration is working!

---

## Step 8: Configure Document Generator with Fallback

Now we need to ensure the document generator falls back to local storage if Google Drive fails.

### 8.1 Update Document Generator

The document generator already supports storage abstraction. No code changes needed! It will automatically use whatever backend is configured in `STORAGE_BACKEND`.

### 8.2 Test with Fallback

To test fallback behavior (optional):

```bash
# Temporarily break Google Drive (rename credentials)
mv ./storage/google_drive_credentials.json ./storage/google_drive_credentials.json.bak

# Try to upload - should fall back to local
python -c "
import os
os.environ['STORAGE_BACKEND'] = 'google_drive'
os.environ['APP_VERSION'] = '4.1'

from modules.content.document_generation.document_generator import DocumentGenerator

gen = DocumentGenerator()
# This will fail to init Google Drive and fall back to local
print('Generator initialized with fallback')
"

# Restore credentials
mv ./storage/google_drive_credentials.json.bak ./storage/google_drive_credentials.json
```

---

## Step 9: Production Use

### 9.1 Start Using Google Drive Storage

Set your environment permanently:

**Edit `.env`:**
```bash
STORAGE_BACKEND=google_drive
APP_VERSION=4.1
```

All new documents will now be uploaded to Google Drive automatically!

### 9.2 Folder Structure

Your documents will be organized as:
```
Google Drive
└── Merlin Documents/
    └── v4.1/
        ├── merlin_v4.1_resume_2025_10_06_abc123.docx
        ├── merlin_v4.1_coverletter_2025_10_06_def456.docx
        └── ...
```

When you update `APP_VERSION` to `4.2`, a new folder will be created automatically.

---

## Troubleshooting

### Problem: "Google hasn't verified this app" and can't proceed

**Solution:**
- Make sure you added your email as a test user in Step 4.1 (OAuth consent screen)
- You must click "Advanced" → "Go to [app name] (unsafe)" to proceed

### Problem: "Access blocked: Authorization Error"

**Solution:**
- Verify you selected the correct scope: `https://www.googleapis.com/auth/drive.file`
- Try deleting and recreating OAuth credentials
- Make sure you're signing in with the test user account

### Problem: "Invalid grant" or token errors

**Solution:**
```bash
# Delete token and re-authenticate
rm ./storage/google_drive_token.json

# Run authentication again (Step 6)
```

### Problem: ImportError for Google libraries

**Solution:**
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Problem: File not appearing in Google Drive

**Solution:**
- Wait 30 seconds and refresh Google Drive
- Check the correct folder: Merlin Documents → v{APP_VERSION}
- Verify the filename starts with `merlin_v4.1_`

### Problem: Can't find the uploaded file by filename

**Solution:**
- Google Drive search is by file ID, not filename
- Use the web interface or `google_drive_link` to locate files

---

## Security Notes

### Files Stored Locally (DO NOT COMMIT)

These files contain sensitive credentials and should **NEVER** be committed to git:

- `./storage/google_drive_credentials.json` - OAuth client secrets
- `./storage/google_drive_token.json` - Access tokens
- `.env` - Environment configuration

**Verify gitignore:**
```bash
grep -E "google_drive|\.env|storage/" .gitignore
```

Should see:
```
.env
storage/
```

### File Permissions

All files uploaded are **private** (owner-only access). They will only be visible to the Google account that authenticated.

### Token Security

- Tokens are stored in `./storage/google_drive_token.json`
- They expire after 1 hour but are automatically refreshed
- Never share token files
- If compromised, delete the file and re-authenticate

---

## Next Steps

1. ✅ **Complete database schema changes** to store Google Drive file IDs
2. ✅ **Update requirements.txt** with Google API dependencies
3. ✅ **Test with real document generation**
4. ✅ **Remove AWS references** from codebase
5. ✅ **Deploy to production**

---

## Quick Reference

### Key Environment Variables
```bash
STORAGE_BACKEND=google_drive
APP_VERSION=4.1
GOOGLE_DRIVE_CREDENTIALS_PATH=./storage/google_drive_credentials.json
GOOGLE_DRIVE_TOKEN_PATH=./storage/google_drive_token.json
```

### Important URLs
- Google Cloud Console: https://console.cloud.google.com/
- Google Drive: https://drive.google.com
- API Library: https://console.cloud.google.com/apis/library

### Command Reference
```bash
# Test storage
python -c "from modules.storage import get_storage_backend; print(get_storage_backend())"

# Validate configuration
python -c "from modules.storage import validate_storage_configuration; print(validate_storage_configuration())"

# Re-authenticate
rm ./storage/google_drive_token.json
# Then run your app or test script
```

---

**Setup Complete! 🎉**

Your Merlin Job Application System is now connected to Google Drive. All generated documents will be automatically uploaded and organized by version number.

For questions or issues, refer to the Troubleshooting section above.
