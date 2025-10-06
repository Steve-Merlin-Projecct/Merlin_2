#!/bin/bash
# Convenient wrapper script to update database schema HTML

echo "📊 Updating database schema..."
python database_tools/update_schema.py 2>/dev/null | grep -E "(✓|❌|Error|Found)" | head -3

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Schema updated"
else
    echo "❌ Schema update failed"
    exit 1
fi