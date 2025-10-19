#!/usr/bin/env python3
"""
Start Flask with proper database configuration for Docker environment
"""

import os
import sys

# Set environment variables BEFORE importing Flask app
os.environ['DATABASE_HOST'] = 'host.docker.internal'
os.environ['DATABASE_PORT'] = '5432'
os.environ['DATABASE_NAME'] = 'local_Merlin_3'
os.environ['DATABASE_USER'] = 'postgres'
os.environ['DATABASE_PASSWORD'] = 'goldmember'
os.environ['PGPASSWORD'] = 'goldmember'

# Set other required environment variables to avoid warnings
os.environ['SESSION_SECRET'] = 'development-secret-key-' + os.urandom(16).hex()
os.environ['WEBHOOK_API_KEY'] = 'development-key-' + os.urandom(16).hex()

# Set Flask to run in debug mode
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

print("=" * 60)
print("Starting Flask with fixed database configuration")
print("=" * 60)
print(f"DATABASE_HOST: {os.environ.get('DATABASE_HOST')}")
print(f"DATABASE_PORT: {os.environ.get('DATABASE_PORT')}")
print(f"DATABASE_NAME: {os.environ.get('DATABASE_NAME')}")
print(f"FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")
print("=" * 60)

# Import and run the Flask app
from app_modular import app

if __name__ == '__main__':
    print("\nStarting Flask application...")
    print("Dashboard will be available at: http://localhost:5001/dashboard")
    print("(Using port 5001 to avoid AirPlay conflict on macOS)")
    print("=" * 60)

    # Run Flask app - Using port 5001 to avoid AirPlay conflict on macOS
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5001,  # Changed from 5000 to avoid AirPlay/AirTunes conflict
        debug=True,
        use_reloader=False  # Disable reloader to avoid double starts
    )