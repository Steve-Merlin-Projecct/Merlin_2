from app_modular import app

# Make app accessible for deployment
# This allows both `main:app` and `app_modular:app` to work
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
