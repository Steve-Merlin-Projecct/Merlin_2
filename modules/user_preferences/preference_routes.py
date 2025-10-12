"""
User Preferences Flask Routes

Provides web interface for managing user job preferences through
multi-variable regression scenarios.
"""

import logging
import pickle
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import Dict, Any
from .preference_regression import PreferenceRegression
from .preference_db import PreferenceDatabase
from .job_scorer import JobScorer, JobScorerFactory

logger = logging.getLogger(__name__)

# Create Blueprint
preference_bp = Blueprint('preferences', __name__, url_prefix='/preferences')


# ==================== Web UI Routes ====================

@preference_bp.route('/')
def index():
    """
    Preference configuration page.

    Shows current scenarios and trained model status.
    """
    try:
        user_id = request.args.get('user_id', 'steve_glen')  # TODO: Get from session

        pref_db = PreferenceDatabase()

        # Get existing scenarios
        scenarios = pref_db.get_scenarios(user_id)

        # Get model status
        model_data = pref_db.load_model(user_id)
        model_trained = model_data is not None

        model_info = None
        if model_trained:
            model_info = model_data['metadata']

        return render_template(
            'preferences.html',
            user_id=user_id,
            scenarios=scenarios,
            model_trained=model_trained,
            model_info=model_info
        )

    except Exception as e:
        logger.error(f"Error loading preferences page: {e}")
        flash(f"Error loading preferences: {str(e)}", 'error')
        return render_template('preferences.html', error=str(e))


@preference_bp.route('/save', methods=['POST'])
def save_scenarios():
    """
    Save user preference scenarios.

    Expected JSON:
    {
        "user_id": "steve_glen",
        "scenarios": [
            {
                "scenario_name": "Local Edmonton Job",
                "salary": 70000,
                "commute_time_minutes": 20,
                "work_hours_per_week": 40,
                "work_arrangement": 2,
                "acceptance_score": 75
            },
            // ... more scenarios
        ]
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'steve_glen')  # TODO: Get from session
        scenarios = data.get('scenarios', [])

        if not scenarios:
            return jsonify({'success': False, 'error': 'No scenarios provided'}), 400

        if len(scenarios) > 5:
            return jsonify({'success': False, 'error': 'Maximum 5 scenarios allowed'}), 400

        # Validate scenarios
        for i, scenario in enumerate(scenarios):
            if 'acceptance_score' not in scenario:
                return jsonify({
                    'success': False,
                    'error': f'Scenario {i+1} missing acceptance_score'
                }), 400

        # Save scenarios to database
        pref_db = PreferenceDatabase()
        scenario_ids = pref_db.save_scenarios(user_id, scenarios)

        logger.info(f"Saved {len(scenario_ids)} scenarios for user {user_id}")

        return jsonify({
            'success': True,
            'scenario_ids': scenario_ids,
            'message': f'Saved {len(scenario_ids)} scenarios'
        })

    except Exception as e:
        logger.error(f"Error saving scenarios: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@preference_bp.route('/train', methods=['POST'])
def train_model():
    """
    Train preference model from saved scenarios.

    Expected JSON:
    {
        "user_id": "steve_glen"
    }
    """
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'steve_glen')  # TODO: Get from session

        # Load scenarios from database
        pref_db = PreferenceDatabase()
        scenarios = pref_db.get_scenarios(user_id)

        if not scenarios:
            return jsonify({
                'success': False,
                'error': 'No scenarios found. Please add scenarios first.'
            }), 400

        # Extract scenario data and acceptance scores
        scenario_data = []
        acceptance_scores = []

        for scenario in scenarios:
            # Remove metadata fields
            scenario_dict = {k: v for k, v in scenario.items()
                           if k not in ['scenario_id', 'scenario_name', 'created_at', 'updated_at']}

            # Extract acceptance score
            acceptance_score = scenario_dict.pop('acceptance_score', None)
            if acceptance_score is None:
                continue

            scenario_data.append(scenario_dict)
            acceptance_scores.append(float(acceptance_score))

        if len(scenario_data) < 1:
            return jsonify({
                'success': False,
                'error': 'Need at least 1 complete scenario with acceptance_score'
            }), 400

        # Train model
        model = PreferenceRegression(user_id)
        training_result = model.train_from_scenarios(scenario_data, acceptance_scores)

        # Serialize and save model
        model_data = pickle.dumps(model.model)
        scaler_data = pickle.dumps(model.scaler)

        model_id = pref_db.save_model(user_id, model_data, scaler_data, model.model_metadata)

        # Clear cached scorer so it loads new model
        JobScorerFactory.clear_cache()

        logger.info(f"Trained preference model {model_id} for user {user_id}")

        return jsonify({
            'success': True,
            'model_id': model_id,
            'training_result': training_result,
            'formula': model.get_formula_display(),
            'message': f'Model trained successfully with {len(scenario_data)} scenarios'
        })

    except Exception as e:
        logger.error(f"Error training model: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@preference_bp.route('/evaluate', methods=['POST'])
def evaluate_job():
    """
    Evaluate a job against user preferences.

    Expected JSON:
    {
        "user_id": "steve_glen",
        "job": {
            "salary": 75000,
            "commute_time_minutes": 20,
            "work_hours_per_week": 40,
            "work_arrangement": 2,
            "career_growth": 8
            // ... other variables
        }
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'steve_glen')  # TODO: Get from session
        job_data = data.get('job', {})

        if not job_data:
            return jsonify({'success': False, 'error': 'No job data provided'}), 400

        # Get scorer for user
        scorer = JobScorerFactory.get_scorer(user_id)

        # Evaluate job
        evaluation = scorer.evaluate_job(job_data)

        return jsonify({
            'success': True,
            'evaluation': evaluation
        })

    except Exception as e:
        logger.error(f"Error evaluating job: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@preference_bp.route('/model-info')
def model_info():
    """
    Get information about user's trained model.

    Query params:
    - user_id: User identifier (default: steve_glen)
    """
    try:
        user_id = request.args.get('user_id', 'steve_glen')  # TODO: Get from session

        pref_db = PreferenceDatabase()
        model_data = pref_db.load_model(user_id)

        if not model_data:
            return jsonify({
                'success': False,
                'trained': False,
                'message': 'No trained model found'
            })

        # Get formula display
        try:
            scorer = JobScorerFactory.get_scorer(user_id)
            formula = scorer.model.get_formula_display()
            feature_importance = scorer.model._get_feature_importance()
        except:
            formula = "Error loading formula"
            feature_importance = {}

        return jsonify({
            'success': True,
            'trained': True,
            'model_id': model_data['model_id'],
            'metadata': model_data['metadata'],
            'formula': formula,
            'feature_importance': feature_importance
        })

    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@preference_bp.route('/scenarios')
def get_scenarios():
    """
    Get user's saved scenarios.

    Query params:
    - user_id: User identifier (default: steve_glen)
    """
    try:
        user_id = request.args.get('user_id', 'steve_glen')  # TODO: Get from session

        pref_db = PreferenceDatabase()
        scenarios = pref_db.get_scenarios(user_id)

        return jsonify({
            'success': True,
            'scenarios': scenarios,
            'count': len(scenarios)
        })

    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@preference_bp.route('/delete-scenarios', methods=['POST'])
def delete_scenarios():
    """
    Delete user scenarios.

    Expected JSON:
    {
        "user_id": "steve_glen",
        "scenario_ids": ["uuid1", "uuid2"] // optional, deletes all if not provided
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'steve_glen')  # TODO: Get from session
        scenario_ids = data.get('scenario_ids')

        pref_db = PreferenceDatabase()
        count = pref_db.delete_scenarios(user_id, scenario_ids)

        return jsonify({
            'success': True,
            'message': f'Deleted scenarios for user {user_id}'
        })

    except Exception as e:
        logger.error(f"Error deleting scenarios: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@preference_bp.route('/top-jobs')
def top_jobs():
    """
    Get user's top-scored jobs.

    Query params:
    - user_id: User identifier (default: steve_glen)
    - limit: Max number of jobs (default: 20)
    """
    try:
        user_id = request.args.get('user_id', 'steve_glen')  # TODO: Get from session
        limit = int(request.args.get('limit', 20))

        pref_db = PreferenceDatabase()
        jobs = pref_db.get_top_scored_jobs(user_id, limit)

        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })

    except Exception as e:
        logger.error(f"Error getting top jobs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== Error Handlers ====================

@preference_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@preference_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
