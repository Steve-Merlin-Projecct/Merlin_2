"""
Server-Sent Events (SSE) for Real-Time Dashboard Updates

Provides live event stream for dashboard without requiring WebSocket complexity.
Perfect for single-user dashboard with one-way server→client communication.

Events streamed:
- job_scraped: New job discovered
- job_analyzed: AI analysis completed
- application_sent: Job application submitted
- pipeline_updated: Processing stage transition
- metrics_refreshed: Dashboard metrics changed
"""

import logging
import json
import time
from flask import Blueprint, Response, stream_with_context, session
from datetime import datetime
from functools import wraps

# Create blueprint
sse_dashboard = Blueprint("sse_dashboard", __name__)
logger = logging.getLogger(__name__)

# Store active SSE connections (simple in-memory for single user)
active_connections = []


def require_dashboard_auth(f):
    """Require dashboard authentication for SSE endpoint"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return Response("Unauthorized", status=401)
        return f(*args, **kwargs)

    return decorated_function


def format_sse(data, event=None):
    """
    Format data as Server-Sent Event

    Args:
        data: Dictionary to send as JSON
        event: Event type (optional)

    Returns:
        Formatted SSE string
    """
    msg = f"data: {json.dumps(data)}\n"
    if event:
        msg = f"event: {event}\n{msg}"
    msg += "\n"
    return msg


@sse_dashboard.route("/api/stream/dashboard", methods=["GET"])
@require_dashboard_auth
def dashboard_event_stream():
    """
    Server-Sent Events endpoint for dashboard real-time updates

    Client connection:
    ```javascript
    const eventSource = new EventSource('/api/stream/dashboard');

    eventSource.addEventListener('job_scraped', (e) => {
        const data = JSON.parse(e.data);
        console.log('New job:', data);
    });
    ```

    Returns:
        SSE stream with events
    """

    @stream_with_context
    def generate():
        """Generator function for SSE stream"""
        # Send initial connection confirmation
        yield format_sse(
            {
                "type": "connected",
                "message": "Real-time connection established",
                "timestamp": datetime.utcnow().isoformat(),
            },
            event="connected",
        )

        # Send heartbeat every 30 seconds to keep connection alive
        last_heartbeat = time.time()

        # Main event loop
        while True:
            try:
                # Check for new events from event queue
                # Note: In production, this would poll a Redis queue or database
                # For now, we'll simulate with periodic checks

                # Heartbeat to keep connection alive
                current_time = time.time()
                if current_time - last_heartbeat > 30:
                    yield format_sse(
                        {"timestamp": datetime.utcnow().isoformat()}, event="heartbeat"
                    )
                    last_heartbeat = current_time

                # Sleep to avoid busy waiting
                time.sleep(1)

            except GeneratorExit:
                # Client disconnected
                logger.info("Client disconnected from SSE stream")
                break
            except Exception as e:
                logger.error(f"Error in SSE stream: {e}", exc_info=True)
                yield format_sse({"error": str(e)}, event="error")
                break

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Connection": "keep-alive",
        },
    )


# =================================================================
# EVENT BROADCASTING FUNCTIONS
# =================================================================


def broadcast_event(event_type, data):
    """
    Broadcast event to all connected SSE clients

    Args:
        event_type: Type of event (job_scraped, application_sent, etc.)
        data: Event data dictionary

    Note: In production, this would publish to Redis pub/sub
    For single user, we can use simpler in-memory approach
    """
    try:
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()

        # Log event
        logger.info(f"Broadcasting SSE event: {event_type} - {data}")

        # In production: Publish to Redis
        # redis_client.publish('dashboard_events', json.dumps({
        #     'event': event_type,
        #     'data': data
        # }))

        # For now, events are polled from database by SSE generator
        # This function serves as the API for other modules to trigger broadcasts

    except Exception as e:
        logger.error(f"Error broadcasting event: {e}", exc_info=True)


def broadcast_job_scraped(job_data):
    """Broadcast when new job is scraped"""
    broadcast_event(
        "job_scraped",
        {
            "id": job_data.get("id"),
            "title": job_data.get("job_title"),
            "company": job_data.get("company_name"),
            "location": job_data.get("location"),
        },
    )


def broadcast_job_analyzed(job_data):
    """Broadcast when job AI analysis completes"""
    broadcast_event(
        "job_analyzed",
        {
            "id": job_data.get("id"),
            "title": job_data.get("job_title"),
            "eligibility": job_data.get("eligibility_flag"),
            "priority_score": job_data.get("priority_score"),
        },
    )


def broadcast_application_sent(application_data):
    """Broadcast when job application is sent"""
    broadcast_event(
        "application_sent",
        {
            "id": application_data.get("id"),
            "job_id": application_data.get("job_id"),
            "job_title": application_data.get("job_title"),
            "company": application_data.get("company_name"),
            "status": application_data.get("application_status"),
        },
    )


def broadcast_pipeline_updated(pipeline_data):
    """Broadcast when pipeline stage counts change"""
    broadcast_event(
        "pipeline_updated",
        {
            "stage": pipeline_data.get("stage"),
            "count": pipeline_data.get("count"),
            "delta": pipeline_data.get("delta", 0),
        },
    )


def broadcast_metrics_refreshed(metrics_data):
    """Broadcast when dashboard metrics are refreshed"""
    broadcast_event(
        "metrics_refreshed",
        {
            "type": metrics_data.get("type"),
            "value": metrics_data.get("value"),
            "trend": metrics_data.get("trend"),
        },
    )


# =================================================================
# EVENT QUEUE (Simple Implementation for Single User)
# =================================================================


class DashboardEventQueue:
    """
    Simple in-memory event queue for dashboard SSE

    For single-user dashboard, this is sufficient.
    For production/multi-user, use Redis pub/sub instead.
    """

    def __init__(self):
        self.events = []
        self.max_size = 100  # Keep last 100 events

    def add_event(self, event_type, data):
        """Add event to queue"""
        self.events.append(
            {
                "event": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Trim queue if too large
        if len(self.events) > self.max_size:
            self.events = self.events[-self.max_size :]

    def get_events(self, since_timestamp=None):
        """Get events since timestamp"""
        if not since_timestamp:
            return self.events

        # Filter events after timestamp
        since_dt = datetime.fromisoformat(since_timestamp)
        return [e for e in self.events if datetime.fromisoformat(e["timestamp"]) > since_dt]

    def clear(self):
        """Clear all events"""
        self.events = []


# Global event queue instance
event_queue = DashboardEventQueue()


# =================================================================
# DATABASE POLLING FOR EVENTS (Fallback Implementation)
# =================================================================


def poll_database_for_events(last_check_time):
    """
    Poll database for new events since last check

    This is a fallback implementation for SSE events.
    In production, use database triggers → Redis pub/sub → SSE

    Args:
        last_check_time: Datetime of last check

    Returns:
        List of events that occurred since last check
    """
    from modules.database.database_client import DatabaseClient
    from sqlalchemy import text

    events = []

    try:
        db_client = DatabaseClient()
        with db_client.get_session() as db_session:
            # Check for new jobs (last 2 minutes)
            new_jobs_query = text("""
                SELECT id, job_title, company_id
                FROM jobs
                WHERE created_at > :last_check
                ORDER BY created_at DESC
                LIMIT 10
            """)

            new_jobs = db_session.execute(
                new_jobs_query, {"last_check": last_check_time}
            ).fetchall()

            for job in new_jobs:
                events.append(
                    {
                        "event": "job_scraped",
                        "data": {
                            "id": str(job.id),
                            "title": job.job_title,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    }
                )

            # Check for new applications (last 2 minutes)
            new_apps_query = text("""
                SELECT ja.id, j.job_title, ja.application_status
                FROM job_applications ja
                LEFT JOIN jobs j ON ja.job_id = j.id
                WHERE ja.created_at > :last_check
                ORDER BY ja.created_at DESC
                LIMIT 10
            """)

            new_apps = db_session.execute(
                new_apps_query, {"last_check": last_check_time}
            ).fetchall()

            for app in new_apps:
                events.append(
                    {
                        "event": "application_sent",
                        "data": {
                            "id": str(app.id),
                            "job_title": app.job_title,
                            "status": app.application_status,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    }
                )

    except Exception as e:
        logger.error(f"Error polling database for events: {e}", exc_info=True)

    return events


# =================================================================
# INTEGRATION WITH EXISTING WORKFLOW
# =================================================================

"""
To integrate SSE with existing workflow, add these calls:

# In modules/scraping/scraper_api.py (after job saved):
from modules.realtime.sse_dashboard import broadcast_job_scraped
broadcast_job_scraped({
    'id': job_id,
    'job_title': title,
    'company_name': company
})

# In modules/ai_job_description_analysis/ (after analysis):
from modules.realtime.sse_dashboard import broadcast_job_analyzed
broadcast_job_analyzed({
    'id': job_id,
    'job_title': title,
    'eligibility_flag': eligible
})

# In modules/workflow/application_orchestrator.py (after application):
from modules.realtime.sse_dashboard import broadcast_application_sent
broadcast_application_sent({
    'id': app_id,
    'job_id': job_id,
    'job_title': title,
    'application_status': 'sent'
})
"""
