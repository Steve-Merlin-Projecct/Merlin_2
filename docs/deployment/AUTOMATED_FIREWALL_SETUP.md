---
title: "Automated Firewall Setup"
type: technical_doc
component: general
status: draft
tags: []
---

# Automated Digital Ocean Firewall Configuration

**Security Level:** Production-Ready
**Method:** Digital Ocean API v2
**Authentication:** Bearer Token (Secure)

---

## Prerequisites

1. Digital Ocean account with database access
2. API token with **read and write** permissions
3. Python 3.11+ with `requests` library

---

## Step 1: Generate Digital Ocean API Token (Secure Method)

### Access Token Management

1. **Log into Digital Ocean:**
   - Go to: https://cloud.digitalocean.com/account/api/tokens

2. **Click "Generate New Token"**

3. **Configure Token Settings:**
   ```
   Token Name: database-firewall-config
   Expiration: 90 days (recommended for security)
   Scopes: Read and Write
   ```

4. **Click "Generate Token"**

5. **⚠️ CRITICAL - Copy Token Immediately:**
   - Token is shown **ONLY ONCE**
   - Copy the entire token (starts with `dop_v1_`)
   - Store securely (do not share or commit to git)

### Example Token Format:
```
dop_v1_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd
```

---

## Step 2: Add API Token to Environment (Secure)

### Method 1: Environment Variable (Recommended for Local)

```bash
# Add to .env file (gitignored)
echo "DIGITALOCEAN_API_TOKEN=dop_v1_your_token_here" >> .env
```

### Method 2: Export in Shell (Temporary)

```bash
# For current session only
export DIGITALOCEAN_API_TOKEN="dop_v1_your_token_here"
```

### Method 3: Production Deployment Platform

**Digital Ocean App Platform:**
1. Go to: Your App → Settings → Environment Variables
2. Add new variable:
   ```
   Key:   DIGITALOCEAN_API_TOKEN
   Value: dop_v1_your_token_here
   Type:  Secret (encrypted)
   ```

**Other Platforms:**
- Use platform's secure secret management
- Never hardcode in code or configuration files
- Always use encrypted storage

---

## Step 3: Install Dependencies

```bash
# Ensure requests library is installed
pip install requests python-dotenv
```

Or verify it's in requirements.txt:
```bash
grep requests requirements.txt
```

---

## Step 4: Run Automated Configuration

```bash
# Navigate to project directory
cd /workspace/.trees/production-dashboard-password-and-configuration

# Run configuration script
python configure_do_firewall.py
```

### Expected Output:

```
================================================================================
Digital Ocean Database Firewall Configuration
================================================================================
🔍 Finding database ID...
✅ Found database: db-postgresql-merlin-tor1-52568 (ID: abc123...)

📋 Retrieving current firewall rules...
✅ Found 0 existing rule(s):
================================================================================

================================================================================
Configuration Options:
================================================================================
1. Add current machine's IP address
2. Add specific IP address
3. Add Digital Ocean App
4. Add Digital Ocean Droplet
5. Remove trusted source
6. View current rules
7. Exit
================================================================================

Select option (1-7):
```

---

## Configuration Options Explained

### Option 1: Add Current Machine's IP (Automatic)

**Use Case:** Configure from your development machine or server

**Process:**
1. Script automatically detects your public IP
2. Shows you the detected IP for confirmation
3. Adds to trusted sources after confirmation

**Security:** Safe - shows IP before adding

```
Select option (1-7): 1

📍 Detected IP: 203.0.113.45
Add this IP to trusted sources? (yes/no): yes

🔐 Adding trusted source:
   Type: ip_addr
   Value: 203.0.113.45

📋 Retrieving current firewall rules...
✅ Found 0 existing rule(s):

✅ Successfully added trusted source!
```

---

### Option 2: Add Specific IP Address (Manual)

**Use Case:** Add production server, staging server, or known IP

**Process:**
1. Enter specific IP address
2. Script validates format
3. Adds to trusted sources

**Example:**
```
Select option (1-7): 2

Enter IP address (e.g., 192.168.1.100): 203.0.113.100

🔐 Adding trusted source:
   Type: ip_addr
   Value: 203.0.113.100

✅ Successfully added trusted source!
```

---

### Option 3: Add Digital Ocean App (App Platform)

**Use Case:** Your dashboard is deployed on Digital Ocean App Platform

**Prerequisites:**
- Find your App ID in App Platform dashboard
- Format: UUID (e.g., `f81d4fae-7dec-11d0-a765-00a0c91e6bf6`)

**How to Find App ID:**
1. Go to: https://cloud.digitalocean.com/apps
2. Click on your app
3. Look at URL: `https://cloud.digitalocean.com/apps/YOUR-APP-ID`
4. Copy the App ID (UUID)

**Process:**
```
Select option (1-7): 3

Enter App Platform App ID (UUID): f81d4fae-7dec-11d0-a765-00a0c91e6bf6

🔐 Adding trusted source:
   Type: app
   Value: f81d4fae-7dec-11d0-a765-00a0c91e6bf6

✅ Successfully added trusted source!
```

**Benefit:** Automatically updates if app's IP changes

---

### Option 4: Add Digital Ocean Droplet

**Use Case:** Dashboard running on Digital Ocean Droplet (VPS)

**How to Find Droplet ID:**
1. Go to: https://cloud.digitalocean.com/droplets
2. Click on your droplet
3. Droplet ID shown in URL or use:
   ```bash
   # If doctl is installed
   doctl compute droplet list
   ```

**Process:**
```
Select option (1-7): 4

Enter Droplet ID: 123456789

🔐 Adding trusted source:
   Type: droplet
   Value: 123456789

✅ Successfully added trusted source!
```

---

### Option 5: Remove Trusted Source

**Use Case:** Remove old IPs or decommissioned resources

**Process:**
```
Select option (1-7): 5

Current rules:
✅ Found 2 existing rule(s):
   1. Type: ip_addr, Value: 203.0.113.45
   2. Type: app, Value: f81d4fae-7dec-11d0-a765-00a0c91e6bf6

Enter rule number to remove (1-2): 1

Remove ip_addr: 203.0.113.45? (yes/no): yes

🗑️  Removing trusted source:
   Type: ip_addr
   Value: 203.0.113.45

✅ Successfully removed trusted source!
```

---

### Option 6: View Current Rules

**Use Case:** Check current firewall configuration

**Output:**
```
Select option (1-7): 6

📋 Retrieving current firewall rules...
✅ Found 2 existing rule(s):
   1. Type: app, Value: f81d4fae-7dec-11d0-a765-00a0c91e6bf6
   2. Type: ip_addr, Value: 203.0.113.100
```

---

## Step 5: Test Database Connection

After adding trusted sources:

```bash
# Test connection
python test_db_connection.py
```

**Expected Success Output:**
```
================================================================================
Digital Ocean Database Connection Test
================================================================================

✅ SUCCESS! Connected to Digital Ocean database

PostgreSQL Version: PostgreSQL 16.x on x86_64-pc-linux-gnu
Database Name: defaultdb
Connected User: doadmin
Number of tables in public schema: 32
```

**If Connection Fails:**
1. Wait 1-2 minutes (firewall propagation delay)
2. Verify trusted source was added (Option 6)
3. Check that correct IP/resource was added
4. Retry test

---

## Security Best Practices

### ✅ DO:

1. **Secure Token Storage:**
   - Store API token in `.env` (gitignored)
   - Use environment variables only
   - Never commit to version control

2. **Token Management:**
   - Set expiration (90 days recommended)
   - Rotate tokens regularly
   - Revoke unused tokens immediately

3. **Access Control:**
   - Use minimum required permissions (read + write for databases)
   - Create separate tokens for different purposes
   - Never share tokens between environments

4. **Audit Logging:**
   - Review Digital Ocean audit logs regularly
   - Monitor for unauthorized access attempts
   - Track when tokens are created/revoked

5. **Trusted Sources:**
   - Add only specific IPs or resources needed
   - Remove old/unused sources immediately
   - Document purpose of each source (use notes in DO dashboard)

### ❌ DON'T:

1. **Never:**
   - Hardcode API tokens in code
   - Commit tokens to git
   - Share tokens via email/chat
   - Use tokens in URLs or logs
   - Create tokens without expiration

2. **Avoid:**
   - Overly broad IP ranges (use specific IPs)
   - Permanent tokens (use expiration)
   - Single token for all purposes (create separate tokens)
   - Leaving test IPs active in production

---

## Troubleshooting

### Error: "DIGITALOCEAN_API_TOKEN environment variable is required"

**Cause:** API token not set in environment

**Solution:**
```bash
# Check if token is set
echo $DIGITALOCEAN_API_TOKEN

# If empty, add to .env
echo "DIGITALOCEAN_API_TOKEN=dop_v1_your_token_here" >> .env

# Or export temporarily
export DIGITALOCEAN_API_TOKEN="dop_v1_your_token_here"
```

---

### Error: "Database with host ... not found"

**Cause:** DATABASE_HOST in .env doesn't match any database

**Solution:**
```bash
# Verify DATABASE_HOST
grep DATABASE_HOST .env

# Should match:
# db-postgresql-merlin-tor1-52568-do-user-27870072-0.e.db.ondigitalocean.com
```

---

### Error: "401 Unauthorized"

**Cause:** Invalid or expired API token

**Solution:**
1. Verify token is correct (copy/paste error)
2. Check token hasn't expired
3. Verify token has read/write permissions
4. Generate new token if needed

---

### Error: "Unable to determine current IP"

**Cause:** Network issue preventing IP detection

**Solution:**
```bash
# Manually find your IP
curl ifconfig.me

# Use Option 2 to add manually
```

---

### Connection Still Timing Out After Adding Trusted Source

**Causes & Solutions:**

1. **Firewall Propagation Delay:**
   - Wait 1-2 minutes after adding source
   - Retry connection test

2. **Wrong IP Address:**
   ```bash
   # Verify your public IP
   curl ifconfig.me

   # Compare with trusted source
   # Use Option 6 to view current rules
   ```

3. **Deployment Platform Uses Different IP:**
   - If deployed on cloud, get deployment server's IP
   - Don't use your local IP for production deployment

4. **App Platform Requires App ID:**
   - For App Platform deployments, use Option 3 (Add App)
   - Don't use IP address for App Platform apps

---

## Production Deployment Workflow

### For Digital Ocean App Platform:

1. **Get App ID:**
   - Navigate to your app in DO dashboard
   - Copy App ID from URL

2. **Run Script:**
   ```bash
   python configure_do_firewall.py
   ```

3. **Select Option 3:**
   - Add App Platform App
   - Enter App ID

4. **Deploy Application:**
   - Set environment variables in App Platform
   - Deploy from connected repository

5. **Verify:**
   - Test dashboard access
   - Check database connectivity

---

### For External Server/VPS:

1. **Get Server IP:**
   ```bash
   # From deployment server
   curl ifconfig.me
   ```

2. **Run Script:**
   ```bash
   python configure_do_firewall.py
   ```

3. **Select Option 2:**
   - Add specific IP address
   - Enter server IP

4. **Deploy Application:**
   - Set environment variables on server
   - Start application

5. **Test Connection:**
   ```bash
   python test_db_connection.py
   ```

---

## Security Checklist

- [ ] API token generated with 90-day expiration
- [ ] Token stored in `.env` (gitignored, not committed)
- [ ] Token has minimum required permissions (read + write)
- [ ] Trusted sources added (specific IPs or App IDs only)
- [ ] No overly broad IP ranges (avoid 0.0.0.0/0)
- [ ] Connection tested successfully
- [ ] Old/test sources removed
- [ ] Token documented in secure password manager
- [ ] Audit log reviewed for unauthorized access
- [ ] `.env` file permissions restricted (chmod 600)

---

## API Token Lifecycle Management

### Creation:
1. Generate with specific purpose
2. Set expiration (90 days)
3. Store in password manager
4. Document in secure location

### Usage:
1. Load from environment only
2. Never log or expose
3. Use HTTPS for all API calls
4. Monitor usage in DO dashboard

### Rotation:
1. Generate new token before expiration
2. Update `.env` file
3. Restart application
4. Revoke old token
5. Verify new token works

### Revocation:
1. Immediately revoke compromised tokens
2. Generate new token
3. Update all environments
4. Review audit logs for unauthorized access

---

## Files Created

- `configure_do_firewall.py` - Automated configuration script
- `test_db_connection.py` - Connection testing script
- `.env` - Environment variables (gitignored)
- `AUTOMATED_FIREWALL_SETUP.md` - This documentation

---

## Support

**Digital Ocean API Documentation:**
- API Reference: https://docs.digitalocean.com/reference/api/
- Database API: https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases
- Authentication: https://docs.digitalocean.com/reference/api/create-personal-access-token/

**Troubleshooting:**
- Digital Ocean Support: https://www.digitalocean.com/support
- Community: https://www.digitalocean.com/community

---

**Configuration Method:** Automated ✅
**Security Level:** Production-Ready 🔐
**Status:** Ready to Use 🚀
