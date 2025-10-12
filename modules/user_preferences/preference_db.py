"""
Preference Database Module

Handles database operations for user preference scenarios, trained models,
and job evaluation scores.
"""

import logging
import pickle
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class PreferenceDatabase:
    """
    Database interface for user preference system.

    Handles CRUD operations for scenarios, models, and evaluation scores.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize preference database interface.

        Args:
            db_manager: Optional database manager (creates new if not provided)
        """
        self.db = db_manager or DatabaseManager()

    # ==================== Scenario Operations ====================

    def save_scenarios(self, user_id: str, scenarios: List[Dict[str, Any]]) -> List[str]:
        """
        Save user preference scenarios to database.

        Args:
            user_id: User identifier
            scenarios: List of scenario dictionaries with variables and acceptance_score

        Returns:
            List of scenario IDs created

        Example:
            scenarios = [
                {
                    'scenario_name': 'Local Edmonton Job',
                    'salary': 70000,
                    'commute_time_minutes': 20,
                    'acceptance_score': 75
                },
                # ... more scenarios
            ]
        """
        scenario_ids = []

        for scenario in scenarios:
            try:
                # Deactivate existing scenario with same name if exists
                if scenario.get('scenario_name'):
                    self._deactivate_scenario_by_name(user_id, scenario['scenario_name'])

                # Build insert query dynamically based on provided fields
                fields = ['user_id']
                values = [user_id]
                placeholders = ['%s']

                # Add all provided scenario fields
                for field, value in scenario.items():
                    if field != 'user_id' and value is not None:
                        fields.append(field)
                        values.append(value)
                        placeholders.append('%s')

                query = f"""
                    INSERT INTO user_preference_scenarios ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                    RETURNING scenario_id
                """

                result = self.db.execute_query(query, tuple(values))
                scenario_id = result[0][0] if result else None

                if scenario_id:
                    scenario_ids.append(str(scenario_id))
                    logger.debug(f"Saved scenario {scenario_id} for user {user_id}")

            except Exception as e:
                logger.error(f"Error saving scenario for user {user_id}: {e}")
                raise

        logger.info(f"Saved {len(scenario_ids)} scenarios for user {user_id}")
        return scenario_ids

    def get_scenarios(self, user_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get user's preference scenarios.

        Args:
            user_id: User identifier
            active_only: Only return active scenarios

        Returns:
            List of scenario dictionaries
        """
        query = """
            SELECT scenario_id, scenario_name,
                   -- Core variables
                   salary, job_stress, career_growth, commute_time_minutes,
                   mission_match, industry_preference, work_hours_per_week,
                   work_hour_flexibility, work_arrangement, job_title_match,
                   company_prestige,
                   -- Job characteristics
                   job_type, company_size, team_size, management_responsibilities,
                   -- Benefits & compensation
                   equity_offered, vacation_days, benefits_quality,
                   bonus_potential, professional_development,
                   -- Work-life balance
                   travel_percent, management_autonomy,
                   -- Impact & culture
                   product_stage, social_impact, diversity_culture,
                   -- Contract-specific
                   contract_length_months,
                   -- Meta
                   acceptance_score, created_at, updated_at
            FROM user_preference_scenarios
            WHERE user_id = %s
        """

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY created_at DESC"

        result = self.db.execute_query(query, (user_id,))

        scenarios = []
        for row in result:
            scenario = {
                'scenario_id': str(row[0]),
                'scenario_name': row[1],
                'created_at': row[29].isoformat() if row[29] else None,
                'updated_at': row[30].isoformat() if row[30] else None
            }

            # Add non-null preference variables (in same order as SELECT)
            variables = [
                # Core (indices 2-12)
                ('salary', row[2]),
                ('job_stress', row[3]),
                ('career_growth', row[4]),
                ('commute_time_minutes', row[5]),
                ('mission_match', row[6]),
                ('industry_preference', row[7]),
                ('work_hours_per_week', row[8]),
                ('work_hour_flexibility', row[9]),
                ('work_arrangement', row[10]),
                ('job_title_match', row[11]),
                ('company_prestige', row[12]),
                # Job characteristics (indices 13-16)
                ('job_type', row[13]),
                ('company_size', row[14]),
                ('team_size', row[15]),
                ('management_responsibilities', row[16]),
                # Benefits (indices 17-21)
                ('equity_offered', row[17]),
                ('vacation_days', row[18]),
                ('benefits_quality', row[19]),
                ('bonus_potential', row[20]),
                ('professional_development', row[21]),
                # Work-life (indices 22-23)
                ('travel_percent', row[22]),
                ('management_autonomy', row[23]),
                # Impact (indices 24-26)
                ('product_stage', row[24]),
                ('social_impact', row[25]),
                ('diversity_culture', row[26]),
                # Contract (index 27)
                ('contract_length_months', row[27]),
                # Acceptance score (index 28)
                ('acceptance_score', row[28])
            ]

            for var_name, var_value in variables:
                if var_value is not None:
                    scenario[var_name] = float(var_value)

            scenarios.append(scenario)

        return scenarios

    def _deactivate_scenario_by_name(self, user_id: str, scenario_name: str) -> None:
        """Deactivate existing scenario with same name"""
        query = """
            UPDATE user_preference_scenarios
            SET is_active = FALSE
            WHERE user_id = %s AND scenario_name = %s AND is_active = TRUE
        """
        self.db.execute_query(query, (user_id, scenario_name))

    def delete_scenarios(self, user_id: str, scenario_ids: Optional[List[str]] = None) -> int:
        """
        Delete (deactivate) user scenarios.

        Args:
            user_id: User identifier
            scenario_ids: Optional list of specific scenario IDs to delete
                         (if None, deletes all user scenarios)

        Returns:
            Number of scenarios deleted
        """
        if scenario_ids:
            query = """
                UPDATE user_preference_scenarios
                SET is_active = FALSE
                WHERE user_id = %s AND scenario_id = ANY(%s)
            """
            self.db.execute_query(query, (user_id, scenario_ids))
            count = len(scenario_ids)
        else:
            query = """
                UPDATE user_preference_scenarios
                SET is_active = FALSE
                WHERE user_id = %s
            """
            self.db.execute_query(query, (user_id,))
            count = -1  # Unknown count

        logger.info(f"Deleted scenarios for user {user_id}")
        return count

    # ==================== Model Operations ====================

    def save_model(self, user_id: str, model_data: bytes, scaler_data: bytes,
                   metadata: Dict[str, Any]) -> str:
        """
        Save trained preference model to database.

        Args:
            user_id: User identifier
            model_data: Serialized sklearn model (pickle)
            scaler_data: Serialized StandardScaler (pickle)
            metadata: Model metadata dict with:
                - model_type: 'Ridge' or 'RandomForest'
                - feature_names: List of feature names
                - num_scenarios: Number of training scenarios
                - train_r2: Training R² score
                - mean_acceptance: Mean acceptance score
                - std_acceptance: Std of acceptance scores
                - feature_importance: Dict of feature weights

        Returns:
            Model ID
        """
        try:
            query = """
                INSERT INTO user_preference_models (
                    user_id, model_type, feature_names, num_scenarios,
                    model_data, scaler_data, train_r2, mean_acceptance,
                    std_acceptance, feature_importance, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING model_id
            """

            params = (
                user_id,
                metadata['model_type'],
                metadata['feature_names'],
                metadata['num_scenarios'],
                model_data,
                scaler_data,
                metadata.get('train_r2'),
                metadata.get('mean_acceptance'),
                metadata.get('std_acceptance'),
                json.dumps(metadata.get('feature_importance', {}))
            )

            result = self.db.execute_query(query, params)
            model_id = str(result[0][0]) if result else None

            logger.info(f"Saved preference model {model_id} for user {user_id}")
            return model_id

        except Exception as e:
            logger.error(f"Error saving model for user {user_id}: {e}")
            raise

    def load_model(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load user's active preference model.

        Args:
            user_id: User identifier

        Returns:
            Dict with model data or None if no model exists:
                - model_id: UUID
                - model_data: Serialized model bytes
                - scaler_data: Serialized scaler bytes
                - metadata: Model metadata dict
        """
        query = """
            SELECT model_id, model_data, scaler_data, model_type,
                   feature_names, num_scenarios, train_r2, mean_acceptance,
                   std_acceptance, feature_importance, trained_at
            FROM user_preference_models
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY trained_at DESC
            LIMIT 1
        """

        result = self.db.execute_query(query, (user_id,))

        if not result:
            return None

        row = result[0]
        return {
            'model_id': str(row[0]),
            'model_data': bytes(row[1]),
            'scaler_data': bytes(row[2]),
            'metadata': {
                'model_type': row[3],
                'feature_names': row[4],
                'num_scenarios': row[5],
                'train_r2': float(row[6]) if row[6] else None,
                'mean_acceptance': float(row[7]) if row[7] else None,
                'std_acceptance': float(row[8]) if row[8] else None,
                'feature_importance': row[9] if row[9] else {},
                'trained_at': row[10].isoformat() if row[10] else None,
                'user_id': user_id
            }
        }

    # ==================== Score Operations ====================

    def save_job_score(self, job_id: str, user_id: str, evaluation: Dict[str, Any],
                       model_id: Optional[str] = None) -> None:
        """
        Save job evaluation score to database.

        Args:
            job_id: Job identifier
            user_id: User identifier
            evaluation: Evaluation result dict from JobScorer
            model_id: Optional model ID used for evaluation
        """
        try:
            query = """
                INSERT INTO job_preference_scores (
                    job_id, user_id, acceptance_score, should_apply,
                    confidence, explanation, model_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id, user_id) DO UPDATE SET
                    acceptance_score = EXCLUDED.acceptance_score,
                    should_apply = EXCLUDED.should_apply,
                    confidence = EXCLUDED.confidence,
                    explanation = EXCLUDED.explanation,
                    model_id = EXCLUDED.model_id,
                    evaluated_at = CURRENT_TIMESTAMP
            """

            params = (
                job_id,
                user_id,
                evaluation['acceptance_score'],
                evaluation['should_apply'],
                evaluation.get('confidence'),
                json.dumps(evaluation.get('explanation', [])),
                model_id
            )

            self.db.execute_query(query, params)
            logger.debug(f"Saved job score for job {job_id}, user {user_id}")

        except Exception as e:
            logger.error(f"Error saving job score: {e}")

    def get_job_score(self, job_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached job evaluation score.

        Args:
            job_id: Job identifier
            user_id: User identifier

        Returns:
            Evaluation dict or None if not found
        """
        query = """
            SELECT acceptance_score, should_apply, confidence,
                   explanation, evaluated_at, model_id
            FROM job_preference_scores
            WHERE job_id = %s AND user_id = %s
        """

        result = self.db.execute_query(query, (job_id, user_id))

        if not result:
            return None

        row = result[0]
        return {
            'acceptance_score': float(row[0]),
            'should_apply': row[1],
            'confidence': float(row[2]) if row[2] else None,
            'explanation': row[3] if row[3] else [],
            'evaluated_at': row[4].isoformat() if row[4] else None,
            'model_id': str(row[5]) if row[5] else None
        }

    def get_top_scored_jobs(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get user's top-scored jobs.

        Args:
            user_id: User identifier
            limit: Max number of jobs to return

        Returns:
            List of job score dicts
        """
        query = """
            SELECT job_id, acceptance_score, should_apply, confidence,
                   explanation, evaluated_at
            FROM job_preference_scores
            WHERE user_id = %s AND should_apply = TRUE
            ORDER BY acceptance_score DESC, confidence DESC
            LIMIT %s
        """

        result = self.db.execute_query(query, (user_id, limit))

        jobs = []
        for row in result:
            jobs.append({
                'job_id': row[0],
                'acceptance_score': float(row[1]),
                'should_apply': row[2],
                'confidence': float(row[3]) if row[3] else None,
                'explanation': row[4] if row[4] else [],
                'evaluated_at': row[5].isoformat() if row[5] else None
            })

        return jobs
