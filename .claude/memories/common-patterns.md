---
title: "Common Patterns"
type: technical_doc
component: general
status: draft
tags: []
---

# Common Code Patterns Memory

## Code Style Standards
- **Formatter**: Black (line length: 120)
- **Linter**: Flake8
- **Dead Code**: Vulture (min confidence: 80)

## Python Patterns

### Module Organization
```python
# Standard import order
import os
import sys
from datetime import datetime

# Third-party imports
from flask import Blueprint, request, jsonify
import sqlalchemy

# Local imports
from modules.database import get_db_session
from modules.storage import get_storage_client
```

### Error Handling
```python
try:
    result = risky_operation()
    logging.info(f"✅ Operation succeeded: {result}")
except SpecificError as e:
    logging.error(f"❌ Operation failed: {e}")
    raise
except Exception as e:
    logging.error(f"❌ Unexpected error: {e}")
    return {"error": str(e), "success": False}
```

### Database Operations
```python
# Always use sessions properly
session = get_db_session()
try:
    record = session.query(Model).filter_by(id=id).first()
    session.commit()
finally:
    session.close()
```

### Storage Operations
```python
# Use storage abstraction
from modules.storage import get_storage_client

storage = get_storage_client()
storage.save("filename.txt", content_bytes)
content = storage.get("filename.txt")
```

## Flask Route Patterns
```python
@blueprint.route("/endpoint", methods=["POST"])
def endpoint_handler():
    """
    Endpoint description

    Expected JSON: {...}
    Returns: {...}
    """
    # Validate request
    if not request.json:
        return jsonify({"error": "No data provided"}), 400

    # Process
    try:
        result = process_data(request.json)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## Documentation Patterns

### Docstrings
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of what this function does.

    Longer explanation if needed, describing:
    - Key features
    - Important behaviors
    - Side effects

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        dict: Description of return value

    Raises:
        ValueError: When param1 is invalid
    """
    pass
```

## Testing Patterns
```python
def test_feature():
    """Test description"""
    # Arrange
    test_data = {...}

    # Act
    result = function_under_test(test_data)

    # Assert
    assert result["success"] is True
    assert "expected_key" in result
```

## Commands to Remember
```bash
# Format code before committing
make format

# Run quality checks
make lint

# Run tests
make test

# Update database schema
make db-update
```
