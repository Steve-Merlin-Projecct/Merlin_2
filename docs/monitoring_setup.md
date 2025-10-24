---
title: "Monitoring Setup"
type: technical_doc
component: general
status: draft
tags: []
---

# replit.md Change Monitoring System

## Overview

The monitoring system tracks every character-level change made to `replit.md` and logs detailed information about who made the changes and when.

## Components

1. **Monitor Script**: `tools/monitor_replit_md.py` - Main monitoring script
2. **Setup Script**: `tools/setup_replit_monitoring.sh` - Initialization helper
3. **Change Log**: `docs/changelogs/replit-md_changelog.md` - Detailed change history
4. **Hash Storage**: `docs/changelogs/.replit_md_hash` - File integrity tracking

## Features

- **Character-level diff detection** - Shows exact additions/deletions
- **Git integration** - Identifies commit info and authors
- **Entity tracking** - Distinguishes between user edits and agent changes
- **Timestamp logging** - UTC timestamps for all changes
- **File integrity** - SHA256 hash verification
- **Continuous monitoring** - Optional watch mode

## Usage

### Initialize Monitoring
```bash
python3 tools/monitor_replit_md.py init
```

### Check for Changes (One-time)
```bash
python3 tools/monitor_replit_md.py check
```

### Continuous Monitoring
```bash
python3 tools/monitor_replit_md.py watch
```

## Change Log Format

Each change entry includes:

```
==========================================
CHANGE DETECTED: 2025-08-07 12:30:45 UTC
==========================================
Entity: replit-agent
Type: active_edit
Commit: pending
Timestamp: 2025-08-07T12:30:45.123456

CHARACTER CHANGES:
15 characters added, 3 characters removed

DETAILED CHANGES:
  • Line 10: Added 'new content here'
  • Line 15: Removed 'old text'

FILE HASH:
Previous: a1b2c3d4e5f6...
Current:  f6e5d4c3b2a1...
```

## Integration with Automation

Add to your workflow scripts:
```bash
# Check for changes after any replit.md modification
python3 tools/monitor_replit_md.py check
```

## Security Features

- Detects unauthorized changes to protected sections
- Logs all modifications with entity attribution
- Maintains file integrity verification
- Works with git history for comprehensive tracking

## Status

✅ System initialized and operational  
✅ File change detection working  
✅ Character-level diff analysis functional  
✅ Git integration active  
✅ Hash-based integrity checking enabled