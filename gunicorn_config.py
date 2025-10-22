"""
Gunicorn WSGI Server Configuration for Production

This configuration is optimized for Digital Ocean App Platform deployment
with appropriate worker counts, timeouts, and logging for production use.
"""

import os
import multiprocessing

# Server Socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5001')}"
backlog = 2048

# Worker Processes
# Digital Ocean Basic tier: 512MB RAM, 1 vCPU
# Professional tier: 1GB RAM, 1 vCPU
# Calculate workers based on available CPU cores (2-4 workers recommended)
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'  # Use 'gevent' or 'eventlet' for async if needed
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting simultaneously
timeout = 120  # Worker timeout (seconds) - increased for AI API calls
keepalive = 5  # Keep-alive connections (seconds)

# Process Naming
proc_name = 'merlin-job-application-system'

# Logging
accesslog = '-'  # Log to stdout (Digital Ocean captures this)
errorlog = '-'   # Log to stderr
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Enable logging of request details in JSON format if LOG_FORMAT=json
if os.environ.get('LOG_FORMAT') == 'json':
    logconfig_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'level': loglevel.upper(),
            'handlers': ['console']
        }
    }

# Server Mechanics
daemon = False  # Run in foreground (required for Docker)
pidfile = None  # Don't create PID file
user = None     # Run as container user
group = None
tmp_upload_dir = None

# SSL (Digital Ocean App Platform handles SSL termination)
# No need to configure SSL here

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Merlin Job Application System")
    server.log.info(f"Workers: {workers}, Timeout: {timeout}s")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Merlin Job Application System")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Merlin Job Application System ready to serve requests")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info(f"Worker received SIGABRT signal (pid: {worker.pid})")
