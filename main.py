import os
from app_modular import app

if __name__ == '__main__':
    # Detect runtime environment
    is_production = os.getenv('FLASK_ENV', 'development') == 'production'
    
    # Set default port based on environment
    port = int(os.getenv('PORT', 5000 if not is_production else 8000))
    
    # Configure debug mode
    debug = not is_production
    
    # Configure host (use 0.0.0.0 in production for container/load balancer)
    host = '0.0.0.0' if is_production else '127.0.0.1'
    
    # Add /health endpoint to app_modular.py before running
    @app.route('/health')
    def health_check():
        return 'OK', 200
    
    app.run(host=host, port=port, debug=debug)
