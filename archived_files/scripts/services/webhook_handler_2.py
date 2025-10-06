import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from replit import object_storage
# Legacy generators have been deprecated and moved to archived_files/
# from .resume_generator import ResumeGenerator
# from .cover_letter_generator import CoverLetterGenerator

# Create Blueprint for webhook endpoints
webhook_bp = Blueprint('webhook', __name__)

# Initialize new template-based document generator
import sys
sys.path.append('..')
from modules.document_generation.document_generator import DocumentGenerator

# Initialize generator
document_generator = DocumentGenerator()

# Initialize object storage client for downloads
try:
    storage_client = object_storage.Client()
    logging.info("Download service connected to Replit Object Storage (default bucket)")
except Exception as e:
    logging.error(f"Failed to connect to object storage: {e}")
    storage_client = None

def validate_api_key():
    """Validate API key from request headers"""
    api_key = request.headers.get('X-API-Key')
    expected_key = os.environ.get('WEBHOOK_API_KEY')
    
    if not expected_key:
        logging.error("WEBHOOK_API_KEY not set in environment")
        return False
    
    if api_key != expected_key:
        logging.warning(f"Invalid API key provided: {api_key}")
        return False
    
    return True

@webhook_bp.route('/resume', methods=['POST'])
def handle_resume_webhook():
    """
    Resume-specific webhook endpoint for structured resume generation
    Accepts comprehensive resume data with all sections
    """
    try:
        # Validate API key
        if not validate_api_key():
            return jsonify({
                'status': 'error',
                'message': 'Invalid or missing API key'
            }), 401
        
        # Log request details
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        logging.info(f"Resume webhook received from IP: {client_ip}")
        
        # Parse JSON data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        resume_data = request.get_json()
        
        # Log received data (excluding sensitive info)
        safe_data = {k: v for k, v in resume_data.items() if k not in ['api_key', 'webhook_secret']}
        logging.info(f"Resume data received: {json.dumps(safe_data, indent=2)}")
        
        # Validate required fields
        if not isinstance(resume_data, dict):
            return jsonify({
                'status': 'error',
                'message': 'Invalid data format'
            }), 400
        
        # Generate resume using new template-based system
        file_info = document_generator.generate_document(resume_data, document_type='resume')
        
        # Prepare response
        response_data = {
            'status': 'success',
            'message': 'Resume generated successfully',
            'file_info': file_info,
            'webhook_id': resume_data.get('webhook_id', 'not_provided'),
            'timestamp': datetime.now().isoformat()
        }
        
        logging.info(f"Resume generated successfully: {file_info['filename']}")
        logging.info(f"Resume webhook response: {json.dumps(response_data, indent=2)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        error_msg = f"Error processing resume webhook: {str(e)}"
        logging.error(error_msg)
        
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'webhook_id': request.get_json().get('webhook_id', 'not_provided') if request.is_json else 'not_provided',
            'timestamp': datetime.now().isoformat()
        }), 500

@webhook_bp.route('/cover-letter', methods=['POST'])
def handle_cover_letter_webhook():
    """
    Cover letter-specific webhook endpoint for cover letter generation
    Accepts comprehensive cover letter data with all sections
    """
    try:
        # Validate API key
        if not validate_api_key():
            return jsonify({
                'status': 'error',
                'message': 'Invalid or missing API key'
            }), 401
        
        # Log request details
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        logging.info(f"Cover letter webhook received from IP: {client_ip}")
        
        # Parse JSON data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        letter_data = request.get_json()
        
        # Log received data (excluding sensitive info)
        safe_data = {k: v for k, v in letter_data.items() if k not in ['api_key', 'webhook_secret']}
        logging.info(f"Cover letter data received: {json.dumps(safe_data, indent=2)}")
        
        # Validate required fields
        if not isinstance(letter_data, dict):
            return jsonify({
                'status': 'error',
                'message': 'Invalid data format'
            }), 400
        
        # Generate cover letter using new template-based system
        file_info = document_generator.generate_document(letter_data, document_type='coverletter')
        
        # Prepare response
        response_data = {
            'status': 'success',
            'message': 'Cover letter generated successfully',
            'file_info': file_info,
            'webhook_id': letter_data.get('webhook_id', 'not_provided'),
            'timestamp': datetime.now().isoformat()
        }
        
        logging.info(f"Cover letter generated successfully: {file_info['filename']}")
        logging.info(f"Cover letter webhook response: {json.dumps(response_data, indent=2)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        error_msg = f"Error processing cover letter webhook: {str(e)}"
        logging.error(error_msg)
        
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'webhook_id': request.get_json().get('webhook_id', 'not_provided') if request.is_json else 'not_provided',
            'timestamp': datetime.now().isoformat()
        }), 500

@webhook_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download endpoint for generated documents
    Allows Make.com to retrieve the generated file from object storage or local fallback
    """
    try:
        logging.info(f"Download request for: {filename}")
        
        # Security: Validate filename to prevent path traversal attacks
        from modules.security.security_patch import SecurityPatch, secure_file_operation
        try:
            safe_filename = SecurityPatch.validate_filename(filename)
        except ValueError as e:
            logging.warning(f"Invalid filename blocked: {filename} - {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid filename'
            }), 400
        
        # Try object storage first
        if storage_client:
            try:
                storage_path = f"documents/{safe_filename}"
                file_data = storage_client.download_as_bytes(storage_path)
                
                logging.info(f"File downloaded from object storage: {storage_path}")
                
                # Validate file type and set appropriate MIME type
                if safe_filename.lower().endswith('.docx'):
                    mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif safe_filename.lower().endswith('.pdf'):
                    mimetype = 'application/pdf'
                else:
                    mimetype = 'application/octet-stream'
                
                response = Response(
                    file_data,
                    mimetype=mimetype,
                    headers={
                        'Content-Disposition': f'attachment; filename="{safe_filename}"',
                        'Content-Length': str(len(file_data))
                    }
                )
                
                return response
                
            except Exception as e:
                logging.warning(f"Object storage download failed: {e}")
        
        # Fallback to local storage with secure path validation
        try:
            secure_path = secure_file_operation(safe_filename, 'read')
            
            if os.path.exists(secure_path):
                logging.info(f"File found locally: {secure_path}")
                
                with open(secure_path, 'rb') as f:
                    file_data = f.read()
                
                # Validate file type and set appropriate MIME type
                if safe_filename.lower().endswith('.docx'):
                    mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif safe_filename.lower().endswith('.pdf'):
                    mimetype = 'application/pdf'
                else:
                    mimetype = 'application/octet-stream'
                
                response = Response(
                    file_data,
                    mimetype=mimetype,
                    headers={
                        'Content-Disposition': f'attachment; filename="{safe_filename}"',
                        'Content-Length': str(len(file_data))
                    }
                )
                
                return response
                
        except ValueError as e:
            logging.error(f"File access security violation: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
            
            return response
        
        # File not found
        logging.error(f"File not found: {filename}")
        return jsonify({
            'status': 'error',
            'message': f'File not found: {filename}'
        }), 404
        
    except Exception as e:
        error_msg = f"Error downloading file {filename}: {str(e)}"
        logging.error(error_msg)
        
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500

@webhook_bp.route('/debug/download/<filename>', methods=['GET'])
def debug_download(filename):
    """
    Debug endpoint to see what Make.com is requesting
    """
    try:
        logging.info(f"Debug download request for: {filename}")
        
        # Check if file exists in object storage
        storage_exists = False
        local_exists = False
        
        if storage_client:
            try:
                storage_path = f"documents/{filename}"
                # Try to get file info
                storage_client.download_as_bytes(storage_path)
                storage_exists = True
            except:
                storage_exists = False
        
        # Check local storage
        local_path = f"storage/{filename}"
        local_exists = os.path.exists(local_path)
        
        debug_info = {
            'filename': filename,
            'storage_exists': storage_exists,
            'local_exists': local_exists,
            'storage_path': f"documents/{filename}",
            'local_path': local_path,
            'timestamp': datetime.now().isoformat()
        }
        
        logging.info(f"Debug info: {json.dumps(debug_info, indent=2)}")
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        error_msg = f"Debug error for {filename}: {str(e)}"
        logging.error(error_msg)
        
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500

@webhook_bp.route('/test', methods=['GET', 'POST'])
def test_webhook():
    """
    Test endpoint to verify webhook functionality
    """
    try:
        if request.method == 'GET':
            return jsonify({
                'status': 'success',
                'message': 'Webhook service is running',
                'timestamp': datetime.now().isoformat(),
                'available_endpoints': [
                    '/resume - POST: Generate structured resume',
                    '/cover-letter - POST: Generate cover letter',
                    '/download/<filename> - GET: Download generated file',
                    '/debug/download/<filename> - GET: Debug file information',
                    '/test - GET/POST: Test endpoint'
                ]
            })
        
        if request.method == 'POST':
            test_data = request.get_json() if request.is_json else {}
            return jsonify({
                'status': 'success',
                'message': 'Test webhook received',
                'received_data': test_data,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        error_msg = f"Test endpoint error: {str(e)}"
        logging.error(error_msg)
        
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500