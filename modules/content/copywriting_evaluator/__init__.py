"""
Copywriting Evaluator System

A five-stage content processing pipeline for validating and classifying sentences
in the job application system's sentence banks.

Processing Pipeline:
- Stage 1: Keyword filtering (brand alignment)
- Stage 2: Truthfulness validation (Gemini AI)
- Stage 3: Canadian spelling corrections
- Stage 4: Tone analysis (Gemini AI)
- Stage 5: Skill assignment (Gemini AI)

Features:
- Independent stage status tracking
- Restart capability from any stage
- Testing vs production modes
- Performance metrics tracking
- Error handling with cooldown
"""

__version__ = "1.0.0"
__author__ = "Automated Job Application System"