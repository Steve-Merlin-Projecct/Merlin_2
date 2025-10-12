#!/usr/bin/env python3
"""
Standalone Dashboard Server - No Database Required
Just for viewing the beautiful UI with mock data
"""

from flask import Flask, render_template, jsonify, session, request, redirect
from datetime import datetime
from functools import wraps

app = Flask(__name__, template_folder='frontend_templates')
app.secret_key = 'dashboard_demo_secret_key_12345'

def require_page_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
def dashboard():
    """Dashboard with login"""
    if not session.get('authenticated'):
        return render_template('dashboard_login.html')
    return render_template('dashboard_v2.html')

@app.route('/dashboard/jobs')
@require_page_auth
def dashboard_jobs():
    """Jobs listing page"""
    return render_template('dashboard_jobs.html')

@app.route('/dashboard/applications')
@require_page_auth
def dashboard_applications():
    """Applications page (placeholder)"""
    return '<h1>Applications View - Coming Soon</h1><a href="/dashboard">Back to Dashboard</a>'

@app.route('/dashboard/analytics')
@require_page_auth
def dashboard_analytics():
    """Analytics page (placeholder)"""
    return '<h1>Analytics View - Coming Soon</h1><a href="/dashboard">Back to Dashboard</a>'

@app.route('/dashboard/authenticate', methods=['POST'])
def dashboard_authenticate():
    """Simple auth - password is 'demo'"""
    import hashlib
    password = request.json.get('password', '')

    # Accept "demo" as password for this standalone version
    if password == 'demo':
        session['authenticated'] = True
        session['auth_time'] = datetime.now().timestamp()
        return jsonify({'success': True, 'message': 'Authentication successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid password (hint: try "demo")'}), 401

@app.route('/api/v2/dashboard/overview', methods=['GET'])
def get_dashboard_overview():
    """Mock dashboard data"""
    return jsonify({
        "success": True,
        "metrics": {
            "scrapes": {
                "24h": 23,
                "7d": 156,
                "trend_24h": 15.2,
                "trend_7d": 12.8
            },
            "analyzed": {
                "24h": 18,
                "7d": 142,
                "trend_24h": 12.5
            },
            "applications": {
                "24h": 7,
                "7d": 45,
                "trend_24h": 18.3
            },
            "success_rate": {
                "current": 87.5,
                "7d_sent": 42,
                "7d_total": 48
            },
            "total_jobs": 1342
        },
        "pipeline": {
            "stages": [
                {"id": "raw", "name": "Raw Scrapes", "count": 287, "status": "active"},
                {"id": "cleaned", "name": "Cleaned", "count": 234, "status": "active"},
                {"id": "analyzed", "name": "Analyzed", "count": 198, "status": "active"},
                {"id": "eligible", "name": "Eligible", "count": 52, "status": "active"},
                {"id": "applied", "name": "Applied", "count": 45, "status": "active"}
            ],
            "conversion_rate": 15.7,
            "bottleneck": "eligible"
        },
        "recent_applications": [
            {
                "id": "app_001",
                "job_title": "Senior Full Stack Developer",
                "company_name": "TechCorp Inc",
                "status": "sent",
                "created_at": "2025-10-09T14:30:00",
                "documents": ["resume", "cover_letter"],
                "coherence_score": 0.92
            },
            {
                "id": "app_002",
                "job_title": "Python Backend Engineer",
                "company_name": "DataFlow Systems",
                "status": "sent",
                "created_at": "2025-10-09T13:15:00",
                "documents": ["resume", "cover_letter"],
                "coherence_score": 0.88
            },
            {
                "id": "app_003",
                "job_title": "AI/ML Software Engineer",
                "company_name": "Neural Networks Ltd",
                "status": "sent",
                "created_at": "2025-10-09T11:45:00",
                "documents": ["resume", "cover_letter", "portfolio"],
                "coherence_score": 0.95
            },
            {
                "id": "app_004",
                "job_title": "DevOps Engineer",
                "company_name": "CloudScale",
                "status": "pending",
                "created_at": "2025-10-09T10:20:00",
                "documents": ["resume"],
                "coherence_score": 0.85
            },
            {
                "id": "app_005",
                "job_title": "Staff Software Engineer",
                "company_name": "Innovation Hub",
                "status": "sent",
                "created_at": "2025-10-09T09:00:00",
                "documents": ["resume", "cover_letter"],
                "coherence_score": 0.91
            }
        ],
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "query_version": "v2_mock_data"
        }
    })

@app.route('/api/stream/dashboard')
def dashboard_stream():
    """Mock SSE stream"""
    from flask import Response, stream_with_context
    import json
    import time

    def generate():
        # Send connection event
        yield f"event: connected\ndata: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

        # Send heartbeat every 30 seconds
        while True:
            time.sleep(30)
            yield f"event: heartbeat\ndata: {json.dumps({'timestamp': datetime.utcnow().isoformat()})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Dashboard Standalone (Mock Data)',
        'version': '2.0.0-demo'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Dashboard Standalone Server Starting...")
    print("=" * 60)
    print()
    print("📊 Dashboard URL: http://localhost:5001/dashboard")
    print("🔑 Password: demo")
    print()
    print("Note: This is a standalone demo with mock data")
    print("=" * 60)
    print()
    app.run(debug=True, host='0.0.0.0', port=5001)
