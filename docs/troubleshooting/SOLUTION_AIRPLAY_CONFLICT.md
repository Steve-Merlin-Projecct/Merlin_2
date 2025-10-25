---
title: "Solution Airplay Conflict"
type: technical_doc
component: general
status: draft
tags: []
---

# SOLVED: 403 Error was AirPlay/AirTunes Conflict

## The Problem
- You were getting 403 Forbidden on http://localhost:5000/dashboard
- The error persisted despite Flask running correctly

## Root Cause Discovery
From the browser's Network tab, the response header revealed:
```
server: AirTunes/760.20.1
```

**Port 5000 is the default port for Apple's AirPlay Receiver service on macOS!**

## The Solution
Changed Flask to run on **port 5001** instead of 5000.

## Working Dashboard URL

### ✅ http://localhost:5001/dashboard

## Why This Happened
- macOS uses port 5000 for AirPlay Receiver (AirTunes)
- When you tried to access localhost:5000, macOS's AirPlay service intercepted the request
- AirPlay returned 403 Forbidden because it's not a web service
- Flask was actually working fine, but you never reached it

## Lessons Learned
1. Always check the `Server` header when debugging HTTP errors
2. Port 5000 conflicts with AirPlay on macOS (common issue for Flask developers)
3. The 403 wasn't from Flask or Docker - it was from a system service

## Alternative Solutions
If you prefer port 5000, you can:
1. Disable AirPlay Receiver: System Preferences → Sharing → uncheck AirPlay Receiver
2. Or continue using port 5001 (recommended)

## To Start Flask
```bash
python3 start_flask_fixed.py
```

Flask is configured to:
- Run on port 5001
- Connect to PostgreSQL via host.docker.internal
- Skip authentication for local development
- Serve the dashboard with materialized views for fast performance