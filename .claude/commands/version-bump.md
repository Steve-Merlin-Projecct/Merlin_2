---
description: Bump project version (minor/mid/major)
parameters:
  - name: type
    description: Version bump type (minor, mid, or major)
    required: true
---

Bump the project version and sync to all files.

Usage examples:
- /version-bump minor  (4.0.1 -> 4.0.2) - increments patch
- /version-bump mid    (4.0.1 -> 4.1.0) - increments minor
- /version-bump major  (4.0.1 -> 5.0.0) - increments major

python tools/version_manager.py --bump {{type}} && python tools/version_manager.py --sync
