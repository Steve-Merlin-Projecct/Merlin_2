import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Create storage directory if it doesn't exist
storage_dir = os.path.join(os.getcwd(), 'storage')
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)
    logging.info(f"Created storage directory: {storage_dir}")

# Import and register webhook routes
from webhook_handler import webhook_bp
app.register_blueprint(webhook_bp)

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint to verify service is running"""
    return {
        "status": "ok",
        "message": "Flask webhook service is running",
        "endpoints": {
            "webhook": "/webhook"
        }
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
