from app_modular import app
import os

# Make app accessible for deployment
# This allows both `main:app` and `app_modular:app` to work
if __name__ == '__main__':
    # Environment-aware configuration
    # Development: Uses port 5000 with debug enabled
    # Production: Uses $PORT environment variable with debug disabled
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
