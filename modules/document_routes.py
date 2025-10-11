#!/usr/bin/env python3
"""
Document Generation Routes Blueprint

Provides REST API endpoints for generating resumes and cover letters using the
template-based document generation system with rate limiting.
"""

import os
import logging
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, Response
from modules.content.document_generation.document_generator import DocumentGenerator
from modules.storage import get_storage_backend
from modules.security.rate_limit_manager import rate_limit_moderate

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint for document generation routes
document_bp = Blueprint("document", __name__)

# Initialize document generator
doc_generator = DocumentGenerator()

# Initialize storage backend for downloads
try:
    storage_client = get_storage_backend()
    logger.info(f"Document routes connected to storage backend: {storage_client.backend_name}")
except Exception as e:
    logger.error(f"Failed to initialize storage client: {str(e)}")
    storage_client = None


@document_bp.route("/resume", methods=["POST"])
@rate_limit_moderate  # Document generation: 20/min;200/hour
def generate_resume():
    """
    Generate a professional resume document

    Expected JSON payload:
    {
        "personal": {
            "full_name": "Steve Glen",
            "phone": "(780) 555-0123",
            "email": "1234.s.t.e.v.e.glen@gmail.com",
            "address": "Edmonton, AB, Canada"
        },
        "professional_summary": "Text summary...",
        "experience": [...],
        "education": [...],
        "skills": {...},
        "target_position": "Marketing Manager"
    }
    """
    try:
        logger.info("Resume generation request received")

        # Validate content type
        if not request.is_json:
            return jsonify({"success": False, "error": "Invalid content type - JSON expected"}), 400

        # Parse JSON payload
        resume_data = request.get_json()
        if not resume_data:
            return jsonify({"success": False, "error": "Empty payload - no resume data received"}), 400

        # Extract optional tracking context
        job_id = resume_data.get("job_id")  # Optional UUID for URL tracking
        application_id = resume_data.get("application_id")  # Optional UUID for URL tracking

        logger.info(f"Resume data received (job_id={job_id}, app_id={application_id}), generating document...")

        # Prepare template data for document generator
        template_data = {
            "document_type": "resume",
            "full_name": resume_data.get("personal", {}).get("full_name", "Steve Glen"),
            "phone": resume_data.get("personal", {}).get("phone", "(780) 555-0123"),
            "email": resume_data.get("personal", {}).get("email", "1234.s.t.e.v.e.glen@gmail.com"),
            "address": resume_data.get("personal", {}).get("address", "Edmonton, AB, Canada"),
            "linkedin": resume_data.get("personal", {}).get("linkedin", ""),
            "website": resume_data.get("personal", {}).get("website", ""),
            "professional_summary": resume_data.get("professional_summary", ""),
            "experience": resume_data.get("experience", []),
            "education": resume_data.get("education", []),
            "skills": resume_data.get("skills", {}),
            "target_position": resume_data.get("target_position", "Marketing Manager"),
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Generate document using template system (with optional URL tracking context)
        result = doc_generator.generate_document(
            data=template_data,
            document_type="resume",
            job_id=job_id,
            application_id=application_id
        )

        if result.get("success"):
            logger.info(f"Resume generated successfully: {result.get('filename')}")
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Resume generated successfully",
                        "filename": result.get("filename"),
                        "file_path": result.get("file_path"),
                        "download_url": f"/download/{result.get('filename')}",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                200,
            )
        else:
            logger.error(f"Resume generation failed: {result.get('error')}")
            return (
                jsonify({"success": False, "error": result.get("error", "Unknown error during resume generation")}),
                500,
            )

    except Exception as e:
        logger.error(f"Resume generation exception: {str(e)}")
        return jsonify({"success": False, "error": f"Resume generation failed: {str(e)}"}), 500


@document_bp.route("/cover-letter", methods=["POST"])
@rate_limit_moderate  # Document generation: 20/min;200/hour
def generate_cover_letter():
    """
    Generate a professional cover letter document

    Expected JSON payload:
    {
        "personal": {
            "full_name": "Steve Glen",
            "phone": "(780) 555-0123",
            "email": "1234.s.t.e.v.e.glen@gmail.com",
            "address": "Edmonton, AB, Canada"
        },
        "recipient": {
            "name": "Hiring Manager",
            "title": "Hiring Manager",
            "company": "Company Name"
        },
        "position": {
            "title": "Marketing Manager",
            "reference": "Job ID: XXX"
        },
        "content": {
            "opening_paragraph": "...",
            "body_paragraphs": ["...", "...", "..."],
            "closing_paragraph": "..."
        },
        "date": "2025-07-23"
    }
    """
    try:
        logger.info("Cover letter generation request received")

        # Validate content type
        if not request.is_json:
            return jsonify({"success": False, "error": "Invalid content type - JSON expected"}), 400

        # Parse JSON payload
        cover_letter_data = request.get_json()
        if not cover_letter_data:
            return jsonify({"success": False, "error": "Empty payload - no cover letter data received"}), 400

        # Extract optional tracking context
        job_id = cover_letter_data.get("job_id")  # Optional UUID for URL tracking
        application_id = cover_letter_data.get("application_id")  # Optional UUID for URL tracking

        logger.info(f"Cover letter data received (job_id={job_id}, app_id={application_id}), generating document...")

        # Prepare template data for document generator
        template_data = {
            "document_type": "cover_letter",
            "full_name": cover_letter_data.get("personal", {}).get("full_name", "Steve Glen"),
            "phone": cover_letter_data.get("personal", {}).get("phone", "(780) 555-0123"),
            "email": cover_letter_data.get("personal", {}).get("email", "1234.s.t.e.v.e.glen@gmail.com"),
            "address": cover_letter_data.get("personal", {}).get("address", "Edmonton, AB, Canada"),
            "recipient_name": cover_letter_data.get("recipient", {}).get("name", "Hiring Manager"),
            "recipient_title": cover_letter_data.get("recipient", {}).get("title", "Hiring Manager"),
            "company_name": cover_letter_data.get("recipient", {}).get("company", "Company Name"),
            "position_title": cover_letter_data.get("position", {}).get("title", "Marketing Manager"),
            "position_reference": cover_letter_data.get("position", {}).get("reference", ""),
            "opening_paragraph": cover_letter_data.get("content", {}).get("opening_paragraph", ""),
            "body_paragraphs": cover_letter_data.get("content", {}).get("body_paragraphs", []),
            "closing_paragraph": cover_letter_data.get("content", {}).get("closing_paragraph", ""),
            "date": cover_letter_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Generate document using template system (with optional URL tracking context)
        result = doc_generator.generate_document(
            data=template_data,
            document_type="cover_letter",
            job_id=job_id,
            application_id=application_id
        )

        if result.get("success"):
            logger.info(f"Cover letter generated successfully: {result.get('filename')}")
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Cover letter generated successfully",
                        "filename": result.get("filename"),
                        "file_path": result.get("file_path"),
                        "download_url": f"/download/{result.get('filename')}",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                200,
            )
        else:
            logger.error(f"Cover letter generation failed: {result.get('error')}")
            return (
                jsonify(
                    {"success": False, "error": result.get("error", "Unknown error during cover letter generation")}
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Cover letter generation exception: {str(e)}")
        return jsonify({"success": False, "error": f"Cover letter generation failed: {str(e)}"}), 500


@document_bp.route("/download/<filename>")
def download_file(filename):
    """
    Download generated document files

    Args:
        filename (str): Name of the file to download

    Returns:
        File download response or error message
    """
    try:
        logger.info(f"Download request for file: {filename}")

        # Security: Validate filename to prevent path traversal
        if not filename or ".." in filename or "/" in filename or "\\" in filename:
            return jsonify({"success": False, "error": "Invalid filename"}), 400

        # Try downloading from storage backend
        if storage_client:
            try:
                # Retrieve file content from storage backend
                file_data = storage_client.get(filename)

                # Determine content type based on file extension
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if filename.endswith(".pdf"):
                    content_type = "application/pdf"
                elif filename.endswith(".txt"):
                    content_type = "text/plain"

                # Create response with proper headers
                response = Response(
                    file_data,
                    content_type=content_type,
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"',
                        "Content-Length": str(len(file_data)),
                    },
                )

                logger.info(f"File downloaded successfully from storage: {filename}")
                return response

            except FileNotFoundError:
                logger.warning(f"File not found in storage backend: {filename}")
                # Fall back to local storage directory
            except Exception as storage_error:
                logger.warning(f"Storage backend download failed: {storage_error}")
                # Fall back to local storage directory

        # Fallback to local storage
        local_path = os.path.join("storage", filename)
        if os.path.exists(local_path):
            logger.info(f"File downloaded from local storage: {filename}")
            return send_file(local_path, as_attachment=True, download_name=filename)
        else:
            logger.error(f"File not found: {filename}")
            return jsonify({"success": False, "error": "File not found"}), 404

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({"success": False, "error": f"Download failed: {str(e)}"}), 500


@document_bp.route("/test", methods=["GET", "POST"])
def test_endpoint():
    """
    Test endpoint for document generation system
    """
    if request.method == "GET":
        return jsonify(
            {
                "status": "Document generation system operational",
                "endpoints": {
                    "resume": "/resume - POST: Generate resume document",
                    "cover_letter": "/cover-letter - POST: Generate cover letter document",
                    "download": "/download/<filename> - GET: Download generated files",
                },
                "timestamp": datetime.now().isoformat(),
            }
        )

    elif request.method == "POST":
        # Simple test document generation
        test_data = {
            "document_type": "test",
            "title": "Test Document",
            "content": "This is a test document generated from the document generation API.",
            "author": "Steve Glen",
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        try:
            result = doc_generator.generate_document(data=test_data, document_type="test")

            return jsonify(
                {
                    "success": True,
                    "message": "Test document generated",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Test generation failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                500,
            )
