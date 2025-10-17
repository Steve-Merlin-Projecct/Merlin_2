# Git Orchestrator Agent: Error Logging System

## Error Logging Specification

### Log Helpers

```python
def log_error(operation, context, message, suggested_action=None):
    """
    Log critical errors that prevent operation completion.
    
    Args:
        operation (str): Type of git operation (checkpoint, section_commit, user_commit)
        context (dict): Contextual information about the operation
        message (str): Detailed error description
        suggested_action (str, optional): Recommended resolution steps
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "ERROR",
        "operation": operation,
        "context": context,
        "message": message,
        "suggested_action": suggested_action or "No specific action suggested"
    }
    _write_log(log_entry)

def log_warning(operation, context, message, suggested_action=None):
    """
    Log non-blocking issues that require attention.
    
    Args:
        operation (str): Type of git operation
        context (dict): Contextual information about the operation
        message (str): Detailed warning description
        suggested_action (str, optional): Recommended resolution steps
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "WARNING",
        "operation": operation,
        "context": context,
        "message": message,
        "suggested_action": suggested_action or "Monitor and address when convenient"
    }
    _write_log(log_entry)

def _write_log(log_entry):
    """
    Write log entry to rotating log file.
    
    Args:
        log_entry (dict): Structured log entry to write
    """
    log_file = _get_current_log_file()
    with open(log_file, 'a') as f:
        json.dump(log_entry, f)
        f.write('\n')
```

### Logging Guidelines

1. **When to Log Errors**
   - Git command failures
   - Test suite failures
   - Pre-commit hook rejections
   - Schema automation errors
   - Documentation validation failures

2. **When to Log Warnings**
   - Partial test failures
   - Missing documentation
   - Incomplete section tasks
   - Push failures to remote

3. **Do NOT Log**
   - Successful operations
   - Cancelled user actions
   - Skipped commits with no changes
   - Redundant or duplicate information

4. **Privacy and Security**
   - Never log sensitive information (passwords, tokens)
   - Mask or remove potential PII
   - Use safe context extraction
   - Ensure log files are in .gitignore

## Implementation Notes

- Logs rotate daily
- Maximum log retention: 30 days
- Use JSON for structured logging
- Implement log rotation mechanism
- Separate log files by month
