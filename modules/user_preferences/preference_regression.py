"""
Preference Regression Engine

Multi-variable regression system that learns user job preferences from 1-5 sample scenarios.
Infers trade-offs between factors like salary, commute, work hours, etc., and generates
a mathematical model for evaluating job opportunities.

Variables supported:
- salary (numeric)
- job_stress (1-10 scale, lower is better)
- career_growth (1-10 scale)
- commute_time_minutes (numeric, lower is better)
- mission_match (1-10 scale)
- industry_preference (1-10 scale)
- work_hours_per_week (numeric, lower is better)
- work_hour_flexibility (1-10 scale)
- work_arrangement (1=onsite, 2=hybrid, 3=remote)
- job_title_match (1-10 scale)
- company_prestige (1-10 scale)
- job_type (1=part-time, 2=contract, 3=full-time)
- company_size (1=startup, 2=small, 3=medium, 4=large, 5=enterprise)
- equity_offered (1-10 scale)
- vacation_days (numeric, days per year)
- benefits_quality (1-10 scale)
- team_size (numeric, number of direct reports/peers)
- travel_percent (0-100, percent time traveling, lower is better)
- professional_development (1-10 scale, training/conference budget)
- management_responsibilities (1-10 scale, 1=no supervision, 10=large team management)
- bonus_potential (0-100, percent of salary)
- product_stage (1-10 scale, 1=early/greenfield, 10=mature/maintenance)
- management_autonomy (1-10 scale, 1=micromanaged, 10=autonomous)
- social_impact (1-10 scale)
- diversity_culture (1-10 scale)
- contract_length_months (numeric, for contract roles)
"""

import logging
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
import joblib

logger = logging.getLogger(__name__)


class PreferenceRegression:
    """
    Multi-variable regression engine for learning user job preferences.

    Handles 1-5 user scenarios describing minimum acceptable jobs, then uses
    regression to infer trade-offs and generate acceptance threshold formula.
    """

    # All supported preference variables
    PREFERENCE_VARIABLES = [
        # Core compensation & work
        'salary',
        'job_stress',
        'career_growth',
        'commute_time_minutes',
        'mission_match',
        'industry_preference',
        'work_hours_per_week',
        'work_hour_flexibility',
        'work_arrangement',  # 1=onsite, 2=hybrid, 3=remote
        'job_title_match',
        'company_prestige',

        # Job characteristics
        'job_type',  # 1=part-time, 2=contract, 3=full-time
        'company_size',  # 1=startup, 2=small, 3=medium, 4=large, 5=enterprise
        'team_size',  # Number of people on team
        'management_responsibilities',  # 1-10 scale (1=no supervision, 10=large team)

        # Benefits & compensation
        'equity_offered',  # 1-10 scale
        'vacation_days',  # Days per year
        'benefits_quality',  # 1-10 scale (health, dental, vision)
        'bonus_potential',  # 0-100 percent of salary
        'professional_development',  # 1-10 scale (training budget, conferences)

        # Work-life balance
        'travel_percent',  # 0-100 percent time traveling
        'management_autonomy',  # 1-10 scale (1=micromanaged, 10=autonomous)

        # Impact & culture
        'product_stage',  # 1-10 (1=early/greenfield, 10=mature/maintenance)
        'social_impact',  # 1-10 scale
        'diversity_culture',  # 1-10 scale

        # Contract-specific
        'contract_length_months',  # For contract roles
    ]

    # Variables that should be inverted (lower is better)
    INVERSE_VARIABLES = [
        'job_stress',
        'commute_time_minutes',
        'work_hours_per_week',
        'travel_percent'
    ]

    def __init__(self, user_id: str):
        """
        Initialize preference regression for a user.

        Args:
            user_id: Unique user identifier
        """
        self.user_id = user_id
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_metadata = {}

    def train_from_scenarios(self, scenarios: List[Dict[str, Any]], acceptance_scores: List[float]) -> Dict:
        """
        Train regression model from user scenarios.

        Args:
            scenarios: List of 1-5 scenario dictionaries with variable values
            acceptance_scores: User's acceptance rating for each scenario (0-100)
                              e.g., [70, 85, 60, 95, 50] means scenario 0 is 70% acceptable

        Returns:
            Dict with training results and model statistics

        Example:
            scenarios = [
                {
                    'salary': 70000,
                    'commute_time_minutes': 30,
                    'work_hours_per_week': 40,
                    'work_arrangement': 2,  # hybrid
                    'career_growth': 7,
                    # ... other variables (optional)
                },
                # ... more scenarios
            ]
            acceptance_scores = [75, 85, 60]  # User's acceptance for each scenario
        """
        if not scenarios or len(scenarios) < 1:
            raise ValueError("Must provide at least 1 scenario")

        if len(scenarios) > 5:
            raise ValueError("Maximum 5 scenarios allowed")

        if len(scenarios) != len(acceptance_scores):
            raise ValueError("Number of scenarios must match number of acceptance scores")

        # Normalize and prepare feature matrix
        X, feature_names = self._prepare_features(scenarios)
        y = np.array(acceptance_scores)

        # Store feature names for later use
        self.feature_names = feature_names

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Choose model based on scenario count
        if len(scenarios) <= 2:
            # Use Ridge regression for small datasets (less overfitting)
            self.model = Ridge(alpha=1.0)
        else:
            # Use Random Forest for 3+ scenarios (captures non-linear relationships)
            self.model = RandomForestRegressor(
                n_estimators=50,
                max_depth=3,
                min_samples_split=2,
                random_state=42
            )

        # Train model
        self.model.fit(X_scaled, y)

        # Calculate training metrics
        train_predictions = self.model.predict(X_scaled)
        train_r2 = self._calculate_r2(y, train_predictions)

        # Store metadata
        self.model_metadata = {
            'user_id': self.user_id,
            'num_scenarios': len(scenarios),
            'feature_names': feature_names,
            'train_r2': float(train_r2),
            'mean_acceptance': float(np.mean(y)),
            'std_acceptance': float(np.std(y)),
            'trained_at': datetime.utcnow().isoformat(),
            'model_type': 'Ridge' if len(scenarios) <= 2 else 'RandomForest'
        }

        # Extract feature importance/coefficients
        feature_importance = self._get_feature_importance()

        logger.info(f"Trained preference model for user {self.user_id} with {len(scenarios)} scenarios (R²={train_r2:.3f})")

        return {
            'success': True,
            'model_type': self.model_metadata['model_type'],
            'train_r2': train_r2,
            'feature_importance': feature_importance,
            'metadata': self.model_metadata
        }

    def _prepare_features(self, scenarios: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[str]]:
        """
        Prepare feature matrix from scenarios, handling missing variables.

        Args:
            scenarios: List of scenario dictionaries

        Returns:
            Tuple of (feature_matrix, feature_names)
        """
        # Determine which features are present across scenarios
        present_features = set()
        for scenario in scenarios:
            present_features.update(scenario.keys())

        # Filter to only supported variables
        present_features = [f for f in self.PREFERENCE_VARIABLES if f in present_features]

        if not present_features:
            raise ValueError("No valid preference variables found in scenarios")

        # Build feature matrix
        X = []
        for scenario in scenarios:
            row = []
            for feature in present_features:
                value = scenario.get(feature, None)

                if value is None:
                    # Use neutral middle value for missing variables
                    if feature in ['salary', 'commute_time_minutes', 'work_hours_per_week',
                                   'vacation_days', 'team_size', 'contract_length_months']:
                        value = 0  # Numeric variables will be handled with normalization
                    elif feature in ['travel_percent', 'bonus_potential']:
                        value = 0  # Percentage variables default to 0
                    elif feature == 'job_type':
                        value = 3  # Default to full-time
                    elif feature == 'company_size':
                        value = 3  # Default to medium
                    else:
                        value = 5  # Middle of 1-10 scale

                # Invert variables where lower is better
                if feature in self.INVERSE_VARIABLES:
                    if feature == 'commute_time_minutes':
                        # Invert: 0 minutes = 10, 60 minutes = 0
                        inverted = max(0, 10 - (float(value) / 60.0) * 10)
                        row.append(inverted)
                    elif feature == 'work_hours_per_week':
                        # Invert: 40 hours = 5, 60 hours = 0, 20 hours = 10
                        inverted = max(0, 10 - ((float(value) - 20) / 40.0) * 10)
                        row.append(inverted)
                    elif feature == 'travel_percent':
                        # Invert: 0% = 10, 100% = 0
                        inverted = max(0, 10 - (float(value) / 10.0))
                        row.append(inverted)
                    elif feature == 'job_stress':
                        # Already 1-10 scale, just invert
                        row.append(10 - float(value))
                    else:
                        # Generic invert for any other inverse variables
                        row.append(10 - float(value))
                else:
                    row.append(float(value))

            X.append(row)

        return np.array(X), present_features

    def predict_acceptance(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict acceptance score for a job opportunity.

        Args:
            job: Job dictionary with preference variables

        Returns:
            Dict with acceptance score and explanation
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_from_scenarios() first.")

        # Ensure job has same features as training data (fill missing with None)
        aligned_job = {}
        for feature in self.feature_names:
            aligned_job[feature] = job.get(feature, None)

        # Prepare features (will use same feature order as training)
        X_job, _ = self._prepare_features([aligned_job])
        X_scaled = self.scaler.transform(X_job)

        # Predict
        acceptance_score = float(self.model.predict(X_scaled)[0])

        # Clamp to 0-100 range
        acceptance_score = max(0, min(100, acceptance_score))

        # Determine acceptance decision (threshold at 50)
        threshold = self.model_metadata.get('mean_acceptance', 50)
        accepted = acceptance_score >= threshold

        # Generate explanation
        explanation = self._generate_explanation(job, acceptance_score)

        return {
            'acceptance_score': acceptance_score,
            'accepted': accepted,
            'threshold': threshold,
            'confidence': self._calculate_confidence(acceptance_score, threshold),
            'explanation': explanation
        }

    def _get_feature_importance(self) -> Dict[str, float]:
        """
        Extract feature importance from trained model.

        Returns:
            Dict mapping feature names to importance scores
        """
        if self.model is None:
            return {}

        if hasattr(self.model, 'feature_importances_'):
            # Random Forest
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            # Ridge regression
            importances = np.abs(self.model.coef_)
        else:
            return {}

        # Normalize to sum to 1
        importances = importances / np.sum(importances)

        return {name: float(importance)
                for name, importance in zip(self.feature_names, importances)}

    def _generate_explanation(self, job: Dict[str, Any], score: float) -> List[str]:
        """
        Generate human-readable explanation for acceptance score.

        Args:
            job: Job dictionary
            score: Predicted acceptance score

        Returns:
            List of explanation strings
        """
        explanation = []
        feature_importance = self._get_feature_importance()

        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

        # Explain top 3 most important factors
        for feature_name, importance in sorted_features[:3]:
            if importance < 0.1:  # Skip features with <10% importance
                continue

            value = job.get(feature_name)
            if value is not None:
                explanation.append(self._format_factor_explanation(feature_name, value, importance))

        return explanation

    def _format_factor_explanation(self, feature: str, value: Any, importance: float) -> str:
        """
        Format explanation for a single factor.

        Args:
            feature: Feature name
            value: Feature value
            importance: Feature importance (0-1)

        Returns:
            Formatted explanation string
        """
        importance_pct = int(importance * 100)

        # Numeric/currency values
        if feature == 'salary':
            return f"Salary ${value:,.0f} ({importance_pct}% weight)"
        elif feature == 'bonus_potential':
            return f"Bonus potential {value}% of salary ({importance_pct}% weight)"

        # Time/duration values
        elif feature == 'commute_time_minutes':
            return f"Commute {value} minutes ({importance_pct}% weight)"
        elif feature == 'work_hours_per_week':
            return f"Work hours {value}/week ({importance_pct}% weight)"
        elif feature == 'vacation_days':
            return f"Vacation {value} days/year ({importance_pct}% weight)"
        elif feature == 'contract_length_months':
            return f"Contract length {value} months ({importance_pct}% weight)"

        # Percentage values
        elif feature == 'travel_percent':
            return f"Travel {value}% of time ({importance_pct}% weight)"

        # Categorical values
        elif feature == 'work_arrangement':
            arrangement = {1: 'On-site', 2: 'Hybrid', 3: 'Remote'}.get(int(value), 'Unknown')
            return f"Work arrangement: {arrangement} ({importance_pct}% weight)"
        elif feature == 'job_type':
            job_type = {1: 'Part-time', 2: 'Contract', 3: 'Full-time'}.get(int(value), 'Unknown')
            return f"Job type: {job_type} ({importance_pct}% weight)"
        elif feature == 'company_size':
            size = {1: 'Startup', 2: 'Small', 3: 'Medium', 4: 'Large', 5: 'Enterprise'}.get(int(value), 'Unknown')
            return f"Company size: {size} ({importance_pct}% weight)"

        # Count values
        elif feature == 'team_size':
            return f"Team size: {int(value)} people ({importance_pct}% weight)"

        # 1-10 scale values with specific names
        elif feature == 'management_responsibilities':
            level = "No supervision" if value <= 2 else "Some supervision" if value <= 5 else "Team lead" if value <= 7 else "Manager"
            return f"Management: {level} ({value}/10, {importance_pct}% weight)"
        elif feature == 'product_stage':
            stage = "Early/Greenfield" if value <= 3 else "Growth" if value <= 7 else "Mature/Maintenance"
            return f"Product stage: {stage} ({value}/10, {importance_pct}% weight)"

        # Generic 1-10 scale values
        else:
            return f"{feature.replace('_', ' ').title()}: {value}/10 ({importance_pct}% weight)"

    def _calculate_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R² score"""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    def _calculate_confidence(self, score: float, threshold: float) -> float:
        """
        Calculate confidence in the accept/reject decision.

        Args:
            score: Predicted acceptance score
            threshold: Acceptance threshold

        Returns:
            Confidence score (0-1)
        """
        # Confidence is higher when score is far from threshold
        distance = abs(score - threshold)
        max_distance = 50  # Max distance from threshold (0-100 range)
        return min(1.0, distance / max_distance)

    def save_model(self, filepath: str) -> None:
        """
        Save trained model to file.

        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metadata': self.model_metadata
        }

        joblib.dump(model_data, filepath)
        logger.info(f"Saved preference model to {filepath}")

    def load_model(self, filepath: str) -> None:
        """
        Load trained model from file.

        Args:
            filepath: Path to load model from
        """
        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_metadata = model_data['metadata']

        logger.info(f"Loaded preference model from {filepath}")

    def get_formula_display(self) -> str:
        """
        Get human-readable formula representation.

        Returns:
            String representation of the preference formula
        """
        if self.model is None:
            return "No model trained yet"

        feature_importance = self._get_feature_importance()
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

        formula_parts = []
        for feature_name, importance in sorted_features:
            weight = int(importance * 100)
            if weight < 5:  # Skip features with <5% importance
                continue
            formula_parts.append(f"{feature_name.replace('_', ' ').title()} ({weight}%)")

        return "Acceptance Score = " + " + ".join(formula_parts)
