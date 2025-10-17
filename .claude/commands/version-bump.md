---
description: Bump project version (patch/minor/major)
argument-hint: patch | minor | major
parameters:
  - name: type
    description: Version bump type (patch, minor, or major)
    required: true
---

Bump the project version and sync to all files.

Usage examples:
- /version-bump patch  (4.0.1 -> 4.0.2)
- /version-bump minor  (4.0.1 -> 4.1.0)
- /version-bump major  (4.0.1 -> 5.0.0)

python tools/version_manager.py --bump {{type}} && python tools/version_manager.py --sync
