#!/bin/bash
# Migrate data only to Digital Ocean (schema already exists)

set -e

echo "🔄 Starting data migration..."

# Configuration
LOCAL_DB="postgresql://REPLACE_WITH_LOCAL_DB_CREDENTIALS"
REMOTE_DB="postgresql://REPLACE_WITH_REMOTE_DB_CREDENTIALS"
BACKUP_FILE="data_export_$(date +%Y%m%d_%H%M%S).sql"

# Step 1: Export data
echo "📤 Exporting data from local database..."
pg_dump "$LOCAL_DB" --data-only --no-owner --no-acl -f "$BACKUP_FILE"
echo "✅ Data exported to $BACKUP_FILE"

# Step 2: Import data
echo "📥 Importing data to Digital Ocean..."
psql "$REMOTE_DB" -f "$BACKUP_FILE"
echo "✅ Data imported successfully"

# Step 3: Verify counts
echo ""
echo "🔍 Verifying migration..."
echo "Local database counts:"
psql "$LOCAL_DB" -t -c "
SELECT
    schemaname || '.' || relname AS table_name,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC
LIMIT 10;"

echo ""
echo "Remote database counts:"
psql "$REMOTE_DB" -t -c "
SELECT
    schemaname || '.' || relname AS table_name,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC
LIMIT 10;"

echo ""
echo "✅ Data migration complete!"
echo "📁 Backup saved: $BACKUP_FILE"
