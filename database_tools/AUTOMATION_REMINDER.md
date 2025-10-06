# DATABASE SCHEMA AUTOMATION REMINDER

## IMPORTANT: Use Automated Tools Only

When making database schema changes, ALWAYS use the automated tools:

### Required Workflow:
1. Make schema changes to PostgreSQL database
2. Run: python database_tools/update_schema.py
3. Commit generated files to version control

### Automated Tools:
- `python database_tools/update_schema.py` - Manual update
- `python database_tools/schema_automation.py --check` - Check changes
- `python database_tools/schema_automation.py --force` - Force update
- `./update_database_schema.sh` - Shell wrapper

### DO NOT:
- Manually edit frontend_templates/database_schema.html
- Manually edit database_tools/docs/ files
- Manually edit database_tools/generated/ files
- Skip running automation after schema changes

### WHY:
- Ensures documentation accuracy
- Prevents inconsistencies
- Maintains code generation synchronization
- Preserves change detection system

For questions, see docs/SCHEMA_AUTOMATION.md