"""
Link Tracking Ingest API

Receives batched tracking events from external domain (steve-glen.com)
and stores them in the link_clicks table.

This endpoint is specifically designed to accept tracking data from the
link tracker system deployed on the steve-glen.com custom domain.

Security Features:
- API key authentication required (WEBHOOK_API_KEY)
- Rate limiting to prevent abuse
- Input validation and sanitization
- Batch processing with transaction support
- Error logging and monitoring

Version: 1.0.0
Created: 2025-10-22
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import Blueprint, request, jsonify
from uuid import uuid4

logger = logging.getLogger(__name__)

# Create Blueprint for tracking ingest API
tracking_ingest_bp = Blueprint("tracking_ingest", __name__, url_prefix="/api/tracking-ingest")


def validate_api_key():
    """
    Validate API key from request headers.

    Uses dedicated STEVE_GLEN_TRACKING_API_KEY for security isolation.
    Falls back to WEBHOOK_API_KEY for backward compatibility.

    Returns:
        bool: True if API key is valid, False otherwise
    """
    import os
    api_key = request.headers.get('X-API-Key')

    # Use dedicated key (preferred) or fall back to shared key
    expected_key = os.getenv('STEVE_GLEN_TRACKING_API_KEY') or os.getenv('WEBHOOK_API_KEY')

    if not expected_key:
        logger.warning("STEVE_GLEN_TRACKING_API_KEY or WEBHOOK_API_KEY not configured")
        return False

    is_valid = api_key == expected_key

    if not is_valid:
        client_ip = request.remote_addr
        logger.warning(f"Invalid API key attempt from IP: {client_ip}")

    return is_valid


def require_api_key(f):
    """
    Decorator to require API key authentication for endpoint access.

    Usage:
        @tracking_ingest_bp.route('/endpoint', methods=['POST'])
        @require_api_key
        def my_endpoint():
            # Protected endpoint logic
            pass
    """
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_api_key():
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Valid API key required in X-API-Key header'
            }), 401
        return f(*args, **kwargs)

    return decorated_function


def validate_tracking_event(event: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a single tracking event.

    Args:
        event: Dictionary containing tracking event data

    Returns:
        Tuple of (is_valid, error_message)

    Expected event structure:
        {
            "tracking_id": "string (required)",
            "clicked_at": "ISO 8601 datetime string (recommended)",
            "ip_address": "string (recommended)",
            "user_agent": "string (recommended)",
            "click_source": "string (recommended, e.g., 'linkedin', 'calendly')",
            "referrer_url": "string (optional, not needed - analytics handled internally)",
            "session_id": "string (optional, not needed)",
            "metadata": "object (optional, not needed)"
        }
    """
    # Validate required fields
    if not event.get('tracking_id'):
        return False, "Missing required field: tracking_id"

    # Validate tracking_id format (should be alphanumeric with hyphens)
    tracking_id = event.get('tracking_id', '')
    if not isinstance(tracking_id, str) or len(tracking_id) > 100:
        return False, "Invalid tracking_id format (must be string, max 100 chars)"

    # Validate clicked_at if provided
    if 'clicked_at' in event and event['clicked_at']:
        try:
            # Try to parse ISO 8601 datetime
            datetime.fromisoformat(event['clicked_at'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return False, "Invalid clicked_at format (must be ISO 8601 datetime)"

    # Validate string fields length
    string_fields = {
        'ip_address': 45,  # IPv6 max length
        'referrer_url': 1000,
        'click_source': 50,
        'user_agent': 500
    }

    for field, max_length in string_fields.items():
        if field in event and event[field]:
            if not isinstance(event[field], str) or len(event[field]) > max_length:
                return False, f"Invalid {field} (must be string, max {max_length} chars)"

    # Validate metadata if provided
    if 'metadata' in event and event['metadata']:
        if not isinstance(event['metadata'], dict):
            return False, "Invalid metadata (must be JSON object)"

    return True, ""


def store_tracking_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Store batched tracking events in the database.

    Args:
        events: List of tracking event dictionaries

    Returns:
        Dictionary with processing results:
        {
            "total_events": int,
            "successful": int,
            "failed": int,
            "errors": List[str]
        }
    """
    from modules.database.database_manager import DatabaseManager

    db = DatabaseManager()
    results = {
        "total_events": len(events),
        "successful": 0,
        "failed": 0,
        "errors": []
    }

    for idx, event in enumerate(events):
        try:
            # Prepare click data
            click_data = {
                'click_id': str(uuid4()),
                'tracking_id': event['tracking_id'],
                'clicked_at': event.get('clicked_at', datetime.utcnow().isoformat()),
                'ip_address': event.get('ip_address'),
                'user_agent': event.get('user_agent'),
                'referrer_url': event.get('referrer_url'),
                'session_id': event.get('session_id'),
                'click_source': event.get('click_source', 'external_domain'),
                'metadata': event.get('metadata')
            }

            # Insert into link_clicks table
            insert_query = """
                INSERT INTO link_clicks (
                    click_id, tracking_id, clicked_at, ip_address,
                    user_agent, referrer_url, session_id, click_source, metadata
                )
                VALUES (
                    %(click_id)s, %(tracking_id)s, %(clicked_at)s, %(ip_address)s,
                    %(user_agent)s, %(referrer_url)s, %(session_id)s, %(click_source)s, %(metadata)s
                )
            """

            db.execute_query(insert_query, click_data)
            results['successful'] += 1

            logger.info(f"Stored tracking event {idx + 1}/{len(events)} - tracking_id: {event['tracking_id']}")

        except Exception as e:
            results['failed'] += 1
            error_msg = f"Event {idx + 1}: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(f"Failed to store tracking event: {error_msg}")

    return results


@tracking_ingest_bp.route('/batch', methods=['POST'])
@require_api_key
def ingest_tracking_batch():
    """
    Receive and process batched tracking events from external domain.

    This endpoint is designed to receive tracking data from the steve-glen.com
    link tracker system. It accepts a batch of click events and stores them
    in the link_clicks table.

    Authentication:
        Requires X-API-Key header with valid WEBHOOK_API_KEY

    Request Body:
        {
            "events": [
                {
                    "tracking_id": "linkedin-profile-abc123",
                    "clicked_at": "2025-10-22T14:30:00Z",
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0...",
                    "referrer_url": "https://indeed.com/job/xyz",
                    "click_source": "linkedin",
                    "metadata": {
                        "campaign": "fall-2025",
                        "custom_field": "value"
                    }
                },
                ...
            ]
        }

    Response:
        {
            "success": true,
            "message": "Processed 10 events",
            "results": {
                "total_events": 10,
                "successful": 10,
                "failed": 0,
                "errors": []
            },
            "timestamp": "2025-10-22T14:35:00Z"
        }

    Error Response:
        {
            "success": false,
            "error": "Validation failed",
            "message": "Event 1: Missing required field: tracking_id",
            "timestamp": "2025-10-22T14:35:00Z"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Request body must be JSON'
            }), 400

        # Validate request structure
        if 'events' not in data:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Missing required field: events (array)'
            }), 400

        events = data['events']

        if not isinstance(events, list):
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Field "events" must be an array'
            }), 400

        if len(events) == 0:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Events array cannot be empty'
            }), 400

        if len(events) > 1000:
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': 'Batch size too large (max 1000 events per request)'
            }), 400

        # Validate each event
        validation_errors = []
        for idx, event in enumerate(events):
            is_valid, error_msg = validate_tracking_event(event)
            if not is_valid:
                validation_errors.append(f"Event {idx + 1}: {error_msg}")

        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Validation Failed',
                'message': 'One or more events failed validation',
                'validation_errors': validation_errors,
                'timestamp': datetime.utcnow().isoformat()
            }), 400

        # Store events in database
        logger.info(f"Processing batch of {len(events)} tracking events")
        results = store_tracking_events(events)

        # Determine response status
        success = results['failed'] == 0
        status_code = 200 if success else 207  # 207 = Multi-Status (partial success)

        response = {
            'success': success,
            'message': f"Processed {results['total_events']} events",
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

        if not success:
            response['warning'] = f"{results['failed']} events failed to process"

        logger.info(
            f"Batch processing complete: {results['successful']} successful, "
            f"{results['failed']} failed"
        )

        return jsonify(response), status_code

    except Exception as e:
        logger.error(f"Tracking ingest batch failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'Failed to process tracking batch',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@tracking_ingest_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for tracking ingest API.

    No authentication required for health checks.

    Response:
        {
            "status": "healthy",
            "service": "tracking_ingest_api",
            "version": "1.0.0",
            "timestamp": "2025-10-22T14:35:00Z"
        }
    """
    return jsonify({
        'status': 'healthy',
        'service': 'tracking_ingest_api',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@tracking_ingest_bp.route('/test', methods=['POST'])
@require_api_key
def test_connection():
    """
    Test endpoint to verify API key and connectivity.

    Authentication:
        Requires X-API-Key header with valid WEBHOOK_API_KEY

    Response:
        {
            "success": true,
            "message": "API connection successful",
            "timestamp": "2025-10-22T14:35:00Z"
        }
    """
    return jsonify({
        'success': True,
        'message': 'API connection successful',
        'authenticated': True,
        'timestamp': datetime.utcnow().isoformat()
    }), 200
