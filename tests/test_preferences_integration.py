#!/usr/bin/env python3
"""
Integration test for User Preferences Dashboard

Tests the full workflow:
1. Save scenarios
2. Train model
3. Evaluate jobs
4. Get model info
"""

import sys
import json
import requests
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:5000"
USER_ID = "steve_glen"


def test_save_scenarios() -> Dict[str, Any]:
    """Test saving user preference scenarios"""
    print("\n" + "="*60)
    print("TEST 1: Save Scenarios")
    print("="*60)

    scenarios = [
        {
            "scenario_name": "Local Edmonton Job",
            "salary": 70000,
            "commute_time_minutes": 20,
            "work_hours_per_week": 40,
            "work_arrangement": 2,  # Hybrid
            "career_growth": 7,
            "acceptance_score": 75
        },
        {
            "scenario_name": "High Salary Remote",
            "salary": 95000,
            "commute_time_minutes": 0,
            "work_hours_per_week": 45,
            "work_arrangement": 3,  # Remote
            "career_growth": 9,
            "acceptance_score": 85
        },
        {
            "scenario_name": "Minimum Acceptable",
            "salary": 60000,
            "commute_time_minutes": 30,
            "work_hours_per_week": 40,
            "work_arrangement": 1,  # Onsite
            "career_growth": 5,
            "acceptance_score": 50
        }
    ]

    response = requests.post(
        f"{BASE_URL}/preferences/save",
        json={"user_id": USER_ID, "scenarios": scenarios}
    )

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    assert data["success"], "Failed to save scenarios"
    assert len(data["scenario_ids"]) == 3, "Expected 3 scenario IDs"

    print("✅ Scenarios saved successfully")
    return data


def test_train_model() -> Dict[str, Any]:
    """Test training the preference model"""
    print("\n" + "="*60)
    print("TEST 2: Train Model")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/preferences/train",
        json={"user_id": USER_ID}
    )

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    assert data["success"], "Failed to train model"
    assert "model_id" in data, "No model ID returned"
    assert "formula" in data, "No formula returned"
    assert "training_result" in data, "No training result returned"

    print("\n📊 Model Details:")
    print(f"  Model Type: {data['training_result'].get('model_type', 'N/A')}")
    print(f"  R² Score: {data['training_result'].get('train_r2', 'N/A')}")
    print(f"  Scenario Count: {data['training_result'].get('scenario_count', 'N/A')}")
    print(f"\n📐 Formula:\n  {data['formula']}")

    if 'feature_importance' in data['training_result']:
        print("\n🎯 Feature Importance:")
        for feature, importance in data['training_result']['feature_importance'].items():
            print(f"  {feature}: {importance:.1f}%")

    print("\n✅ Model trained successfully")
    return data


def test_evaluate_job(job_data: Dict[str, Any], expected_result: str) -> Dict[str, Any]:
    """Test evaluating a job"""
    print("\n" + "="*60)
    print(f"TEST 3: Evaluate Job - {expected_result}")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/preferences/evaluate",
        json={"user_id": USER_ID, "job": job_data}
    )

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    assert data["success"], "Failed to evaluate job"
    assert "evaluation" in data, "No evaluation returned"

    eval_result = data["evaluation"]
    print(f"\n📈 Evaluation:")
    print(f"  Should Apply: {eval_result['should_apply']}")
    print(f"  Acceptance Score: {eval_result['acceptance_score']}/100")
    print(f"  Confidence: {eval_result['confidence']}%")
    print(f"  Explanation: {eval_result['explanation']}")

    print(f"\n✅ Job evaluated - Result: {'APPLY' if eval_result['should_apply'] else 'SKIP'}")
    return data


def test_get_model_info() -> Dict[str, Any]:
    """Test getting model information"""
    print("\n" + "="*60)
    print("TEST 4: Get Model Info")
    print("="*60)

    response = requests.get(
        f"{BASE_URL}/preferences/model-info",
        params={"user_id": USER_ID}
    )

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    assert data["success"], "Failed to get model info"
    assert data["trained"], "Model not trained"

    print(f"\n📊 Model Info:")
    print(f"  Model ID: {data['model_id']}")
    print(f"  Trained: {data['trained']}")
    print(f"  Formula: {data['formula']}")

    print("\n✅ Model info retrieved successfully")
    return data


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("USER PREFERENCES DASHBOARD INTEGRATION TESTS")
    print("="*60)

    try:
        # Test 1: Save scenarios
        test_save_scenarios()

        # Test 2: Train model
        test_train_model()

        # Test 3a: Evaluate good job (should apply)
        good_job = {
            "salary": 80000,
            "commute_time_minutes": 15,
            "work_hours_per_week": 40,
            "career_growth": 8,
            "work_arrangement": 2
        }
        test_evaluate_job(good_job, "Good Job (Expected: APPLY)")

        # Test 3b: Evaluate poor job (should skip)
        poor_job = {
            "salary": 50000,
            "commute_time_minutes": 60,
            "work_hours_per_week": 55,
            "career_growth": 3,
            "work_arrangement": 1
        }
        test_evaluate_job(poor_job, "Poor Job (Expected: SKIP)")

        # Test 4: Get model info
        test_get_model_info()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nThe User Preferences Dashboard is ready for use.")
        print(f"Visit: {BASE_URL}/preferences/")
        print("="*60)

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Could not connect to {BASE_URL}")
        print("Make sure the Flask app is running:")
        print("  python app_modular.py")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
