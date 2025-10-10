#!/usr/bin/env python3
"""
Sentence Variation API - Flask Blueprint

REST API for generating sentence variations using Gemini AI.
Accepts seed sentences and returns CSV-ready variations.

Author: Automated Job Application System
Version: 1.0.0
"""

import logging
import json
from flask import Blueprint, request, jsonify, Response
from typing import Dict, List
from .sentence_variation_generator import SentenceVariationGenerator

logger = logging.getLogger(__name__)

# Create Blueprint
sentence_variation_bp = Blueprint('sentence_variation', __name__, url_prefix='/api/sentence-variations')


@sentence_variation_bp.route('/generate', methods=['POST'])
def generate_variations():
    """
    Generate variations for seed sentences using Gemini AI

    Request Body:
    {
        "seed_sentences": [
            {
                "content_text": "Led comprehensive rebranding initiative...",
                "tone": "Confident",
                "category": "Achievement",
                "intended_document": "resume",
                "position_label": "Marketing Automation Manager",
                "matches_job_skill": "Brand Management"
            }
        ],
        "variations_per_seed": 7,
        "target_position": "Marketing Automation Manager",
        "output_format": "json"  // or "csv"
    }

    Response:
    {
        "success": true,
        "variations": [...],
        "stats": {...},
        "csv_download_url": "/api/sentence-variations/download/session_id"
    }
    """

    try:
        # Parse request body
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400

        seed_sentences = data.get('seed_sentences', [])
        variations_per_seed = data.get('variations_per_seed', 7)
        target_position = data.get('target_position')
        output_format = data.get('output_format', 'json')

        # Validate input
        if not seed_sentences:
            return jsonify({
                'success': False,
                'error': 'seed_sentences array is required'
            }), 400

        if not isinstance(seed_sentences, list):
            return jsonify({
                'success': False,
                'error': 'seed_sentences must be an array'
            }), 400

        # Validate each seed sentence has required fields
        for idx, seed in enumerate(seed_sentences):
            if not seed.get('content_text'):
                return jsonify({
                    'success': False,
                    'error': f'Seed sentence {idx + 1} missing required field: content_text'
                }), 400

        logger.info(f"Generating variations for {len(seed_sentences)} seed sentences")

        # Initialize generator
        generator = SentenceVariationGenerator()

        # Generate variations
        result = generator.generate_variations(
            seed_sentences=seed_sentences,
            variations_per_seed=variations_per_seed,
            target_position=target_position
        )

        # Return based on requested format
        if output_format == 'csv':
            csv_content = generator.export_to_csv_format(result['variations'])

            return Response(
                csv_content,
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=sentence_variations_{result["stats"]["start_time"]}.csv'
                }
            )
        else:
            # JSON response
            return jsonify({
                'success': True,
                'message': f'Generated {result["stats"]["total_generated"]} variations from {len(seed_sentences)} seeds',
                'variations': result['variations'],
                'stats': result['stats']
            })

    except ValueError as e:
        logger.error(f"Validation error in generate_variations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error generating variations: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@sentence_variation_bp.route('/batch-generate', methods=['POST'])
def batch_generate_variations():
    """
    Generate variations in batches to handle large seed lists

    Request Body:
    {
        "seed_sentences": [...],  // Can be large list
        "variations_per_seed": 7,
        "target_position": "Marketing Automation Manager",
        "batch_size": 5  // Process 5 seeds at a time
    }

    Response:
    {
        "success": true,
        "job_id": "batch_20250109_123456",
        "status": "processing",
        "message": "Batch generation started. Check status at /api/sentence-variations/status/job_id"
    }
    """

    try:
        data = request.get_json()

        seed_sentences = data.get('seed_sentences', [])
        variations_per_seed = data.get('variations_per_seed', 7)
        target_position = data.get('target_position')
        batch_size = data.get('batch_size', 5)

        if not seed_sentences:
            return jsonify({
                'success': False,
                'error': 'seed_sentences array is required'
            }), 400

        # For now, process synchronously
        # TODO: Implement async processing with job tracking
        generator = SentenceVariationGenerator()

        all_variations = []
        total_stats = {
            'total_seeds': len(seed_sentences),
            'total_generated': 0,
            'successful_batches': 0,
            'failed_batches': 0
        }

        # Process in batches
        for i in range(0, len(seed_sentences), batch_size):
            batch = seed_sentences[i:i + batch_size]

            try:
                result = generator.generate_variations(
                    seed_sentences=batch,
                    variations_per_seed=variations_per_seed,
                    target_position=target_position
                )

                all_variations.extend(result['variations'])
                total_stats['total_generated'] += result['stats']['total_generated']
                total_stats['successful_batches'] += 1

            except Exception as e:
                logger.error(f"Batch {i // batch_size + 1} failed: {str(e)}")
                total_stats['failed_batches'] += 1
                continue

        return jsonify({
            'success': True,
            'message': f'Batch processing complete. Generated {total_stats["total_generated"]} variations',
            'variations': all_variations,
            'stats': total_stats
        })

    except Exception as e:
        logger.error(f"Error in batch generation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sentence_variation_bp.route('/example-request', methods=['GET'])
def example_request():
    """
    Get an example request body for the generate endpoint

    Returns example JSON showing how to structure seed sentences
    """

    example = {
        "seed_sentences": [
            {
                "content_text": "Led comprehensive rebranding initiative for 14-year-old media company, modernizing visual identity and messaging strategy",
                "tone": "Confident",
                "category": "Leadership",
                "intended_document": "resume",
                "position_label": "Marketing Automation Manager",
                "matches_job_skill": "Brand Management"
            },
            {
                "content_text": "Your company's innovative approach to marketing automation immediately caught my attention",
                "tone": "Curious",
                "category": "Opening",
                "intended_document": "cover_letter",
                "position_label": "Marketing Automation Manager",
                "matches_job_skill": "Marketing Automation"
            },
            {
                "content_text": "I bring 14+ years of experience building marketing strategies that bridge creativity and data analysis",
                "tone": "Confident",
                "category": "Alignment",
                "intended_document": "cover_letter",
                "position_label": "Marketing Automation Manager",
                "matches_job_skill": "Marketing Strategy"
            }
        ],
        "variations_per_seed": 7,
        "target_position": "Marketing Automation Manager",
        "output_format": "json"
    }

    return jsonify({
        'success': True,
        'example_request': example,
        'usage_notes': {
            'required_fields': ['content_text'],
            'optional_fields': ['tone', 'category', 'intended_document', 'position_label', 'matches_job_skill'],
            'default_variations': 7,
            'output_formats': ['json', 'csv'],
            'tone_options': ['Confident', 'Warm', 'Bold', 'Curious', 'Storytelling', 'Insightful', 'Quirky']
        }
    })


@sentence_variation_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for sentence variation service

    Returns API status and Gemini API key availability
    """

    import os

    gemini_configured = bool(os.environ.get('GEMINI_API_KEY'))

    return jsonify({
        'success': True,
        'service': 'Sentence Variation Generator',
        'status': 'healthy',
        'gemini_configured': gemini_configured,
        'model': 'gemini-2.0-flash-exp',
        'endpoints': {
            'generate': '/api/sentence-variations/generate',
            'batch_generate': '/api/sentence-variations/batch-generate',
            'example': '/api/sentence-variations/example-request',
            'health': '/api/sentence-variations/health'
        }
    })
