"""
User Preferences Module

Handles user job preference learning and evaluation through multi-variable regression.
Allows users to input 1-5 scenarios describing acceptable jobs, then infers
trade-offs between factors to evaluate new job opportunities.
"""

from .preference_regression import PreferenceRegression
from .job_scorer import JobScorer

__all__ = ["PreferenceRegression", "JobScorer"]
