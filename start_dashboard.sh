#!/bin/bash
# Dashboard V2 Startup Script
# Automatically configures and starts the dashboard with database connection

echo "🚀 Starting Dashboard V2..."
echo ""

# Set environment variables directly
export PGPASSWORD=goldmember
export DATABASE_NAME=local_Merlin_3
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_USER=postgres
export SESSION_SECRET=3acb64f5f137235ee7ba9e8c5c52004bb7c932d49d5ed7a9a288bcf082650312
export DATABASE_URL=postgresql://postgres:goldmember@localhost:5432/local_Merlin_3
export WEBHOOK_API_KEY=LKi7BfXjnqKYzR9uBARMcQucamcsiI_vGtxgL5353StnU2bUtJtjWeRAEyi9-adu

echo "✅ Environment variables configured"
echo "✅ Database: local_Merlin_3 at localhost:5432"
echo ""

# Test database connection
echo "🔍 Testing database connection..."
python3 << 'PYEOF'
from modules.database.database_client import DatabaseClient
from sqlalchemy import text
try:
    db = DatabaseClient()
    with db.get_session() as session:
        count = session.execute(text('SELECT COUNT(*) FROM jobs')).scalar()
        print(f'✅ Database connected! Found {count} jobs')
except Exception as e:
    print(f'❌ Database error: {e}')
    exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Database connection failed. Please check PostgreSQL is running."
    exit 1
fi

echo ""
echo "🌐 Starting Flask server..."
echo "📍 Dashboard will be available at: http://localhost:5001/dashboard"
echo "📍 Jobs view at: http://localhost:5001/dashboard/jobs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask
python3 app_modular.py
