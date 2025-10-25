---
title: "Replit Migration Readme"
type: technical_doc
component: general
status: draft
tags: []
---

# Archived Replit-Specific Files

**Archive Date:** October 6, 2025
**Reason:** Replit Platform Migration

## Overview

This directory contains archived Python files that were created during the Replit development phase of the Merlin Job Application System. These files contain obsolete Replit Object Storage code and are kept for historical reference only.

## Important Notice

⚠️ **These files are NOT used in the current application.**

The codebase has been migrated away from Replit-specific dependencies. All active production code now uses the new storage abstraction layer located in `modules/storage/`.

## Archived Files

### Webhook Handlers
- `webhook_handler.py` - Original webhook handler with Replit storage
- `webhook_handler_2.py` - Second iteration
- `webhook_handler_original.py` - Initial implementation

### Document Generators
- `resume_generator2.py` - Resume generator with Replit storage
- `resume_generator_original.py` - Original resume generator
- `base_generator.py` - Base document generator class
- `makecom-document-generator.py` - Make.com integration version

## Migration Details

**Migration Completed:** October 6, 2025

**What Changed:**
- Removed `from replit.object_storage import Client`
- Replaced with `from modules.storage import get_storage_backend`
- Updated all storage operations to use new abstraction layer

**Active Production Files:**
- `modules/content/document_generation/document_generator.py`
- `modules/document_routes.py`
- `modules/storage/` (new storage abstraction layer)

## Why Keep These Files?

These files are preserved for:
1. Historical reference
2. Understanding evolution of the codebase
3. Potential code pattern reference
4. Migration documentation

## Replit Object Storage References

All files in this directory contain references to:
```python
from replit.object_storage import Client

storage_client = Client()
storage_client.upload(object_key, file_content)
file_data = storage_client.get(filename)
```

**Do not use these patterns in new code!** Use the storage abstraction layer instead:
```python
from modules.storage import get_storage_backend

storage = get_storage_backend()
storage.save(filename, content)
file_data = storage.get(filename)
```

## Documentation

For current storage implementation, see:
- `docs/storage-architecture.md` - Storage system documentation
- `modules/storage/README.md` - Storage module documentation
- `CLAUDE.md` - Updated system architecture

## Questions?

If you need to reference historical Replit implementation details, these files provide that context. However, for all new development, use the current storage abstraction layer.

---

**Migration Version:** 4.1
**Last Updated:** October 6, 2025
