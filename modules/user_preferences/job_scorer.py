"""
Job Scorer Module

Evaluates job opportunities against user's learned preferences using the
trained regression model. Provides binary accept/reject decisions with
confidence scores and explanations.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .preference_regression import PreferenceRegression
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class JobScorer:
    """
    Evaluates job opportunities against user preferences.

    Loads user's trained preference model and scores incoming jobs
    to determine if they meet minimum acceptance criteria.
    """

    def __init__(self, user_id: str, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize job scorer for a user.

        Args:
            user_id: Unique user identifier
            db_manager: Optional database manager (creates new if not provided)
        """
        self.user_id = user_id
        self.db = db_manager or DatabaseManager()
        self.model = PreferenceRegression(user_id)
        self._load_user_model()

    def _load_user_model(self) -> None:
        """
        Load user's trained preference model from database.

        Raises:
            ValueError: If no trained model exists for user
        """
        try:
            # Query for user's most recent preference model
            query = """
                SELECT model_data, feature_names, metadata
                FROM user_preference_models
                WHERE user_id = %s
                ORDER BY trained_at DESC
                LIMIT 1
            """

            result = self.db.execute_query(query, (self.user_id,))

            if not result:
                raise ValueError(f"No preference model found for user {self.user_id}")

            # Load model data
            model_row = result[0]
            # Model will be loaded from serialized data in Phase 3
            logger.info(f"Loaded preference model for user {self.user_id}")

        except Exception as e:
            logger.warning(f"Could not load preference model for user {self.user_id}: {e}")
            # Model not trained yet - this is expected for new users

    def evaluate_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a job opportunity against user preferences.

        Args:
            job_data: Job dictionary with preference variables:
                Core:
                - salary (int): Annual salary
                - job_stress (1-10): Estimated stress level (lower is better)
                - career_growth (1-10): Growth opportunity
                - commute_time_minutes (int): Commute time (lower is better)
                - mission_match (1-10): Mission alignment
                - industry_preference (1-10): Industry match
                - work_hours_per_week (int): Expected hours (lower is better)
                - work_hour_flexibility (1-10): Schedule flexibility
                - work_arrangement (1-3): 1=onsite, 2=hybrid, 3=remote
                - job_title_match (1-10): Title match
                - company_prestige (1-10): Company reputation

                Job Characteristics:
                - job_type (1-3): 1=part-time, 2=contract, 3=full-time
                - company_size (1-5): 1=startup, 2=small, 3=medium, 4=large, 5=enterprise
                - team_size (int): Number of people on team
                - management_responsibilities (1-10): 1=no supervision, 10=large team

                Benefits & Compensation:
                - equity_offered (1-10): Equity/stock options
                - vacation_days (int): Days per year
                - benefits_quality (1-10): Health, dental, vision
                - bonus_potential (0-100): Percent of salary
                - professional_development (1-10): Training/conference budget

                Work-Life Balance:
                - travel_percent (0-100): Percent time traveling (lower is better)
                - management_autonomy (1-10): 1=micromanaged, 10=autonomous

                Impact & Culture:
                - product_stage (1-10): 1=early/greenfield, 10=mature/maintenance
                - social_impact (1-10): Social/environmental impact
                - diversity_culture (1-10): D&I culture

                Contract-Specific:
                - contract_length_months (int): For contract roles

        Returns:
            Dict with evaluation results:
                - should_apply (bool): Whether to apply
                - acceptance_score (float): 0-100 score
                - confidence (float): 0-1 confidence in decision
                - explanation (list): Human-readable reasons
                - evaluated_at (str): Timestamp

        Example:
            job = {
                'salary': 75000,
                'commute_time_minutes': 20,
                'work_hours_per_week': 40,
                'work_arrangement': 2,  # hybrid
                'career_growth': 8,
                'vacation_days': 15,
                'benefits_quality': 7,
                'management_responsibilities': 3,  # some supervision
                'equity_offered': 5,
                'professional_development': 8
            }
            result = scorer.evaluate_job(job)
            if result['should_apply']:
                # Proceed with application
        """
        try:
            # Predict acceptance using regression model
            prediction = self.model.predict_acceptance(job_data)

            # Build result
            result = {
                'should_apply': prediction['accepted'],
                'acceptance_score': prediction['acceptance_score'],
                'threshold': prediction['threshold'],
                'confidence': prediction['confidence'],
                'explanation': prediction['explanation'],
                'evaluated_at': datetime.utcnow().isoformat(),
                'user_id': self.user_id
            }

            # Log decision
            decision = "APPLY" if result['should_apply'] else "SKIP"
            logger.info(
                f"Job evaluation for {self.user_id}: {decision} "
                f"(score={result['acceptance_score']:.1f}, confidence={result['confidence']:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"Error evaluating job for user {self.user_id}: {e}")
            # Return safe default (don't apply if error)
            return {
                'should_apply': False,
                'acceptance_score': 0,
                'confidence': 0,
                'explanation': [f"Error evaluating job: {str(e)}"],
                'evaluated_at': datetime.utcnow().isoformat(),
                'user_id': self.user_id,
                'error': True
            }

    def evaluate_job_batch(self, jobs: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Evaluate multiple jobs efficiently.

        Args:
            jobs: List of job dictionaries

        Returns:
            List of evaluation results
        """
        return [self.evaluate_job(job) for job in jobs]

    def get_acceptance_threshold(self) -> float:
        """
        Get user's acceptance threshold.

        Returns:
            Acceptance threshold score (0-100)
        """
        return self.model.model_metadata.get('mean_acceptance', 50)

    def explain_preferences(self) -> Dict[str, Any]:
        """
        Get explanation of user's learned preferences.

        Returns:
            Dict with preference explanation:
                - formula: Human-readable formula
                - feature_importance: Dict of feature weights
                - training_stats: Model training statistics
        """
        if self.model.model is None:
            return {
                'formula': 'No preferences learned yet',
                'feature_importance': {},
                'training_stats': {}
            }

        feature_importance = self.model._get_feature_importance()

        return {
            'formula': self.model.get_formula_display(),
            'feature_importance': feature_importance,
            'training_stats': {
                'num_scenarios': self.model.model_metadata.get('num_scenarios', 0),
                'model_type': self.model.model_metadata.get('model_type', 'Unknown'),
                'train_r2': self.model.model_metadata.get('train_r2', 0),
                'trained_at': self.model.model_metadata.get('trained_at', 'Never')
            }
        }

    def save_evaluation_to_db(self, job_id: str, evaluation: Dict[str, Any]) -> None:
        """
        Save job evaluation result to database for tracking.

        Args:
            job_id: Unique job identifier
            evaluation: Evaluation result from evaluate_job()
        """
        try:
            query = """
                INSERT INTO job_preference_scores (
                    job_id, user_id, acceptance_score, should_apply,
                    confidence, explanation, evaluated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id, user_id) DO UPDATE SET
                    acceptance_score = EXCLUDED.acceptance_score,
                    should_apply = EXCLUDED.should_apply,
                    confidence = EXCLUDED.confidence,
                    explanation = EXCLUDED.explanation,
                    evaluated_at = EXCLUDED.evaluated_at
            """

            params = (
                job_id,
                self.user_id,
                evaluation['acceptance_score'],
                evaluation['should_apply'],
                evaluation['confidence'],
                str(evaluation['explanation']),
                evaluation['evaluated_at']
            )

            self.db.execute_query(query, params)
            logger.debug(f"Saved evaluation for job {job_id}")

        except Exception as e:
            logger.error(f"Error saving evaluation to database: {e}")


class JobScorerFactory:
    """
    Factory for creating and caching JobScorer instances.

    Prevents recreating scorer objects for the same user repeatedly.
    """

    _scorers = {}

    @classmethod
    def get_scorer(cls, user_id: str, db_manager: Optional[DatabaseManager] = None) -> JobScorer:
        """
        Get or create JobScorer for user.

        Args:
            user_id: User identifier
            db_manager: Optional database manager

        Returns:
            JobScorer instance
        """
        if user_id not in cls._scorers:
            cls._scorers[user_id] = JobScorer(user_id, db_manager)
        return cls._scorers[user_id]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached scorers (useful after model updates)"""
        cls._scorers.clear()
        logger.info("Cleared JobScorer cache")


def evaluate_job_for_user(user_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to evaluate a job for a user.

    Args:
        user_id: User identifier
        job_data: Job dictionary with preference variables

    Returns:
        Evaluation result

    Example:
        result = evaluate_job_for_user('steve_glen', {
            'salary': 75000,
            'commute_time_minutes': 20,
            'work_arrangement': 2
        })
    """
    scorer = JobScorerFactory.get_scorer(user_id)
    return scorer.evaluate_job(job_data)
