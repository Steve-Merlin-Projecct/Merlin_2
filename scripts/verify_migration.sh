#!/bin/bash
# Verify database migration - compare local vs Digital Ocean

set -e

LOCAL_DB="postgresql://REPLACE_WITH_LOCAL_DB_CREDENTIALS"
REMOTE_DB="postgresql://REPLACE_WITH_REMOTE_DB_CREDENTIALS"

echo "🔍 Comparing Local vs Digital Ocean databases..."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Top 10 Tables by Row Count"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get counts from both databases and display side-by-side
psql "$LOCAL_DB" -t -A -F'|' -c "
SELECT relname, n_live_tup
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC
LIMIT 10;" > /tmp/local_counts.txt

psql "$REMOTE_DB" -t -A -F'|' -c "
SELECT relname, n_live_tup
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC
LIMIT 10;" > /tmp/remote_counts.txt

printf "%-30s %15s %15s %10s\n" "TABLE" "LOCAL" "REMOTE" "MATCH"
printf "%-30s %15s %15s %10s\n" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "━━━━━━━━━━━━━━━" "━━━━━━━━━━━━━━━" "━━━━━━━━━━"

while IFS='|' read -r table local_count; do
    remote_count=$(grep "^$table|" /tmp/remote_counts.txt | cut -d'|' -f2)
    if [ "$local_count" = "$remote_count" ]; then
        match="✅"
    else
        match="❌"
    fi
    printf "%-30s %15s %15s %10s\n" "$table" "$local_count" "${remote_count:-0}" "$match"
done < /tmp/local_counts.txt

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total Tables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LOCAL_TOTAL=$(psql "$LOCAL_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
REMOTE_TOTAL=$(psql "$REMOTE_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

printf "%-30s %15s %15s\n" "Total tables" "$LOCAL_TOTAL" "$REMOTE_TOTAL"

echo ""
if [ "$LOCAL_TOTAL" = "$REMOTE_TOTAL" ]; then
    echo "✅ Migration verification complete - all tables present!"
else
    echo "⚠️  Table count mismatch - review migration"
fi

# Cleanup
rm -f /tmp/local_counts.txt /tmp/remote_counts.txt
