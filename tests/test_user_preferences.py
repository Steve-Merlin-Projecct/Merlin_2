"""
Test Suite for User Preferences System

Tests multi-variable regression preference learning and job evaluation.
"""

import pytest
import numpy as np
from modules.user_preferences.preference_regression import PreferenceRegression
from modules.user_preferences.job_scorer import JobScorer


class TestPreferenceRegression:
    """Test preference regression engine"""

    def test_train_single_scenario(self):
        """Test training with single scenario"""
        model = PreferenceRegression("test_user")

        scenarios = [
            {
                'salary': 70000,
                'commute_time_minutes': 20,
                'work_hours_per_week': 40,
                'work_arrangement': 2,  # hybrid
                'career_growth': 7
            }
        ]
        acceptance_scores = [75]

        result = model.train_from_scenarios(scenarios, acceptance_scores)

        assert result['success'] is True
        assert result['model_type'] in ['Ridge', 'RandomForest']
        assert model.model is not None

    def test_train_multiple_scenarios(self):
        """Test training with 3 scenarios"""
        model = PreferenceRegression("test_user")

        scenarios = [
            {
                'salary': 70000,
                'commute_time_minutes': 20,
                'work_hours_per_week': 40,
                'career_growth': 7,
                'acceptance_score': 75
            },
            {
                'salary': 90000,
                'commute_time_minutes': 60,
                'work_hours_per_week': 45,
                'career_growth': 8,
                'acceptance_score': 85
            },
            {
                'salary': 60000,
                'commute_time_minutes': 10,
                'work_hours_per_week': 35,
                'career_growth': 6,
                'acceptance_score': 65
            }
        ]

        # Extract acceptance scores
        acceptance_scores = [s.pop('acceptance_score') for s in scenarios]

        result = model.train_from_scenarios(scenarios, acceptance_scores)

        assert result['success'] is True
        assert result['model_type'] == 'RandomForest'
        assert len(result['feature_importance']) > 0

    def test_predict_acceptance(self):
        """Test job acceptance prediction"""
        model = PreferenceRegression("test_user")

        # Train with scenarios
        scenarios = [
            {'salary': 70000, 'commute_time_minutes': 20, 'career_growth': 7},
            {'salary': 90000, 'commute_time_minutes': 60, 'career_growth': 8},
            {'salary': 60000, 'commute_time_minutes': 10, 'career_growth': 6}
        ]
        acceptance_scores = [75, 85, 65]

        model.train_from_scenarios(scenarios, acceptance_scores)

        # Predict similar job
        job = {
            'salary': 75000,
            'commute_time_minutes': 25,
            'career_growth': 7
        }

        prediction = model.predict_acceptance(job)

        assert 'acceptance_score' in prediction
        assert 'accepted' in prediction
        assert 'confidence' in prediction
        assert 'explanation' in prediction
        assert 0 <= prediction['acceptance_score'] <= 100
        assert isinstance(prediction['accepted'], bool)

    def test_handle_missing_variables(self):
        """Test handling of missing variables"""
        model = PreferenceRegression("test_user")

        scenarios = [
            {
                'salary': 70000,
                'commute_time_minutes': 20,
                # Missing other variables
            },
            {
                'salary': 90000,
                'work_hours_per_week': 45,
                # Different missing variables
            }
        ]
        acceptance_scores = [70, 80]

        result = model.train_from_scenarios(scenarios, acceptance_scores)
        assert result['success'] is True

    def test_too_many_scenarios(self):
        """Test error when >5 scenarios provided"""
        model = PreferenceRegression("test_user")

        scenarios = [{'salary': i * 10000} for i in range(6)]
        acceptance_scores = list(range(6))

        with pytest.raises(ValueError, match="Maximum 5 scenarios"):
            model.train_from_scenarios(scenarios, acceptance_scores)

    def test_no_scenarios(self):
        """Test error when no scenarios provided"""
        model = PreferenceRegression("test_user")

        with pytest.raises(ValueError, match="at least 1 scenario"):
            model.train_from_scenarios([], [])

    def test_feature_importance(self):
        """Test feature importance extraction"""
        model = PreferenceRegression("test_user")

        scenarios = [
            {'salary': 70000, 'commute_time_minutes': 20},
            {'salary': 90000, 'commute_time_minutes': 60},
            {'salary': 60000, 'commute_time_minutes': 10}
        ]
        acceptance_scores = [75, 60, 85]  # Lower commute = higher acceptance

        model.train_from_scenarios(scenarios, acceptance_scores)
        importance = model._get_feature_importance()

        assert len(importance) == 2
        assert 'salary' in importance
        assert 'commute_time_minutes' in importance
        assert all(0 <= v <= 1 for v in importance.values())

    def test_formula_display(self):
        """Test human-readable formula generation"""
        model = PreferenceRegression("test_user")

        scenarios = [
            {'salary': 70000, 'career_growth': 7},
            {'salary': 90000, 'career_growth': 8}
        ]
        acceptance_scores = [70, 80]

        model.train_from_scenarios(scenarios, acceptance_scores)
        formula = model.get_formula_display()

        assert "Acceptance Score" in formula
        assert isinstance(formula, str)


class TestJobScorer:
    """Test job scorer"""

    @pytest.fixture
    def trained_scorer(self):
        """Create scorer with trained model"""
        model = PreferenceRegression("test_user")

        scenarios = [
            {
                'salary': 70000,
                'commute_time_minutes': 20,
                'work_hours_per_week': 40,
                'career_growth': 7
            },
            {
                'salary': 90000,
                'commute_time_minutes': 60,
                'work_hours_per_week': 45,
                'career_growth': 8
            },
            {
                'salary': 60000,
                'commute_time_minutes': 10,
                'work_hours_per_week': 35,
                'career_growth': 6
            }
        ]
        acceptance_scores = [75, 70, 80]

        model.train_from_scenarios(scenarios, acceptance_scores)

        # Create scorer (note: this won't have DB access in unit test)
        scorer = JobScorer.__new__(JobScorer)
        scorer.user_id = "test_user"
        scorer.model = model
        scorer.db = None

        return scorer

    def test_evaluate_good_job(self, trained_scorer):
        """Test evaluation of good job match"""
        job = {
            'salary': 75000,
            'commute_time_minutes': 15,
            'work_hours_per_week': 40,
            'career_growth': 8
        }

        result = trained_scorer.evaluate_job(job)

        assert 'should_apply' in result
        assert 'acceptance_score' in result
        assert 'confidence' in result
        assert 'explanation' in result
        assert isinstance(result['should_apply'], bool)

    def test_evaluate_poor_job(self, trained_scorer):
        """Test evaluation of poor job match"""
        job = {
            'salary': 50000,
            'commute_time_minutes': 90,
            'work_hours_per_week': 60,
            'career_growth': 3
        }

        result = trained_scorer.evaluate_job(job)

        assert 'should_apply' in result
        # Poor job should likely get low score
        # (exact value depends on model, so we just check structure)

    def test_evaluate_batch(self, trained_scorer):
        """Test batch job evaluation"""
        jobs = [
            {'salary': 70000, 'commute_time_minutes': 20},
            {'salary': 80000, 'commute_time_minutes': 30},
            {'salary': 90000, 'commute_time_minutes': 40}
        ]

        results = trained_scorer.evaluate_job_batch(jobs)

        assert len(results) == 3
        assert all('acceptance_score' in r for r in results)

    def test_explain_preferences(self, trained_scorer):
        """Test preference explanation"""
        explanation = trained_scorer.explain_preferences()

        assert 'formula' in explanation
        assert 'feature_importance' in explanation
        assert 'training_stats' in explanation
        assert isinstance(explanation['feature_importance'], dict)


class TestEndToEnd:
    """End-to-end integration tests"""

    def test_complete_workflow(self):
        """Test complete workflow: train -> evaluate -> decide"""
        user_id = "integration_test_user"

        # Step 1: Create and train model
        model = PreferenceRegression(user_id)

        scenarios = [
            {
                'scenario_name': 'Local Job',
                'salary': 70000,
                'commute_time_minutes': 20,
                'work_hours_per_week': 40,
                'career_growth': 7,
                'work_arrangement': 2
            },
            {
                'scenario_name': 'High Salary Remote',
                'salary': 100000,
                'commute_time_minutes': 0,
                'work_hours_per_week': 45,
                'career_growth': 9,
                'work_arrangement': 3
            },
            {
                'scenario_name': 'Minimum Acceptable',
                'salary': 60000,
                'commute_time_minutes': 30,
                'work_hours_per_week': 40,
                'career_growth': 5,
                'work_arrangement': 1
            }
        ]
        acceptance_scores = [75, 90, 50]

        training_result = model.train_from_scenarios(scenarios, acceptance_scores)

        assert training_result['success'] is True

        # Step 2: Create scorer
        scorer = JobScorer.__new__(JobScorer)
        scorer.user_id = user_id
        scorer.model = model
        scorer.db = None

        # Step 3: Evaluate several jobs
        jobs = [
            {
                'job_id': 'job_1',
                'salary': 75000,
                'commute_time_minutes': 15,
                'work_hours_per_week': 40,
                'career_growth': 8,
                'work_arrangement': 2
            },
            {
                'job_id': 'job_2',
                'salary': 50000,
                'commute_time_minutes': 60,
                'work_hours_per_week': 50,
                'career_growth': 4,
                'work_arrangement': 1
            },
            {
                'job_id': 'job_3',
                'salary': 95000,
                'commute_time_minutes': 0,
                'work_hours_per_week': 40,
                'career_growth': 9,
                'work_arrangement': 3
            }
        ]

        results = []
        for job in jobs:
            result = scorer.evaluate_job(job)
            results.append(result)

        # Verify we got results for all jobs
        assert len(results) == 3

        # Verify high-quality job scored well
        assert results[2]['acceptance_score'] > results[1]['acceptance_score']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
