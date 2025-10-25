---
title: "Readme"
type: technical_doc
component: general
status: draft
tags: []
---

# Digital Ocean Deployment Files

## 📁 Files in This Directory

### 🚀 **Start Here**
- **`DIGITAL_OCEAN_SETUP.md`** - Complete step-by-step deployment guide
- **`MINIMAL_VARIABLES.txt`** - Just 4 variables to get started quickly

### 📋 **Environment Variables**
- **`DIGITAL_OCEAN_VARIABLES.txt`** - All 14 variables formatted for copy-paste
- **`variables.csv`** - CSV format (if Digital Ocean supports bulk import)
- **`.env`** - Full configuration file (for reference/local development only)

### 📖 **Which File Should I Use?**

#### Option 1: Quick Deploy (5 minutes)
1. Open **`MINIMAL_VARIABLES.txt`**
2. Add only 4 variables to Digital Ocean
3. Deploy and verify it works
4. Add remaining variables later

#### Option 2: Full Deploy (15 minutes)
1. Open **`DIGITAL_OCEAN_VARIABLES.txt`**
2. Add all 14 variables to Digital Ocean
3. Deploy with all features enabled

#### Option 3: Reference the .env
1. Open **`.env`** file
2. Use it as reference for understanding what each variable does
3. Add variables manually to Digital Ocean from this file

---

## 🔧 How to Add Variables to Digital Ocean

1. Go to: **Digital Ocean** → **merlin-2 app** → **Settings**
2. Click: **"Edit"** next to "Environment variables"
3. For each variable:
   - Click **"Add Variable"**
   - Copy **Key** from the file
   - Copy **Value** from the file
   - Paste into Digital Ocean form
4. Click: **"Save"**
5. Digital Ocean will automatically redeploy

---

## 📊 Variable Summary

| Category | Count | Required? | File Reference |
|----------|-------|-----------|----------------|
| Core Requirements | 4 | ✅ Yes | MINIMAL_VARIABLES.txt |
| Observability (v4.5.0) | 6 | ⚠️ Recommended | Lines 42-58 |
| AI & Scraping | 4 | ⚠️ If using features | Lines 60-72 |
| **Total Minimum** | **14** | - | DIGITAL_OCEAN_VARIABLES.txt |

---

## 🔐 Security Notes

**⚠️ IMPORTANT:**
- These files contain **sensitive credentials**
- **NEVER** commit these files to version control
- **NEVER** share these files publicly
- Store API keys in a password manager
- Rotate keys every 90 days

**Keys in these files:**
- Database password (in DATABASE_URL)
- SECRET_KEY (Flask session security)
- WEBHOOK_API_KEY (API authentication)
- GEMINI_API_KEY (Google AI access)
- APIFY_API_TOKEN (Web scraping access)

---

## ✅ After Adding Variables

1. **Save** in Digital Ocean
2. **Wait** 2-3 minutes for deployment
3. **Test** health endpoint:
   ```
   https://merlin-2-xxxxx.ondigitalocean.app/health
   ```
4. Expected response:
   ```json
   {
     "status": "healthy",
     "version": "4.5.0"
   }
   ```

---

## 🆘 Troubleshooting

### App shows "Unhealthy" or "Failed"
1. Check **Runtime Logs** in Digital Ocean
2. Look for missing environment variable errors
3. Verify all 4 required variables are set correctly

### Database connection errors
1. Verify DATABASE_URL is one continuous line (no line breaks)
2. Check that `?sslmode=require` is at the end
3. Verify database is running in Digital Ocean

### Need Help?
- See: `DIGITAL_OCEAN_SETUP.md` (full troubleshooting guide)
- Check: Digital Ocean Runtime Logs for specific errors

---

## 🎯 Quick Reference

**Minimum to deploy:** 4 variables (MINIMAL_VARIABLES.txt)
**Recommended:** 14 variables (DIGITAL_OCEAN_VARIABLES.txt)
**Time to add:** 5-15 minutes
**Deployment time:** 2-3 minutes after saving

**Next:** After deployment succeeds, see `DIGITAL_OCEAN_SETUP.md` for testing instructions.
