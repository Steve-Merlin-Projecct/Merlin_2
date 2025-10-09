import os
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, jsonify, render_template, request, session, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
# Webhook handlers moved to archived_files/ - no longer using Make.com integration
# from modules.webhook_handler import webhook_bp
from modules.database.database_api import database_bp
from modules.content.job_system_routes import job_system_bp
from modules.dashboard_api import dashboard_api, require_dashboard_auth
from modules.ai_job_description_analysis.ai_integration_routes import ai_bp
from modules.integration.integration_api import integration_bp
from modules.ai_job_description_analysis.batch_integration_api import batch_ai_bp
from modules.scheduling.workflow_api import workflow_api
from modules.email_integration.email_api import email_api
from modules.scraping.scraper_api import scraper_bp
from modules.document_routes import document_bp
from modules.user_management.user_profile_api import user_profile_bp
from modules.workflow.email_application_api import email_application_api
from modules.workflow.workflow_api import workflow_api as step_2_2_workflow_api
from modules.security.security_patch import apply_security_headers, validate_environment, SecurityPatch

# Set up logging
__version__ = "4.2.0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, template_folder='frontend_templates')

# Validate environment and apply security settings
validate_environment()

# Check for weak secrets and warn
security_check = SecurityPatch.check_weak_secrets()
if security_check['weak_secrets']:
    logger.warning(f"Security audit found weak secrets. Please update them using utils/security_key_generator.py")

# Set secure session key
session_secret = os.environ.get("SESSION_SECRET")
if not session_secret or len(session_secret) < 32:
    session_secret = SecurityPatch.create_secure_session_key()
    logger.warning("Generated temporary session key - set SESSION_SECRET environment variable")

app.secret_key = session_secret

# Configure request size limit
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Configure proxy middleware for deployment
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Register blueprints
# Webhook blueprint registration disabled - no longer using Make.com
# app.register_blueprint(webhook_bp)
app.register_blueprint(database_bp)
app.register_blueprint(job_system_bp)
app.register_blueprint(dashboard_api)
app.register_blueprint(ai_bp)
app.register_blueprint(integration_bp)
app.register_blueprint(batch_ai_bp)
app.register_blueprint(workflow_api)

# Register new workflow API for redesigned pipeline
try:
    from modules.database.workflow_api import workflow_api as new_workflow_api
    app.register_blueprint(new_workflow_api, name='new_workflow')
    logger.info("New workflow API registered successfully")
except ImportError as e:
    logger.warning(f"Could not register new workflow API: {e}")
app.register_blueprint(email_api)
app.register_blueprint(scraper_bp)
app.register_blueprint(document_bp)
app.register_blueprint(user_profile_bp)

# Register Step 2.2 Workflow API - End-to-End Application Orchestration
app.register_blueprint(step_2_2_workflow_api, name='step_2_2_workflow')

# Register Email Application API
app.register_blueprint(email_application_api)

# Register Link Tracking API
try:
    from modules.link_tracking.link_tracking_api import link_tracking_api_bp
    app.register_blueprint(link_tracking_api_bp)
    logger.info("Link Tracking API registered successfully")
except ImportError as e:
    logger.warning(f"Could not register Link Tracking API: {e}")

# Register Copywriting Evaluator API
try:
    from modules.content.copywriting_evaluator.copywriting_evaluator_api import copywriting_evaluator_bp
    app.register_blueprint(copywriting_evaluator_bp)
    logger.info("Copywriting Evaluator API registered successfully")
except ImportError as e:
    logger.warning(f"Could not register Copywriting Evaluator API: {e}")

# Register Analytics API
try:
    from modules.analytics.engagement_analytics_api import engagement_analytics_bp
    app.register_blueprint(engagement_analytics_bp)
    logger.info("Analytics API registered successfully")
except ImportError as e:
    logger.warning(f"Could not register Analytics API: {e}")

# Document Generation API is already registered above via document_bp from modules.document_routes
logger.info("Document Generation API already registered via document_bp")

# The user_profile_bp is already registered above 
logger.info("User Profile API already registered via user_profile_bp")

# Create storage directory if it doesn't exist
os.makedirs("storage", exist_ok=True)

@app.route('/')
def index():
    """Root endpoint with service information"""
    return jsonify({
        'service': 'Document Generation Service',
        'version': '2.1.3',
        'status': 'running',
        'modules': [
            'Resume Generator',
            'Cover Letter Generator',
            'AI Job Analysis with Prestige Factors',
            'Gmail OAuth Integration',
            'Workflow Scheduling'
        ],
        'endpoints': {
            'resume': '/resume - POST: Generate structured resume',
            'cover_letter': '/cover-letter - POST: Generate cover letter',
            'download': '/download/<filename> - GET: Download generated file',
            'debug': '/debug/download/<filename> - GET: Debug file information',
            'test': '/test - GET/POST: Test endpoint',
            'health': '/health - GET: Health check'
        },
        'database_api': {
            'jobs': '/api/db/jobs - GET: List jobs with filtering',
            'job_detail': '/api/db/jobs/<id> - GET: Get specific job',
            'statistics': '/api/db/statistics - GET: Job statistics',
            'settings': '/api/db/settings - GET: Application settings',
            'db_health': '/api/db/health - GET: Database health check'
        },
        'job_system': {
            'demo': '/demo - GET: Job application system demonstration',
            'workflow': '/job-system/run-workflow - POST: Run complete workflow',
            'stats': '/job-system/stats - GET: System statistics',
            'tracking': '/track/<id> - GET: Link tracking and redirect'
        },
        'workflow_api': {
            'status': '/api/workflow/status - GET: Current workflow scheduling status',
            'next_phase': '/api/workflow/next-phase - GET: Next scheduled workflow phase',
            'schedule_summary': '/api/workflow/schedule-summary - GET: Complete workflow schedule'
        },
        'email_api': {
            'oauth_status': '/api/email/oauth/status - GET: Gmail OAuth authentication status',
            'setup_guide': '/api/email/setup-guide - GET: Complete Gmail OAuth setup instructions',
            'test_email': '/api/email/test - POST: Send test email to verify integration',
            'send_application': '/api/email/send-job-application - POST: Send job application with attachments'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint to verify service is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'Merlin Job Application System',
        'version': __version__
    })

# Apply security headers to all responses
@app.after_request
def add_security_headers(response):
    return apply_security_headers(response)

@app.route('/dashboard')
def dashboard():
    """Personal job application dashboard for Steve Glen"""
    # Check if user is authenticated via session
    if not session.get('authenticated'):
        return render_template('dashboard_login.html')
    return render_template('dashboard_enhanced.html')

@app.route('/dashboard/authenticate', methods=['POST'])
def dashboard_authenticate():
    """Handle dashboard authentication"""
    import hashlib
    
    password = request.json.get('password', '')
    expected_hash = '008b6a04a1580494b58c1241e0b56ea683360c64f102160c17fbb8b013c07d8a'
    
    # Hash the provided password with salt
    password_hash = hashlib.sha256((password + 'steve-salt-2025').encode()).hexdigest()
    
    if password_hash == expected_hash:
        session['authenticated'] = True
        session['auth_time'] = datetime.now().timestamp()
        return jsonify({'success': True, 'message': 'Authentication successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid password'}), 401

@app.route('/test-access')
def test_access():
    """Browser access test page"""
    return open('test_browser_access.html').read()

@app.route('/dashboard/logout', methods=['POST'])
def dashboard_logout():
    """Handle dashboard logout"""
    session.pop('authenticated', None)
    session.pop('auth_time', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

def require_page_auth(f):
    """Decorator to require authentication for page routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/workflow')
@require_page_auth
def workflow_visualization():
    """Workflow visualization showing information flow and decision factors"""
    return render_template('workflow_visualization.html')

@app.route('/database-schema')
@require_page_auth
def database_schema():
    """Database schema visualization showing table relationships"""
    return render_template('database_schema.html')

@app.route('/demo')
@require_page_auth
def demo():
    """Job application system demonstration interface"""
    return render_template('job_system_demo.html')

@app.route('/tone-analysis')
@require_page_auth
def tone_analysis():
    """Tone analysis and formula logic display page"""
    return render_template('tone_analysis.html')

@app.route('/preferences')
@require_page_auth
def preferences():
    """User job preferences configuration page with 8 scenarios"""
    return render_template('preferences.html')

@app.route('/copywriting-evaluator-dashboard')
@require_page_auth
def copywriting_evaluator_dashboard():
    """Copywriting evaluator dashboard"""
    return render_template('copywriting_evaluator_dashboard.html')

@app.route('/job-override')
@require_page_auth
def job_override():
    """Manual job override page for post-interview adjustments"""
    return render_template('job_override.html')

@app.route('/api/process-scrapes', methods=['POST'])
@require_dashboard_auth
def process_scrapes():
    """Process raw scrapes into cleaned, deduplicated records"""
    try:
        from modules.scraping.scrape_pipeline import ScrapeDataPipeline
        
        data = request.get_json() or {}
        batch_size = data.get('batch_size', 100)
        
        pipeline = ScrapeDataPipeline()
        results = pipeline.process_raw_scrapes_to_cleaned(batch_size)
        
        return jsonify({
            'success': True,
            'message': 'Scrape processing completed',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing scrapes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/pipeline-stats')
@require_dashboard_auth
def pipeline_stats():
    """Get scraping pipeline statistics"""
    try:
        from modules.scraping.scrape_pipeline import ScrapeDataPipeline
        
        pipeline = ScrapeDataPipeline()
        stats = pipeline.get_pipeline_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting pipeline stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/intelligent-scrape', methods=['POST'])
@require_dashboard_auth
def intelligent_scrape():
    """
    Trigger intelligent job scraping based on user preference packages
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'steve_glen')
        max_jobs_per_package = data.get('max_jobs_per_package', 30)
        
        from modules.scraping.intelligent_scraper import IntelligentScraper
        # TODO: Add initialize_steve_glen_preferences import
        
        # Initialize preferences if needed
        initialize_steve_glen_preferences()
        
        # Run intelligent scrape
        scraper = IntelligentScraper()
        results = scraper.run_targeted_scrape(user_id, max_jobs_per_package)
        
        return jsonify({
            'success': True,
            'message': f'Intelligent scrape completed for {user_id}',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in intelligent scrape: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/preference-packages/<user_id>', methods=['GET'])
@require_dashboard_auth
def get_preference_packages(user_id):
    """
    Get user's preference packages and their performance
    """
    try:
        from modules.preference_packages import PreferencePackages
        from modules.scraping.intelligent_scraper import IntelligentScraper
        
        pp = PreferencePackages()
        scraper = IntelligentScraper()
        
        # Get search configurations (which include package details)
        search_configs = pp.get_targeted_search_configs(user_id)
        
        # Get performance metrics
        performance = scraper.get_package_performance(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'packages': search_configs,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f"Error getting preference packages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Blueprints already registered above

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)