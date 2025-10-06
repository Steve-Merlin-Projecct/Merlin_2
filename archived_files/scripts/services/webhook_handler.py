import os
import logging
import json
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, Response
from document_generator import DocumentGenerator
from resume_generator import ResumeGenerator
from replit.object_storage import Client

# Create blueprint for webhook routes
webhook_bp = Blueprint('webhook', __name__)

# Initialize document generator
doc_generator = DocumentGenerator()

# Initialize object storage client for downloads (using default bucket)
try:
    storage_client = Client()
    logging.info("Download service connected to Replit Object Storage (default bucket)")
except Exception as e:
    logging.error(f"Failed to initialize download storage client: {str(e)}")
    storage_client = None

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Main webhook endpoint for Make.com integration
    Accepts JSON payload and generates Word document
    """
    try:
        # API key authentication
        api_key = request.headers.get('X-API-Key')
        expected_key = os.environ.get('WEBHOOK_API_KEY')
        
        if expected_key and api_key != expected_key:
            logging.warning(f"Unauthorized webhook attempt from IP: {request.remote_addr}")
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized - Invalid API Key',
                'timestamp': datetime.now().isoformat()
            }), 401
        
        # Log incoming webhook request
        logging.info(f"Webhook received from IP: {request.remote_addr}")
        
        # Validate content type
        if not request.is_json:
            logging.error("Invalid content type - JSON expected")
            return jsonify({
                "error": "Invalid content type",
                "message": "Expected application/json"
            }), 400
        
        # Parse JSON payload
        webhook_data = request.get_json()
        
        if not webhook_data:
            logging.error("Empty JSON payload received")
            return jsonify({
                "error": "Empty payload",
                "message": "No data received in webhook"
            }), 400
        
        logging.info(f"Webhook data received: {json.dumps(webhook_data, indent=2)}")
        
        # Validate required fields
        required_fields = ['title', 'content']
        missing_fields = [field for field in required_fields if field not in webhook_data]
        
        if missing_fields:
            logging.error(f"Missing required fields: {missing_fields}")
            return jsonify({
                "error": "Missing required fields",
                "message": f"Required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }), 400
        
        # Generate Word document
        try:
            file_info = doc_generator.generate_document(webhook_data)
            logging.info(f"Document generated successfully: {file_info['filename']}")
            
            # Return success response with file information
            response_data = {
                "status": "success",
                "message": "Document generated successfully",
                "file_info": file_info,
                "webhook_id": webhook_data.get('webhook_id', 'not_provided'),
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Webhook response: {json.dumps(response_data, indent=2)}")
            return jsonify(response_data), 200
            
        except Exception as doc_error:
            logging.error(f"Document generation failed: {str(doc_error)}")
            return jsonify({
                "error": "Document generation failed",
                "message": str(doc_error),
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except json.JSONDecodeError as json_error:
        logging.error(f"JSON parsing error: {str(json_error)}")
        return jsonify({
            "error": "Invalid JSON",
            "message": "Failed to parse JSON payload"
        }), 400
        
    except Exception as e:
        logging.error(f"Unexpected webhook error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }), 500

@webhook_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download endpoint for generated documents
    Allows Make.com to retrieve the generated file from object storage or local fallback
    """
    try:
        # Log the request details for debugging
        logging.info(f"Download request for: {filename}")
        logging.info(f"User-Agent: {request.headers.get('User-Agent', 'Not provided')}")
        logging.info(f"Request headers: {dict(request.headers)}")
        
        # First try to download from object storage
        if storage_client:
            try:
                object_storage_path = f"documents/{filename}"
                
                # Check if file exists in object storage
                if storage_client.exists(object_storage_path):
                    # Download file as bytes from object storage
                    file_data = storage_client.download_as_bytes(object_storage_path)
                    
                    logging.info(f"Serving file from object storage: {filename} ({len(file_data)} bytes)")
                    
                    # Create a simple response with just the file data and essential headers
                    from flask import make_response
                    
                    response = make_response(file_data)
                    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
                    response.headers['Content-Length'] = str(len(file_data))
                    response.headers['Accept-Ranges'] = 'bytes'
                    
                    # Add some cache control to ensure fresh downloads
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    
                    return response
                else:
                    logging.info(f"File not found in object storage, trying local: {filename}")
                    
            except Exception as storage_error:
                logging.error(f"Object storage download failed: {str(storage_error)}")
                logging.info(f"Falling back to local storage for: {filename}")
        
        # Fallback to local storage
        storage_dir = os.path.join(os.getcwd(), 'storage')
        file_path = os.path.join(storage_dir, filename)
        
        if os.path.exists(file_path):
            logging.info(f"Serving file from local storage: {filename}")
            
            # Read file and create response
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            from flask import make_response
            response = make_response(file_data)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.headers['Content-Length'] = str(len(file_data))
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        
        # File not found in either location
        logging.error(f"File not found in object storage or local storage: {filename}")
        return jsonify({
            "error": "File not found",
            "message": f"File {filename} does not exist in object storage or local storage"
        }), 404
        
    except Exception as e:
        logging.error(f"File download error: {str(e)}")
        return jsonify({
            "error": "Download failed",
            "message": str(e)
        }), 500



@webhook_bp.route('/download-debug/<filename>', methods=['GET'])
def debug_download(filename):
    """
    Debug endpoint to see what Make.com is requesting
    """
    logging.info(f"Download debug request for: {filename}")
    logging.info(f"Request headers: {dict(request.headers)}")
    logging.info(f"Request args: {dict(request.args)}")
    logging.info(f"User-Agent: {request.headers.get('User-Agent', 'Not provided')}")
    
    return jsonify({
        "filename": filename,
        "headers": dict(request.headers),
        "args": dict(request.args),
        "method": request.method,
        "url": request.url
    })

@webhook_bp.route('/webhook/test', methods=['GET'])
def test_webhook():
    """
    Test endpoint to verify webhook functionality
    """
    return jsonify({
        "status": "ok",
        "message": "Webhook endpoint is working",
        "timestamp": datetime.now().isoformat(),
        "instructions": {
            "method": "POST",
            "endpoint": "/webhook",
            "content_type": "application/json",
            "required_fields": ["title", "content"],
            "optional_fields": ["author", "date", "sections", "formatting"]
        }
    }), 200

@webhook_bp.route('/resume', methods=['POST'])
def handle_resume_webhook():
    """
    Resume-specific webhook endpoint for structured resume generation
    Accepts comprehensive resume data with all sections
    """
    try:
        # Verify API key
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('WEBHOOK_API_KEY'):
            logging.warning(f"Unauthorized resume webhook attempt from IP: {request.remote_addr}")
            return jsonify({"error": "Unauthorized"}), 401
        
        # Log request details
        logging.info(f"Resume webhook received from IP: {request.remote_addr}")
        
        # Parse JSON data
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        resume_data = request.get_json()
        logging.info(f"Resume data received: {json.dumps(resume_data, indent=2)}")
        
        # Generate resume using structured generator
        resume_generator = ResumeGenerator()
        file_info = resume_generator.generate_resume(resume_data)
        
        # Prepare response
        response_data = {
            "status": "success",
            "message": "Resume generated successfully",
            "file_info": {
                **file_info,
                "download_url": f"/download/{file_info['filename']}",
                "direct_download_url": f"/download/{file_info['filename']}"
            },
            "webhook_id": resume_data.get('webhook_id', 'not_provided'),
            "timestamp": datetime.now().isoformat()
        }
        
        logging.info(f"Resume webhook response: {json.dumps(response_data, indent=2)}")
        return jsonify(response_data)
        
    except Exception as e:
        logging.error(f"Resume webhook processing error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Resume processing failed",
            "message": str(e)
        }), 500
