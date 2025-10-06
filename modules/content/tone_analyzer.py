"""
Tone Analysis and Scoring System
Implements the tone coherence scoring algorithms from building_sentences.md

This module uses numpy for mathematical calculations in tone analysis.
Numpy is loaded on-demand to avoid unnecessary startup overhead.
"""

import json
import logging
import sys
import os
from typing import List, Dict, Tuple, Optional
from sqlalchemy import text
from ..database.database_client import DatabaseClient


# On-demand numpy loading - only install when tone analysis is actually used
def _get_numpy_module():
    """Get numpy module with on-demand installation"""
    try:
        # Add utils directory to path for dependency manager
        utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "utils")
        if utils_path not in sys.path:
            sys.path.append(utils_path)

        from dependency_manager import get_numpy_module

        return get_numpy_module()
    except ImportError as e:
        logging.warning(f"numpy not available for tone analysis: {e}")

        # Create a minimal numpy-like interface for basic operations
        class MockNumpy:
            """
            Minimal numpy-like interface for basic operations when numpy is unavailable
            Provides essential mathematical functions for tone analysis calculations
            """

            def array(self, data):
                """Convert data to list (mock numpy array)"""
                return list(data)

            def mean(self, data):
                """Calculate arithmetic mean"""
                return sum(data) / len(data) if data else 0

            def std(self, data):
                """Calculate standard deviation"""
                if not data:
                    return 0
                mean_val = self.mean(data)
                return (sum((x - mean_val) ** 2 for x in data) / len(data)) ** 0.5

        logging.info("Using mock numpy interface for tone analysis")
        return MockNumpy()


# Initialize numpy module (with lazy loading)
np = None


def _ensure_numpy_loaded():
    """Ensure numpy is loaded when needed"""
    global np
    if np is None:
        np = _get_numpy_module()
        logging.info("numpy loaded for tone analysis calculations")
    return np


class ToneAnalyzer:
    """
    Analyzes tone consistency and calculates coherence scores for documents
    Based on the Tone Jump Score and Tone Coherence Score algorithms
    """

    def __init__(self):
        self.db_client = DatabaseClient()

        # Tone distance matrix based on building_sentences.md
        self.tone_distances = {
            ("Confident", "Warm"): 0.3,
            ("Confident", "Analytical"): 0.2,
            ("Confident", "Insightful"): 0.25,
            ("Confident", "Storytelling"): 0.4,
            ("Confident", "Curious"): 0.35,
            ("Confident", "Bold"): 0.15,
            ("Confident", "Quirky"): 0.6,
            ("Warm", "Analytical"): 0.4,
            ("Warm", "Insightful"): 0.3,
            ("Warm", "Storytelling"): 0.2,
            ("Warm", "Curious"): 0.25,
            ("Warm", "Bold"): 0.5,
            ("Warm", "Quirky"): 0.45,
            ("Analytical", "Insightful"): 0.2,
            ("Analytical", "Storytelling"): 0.45,
            ("Analytical", "Curious"): 0.3,
            ("Analytical", "Bold"): 0.5,
            ("Analytical", "Quirky"): 0.7,
            ("Insightful", "Storytelling"): 0.35,
            ("Insightful", "Curious"): 0.25,
            ("Insightful", "Bold"): 0.3,
            ("Insightful", "Quirky"): 0.5,
            ("Storytelling", "Curious"): 0.3,
            ("Storytelling", "Bold"): 0.4,
            ("Storytelling", "Quirky"): 0.4,
            ("Curious", "Bold"): 0.45,
            ("Curious", "Quirky"): 0.35,
            ("Bold", "Quirky"): 0.3,
        }

        # Make distance matrix symmetric
        symmetric_distances = {}
        for (tone1, tone2), distance in self.tone_distances.items():
            symmetric_distances[(tone1, tone2)] = distance
            symmetric_distances[(tone2, tone1)] = distance
        self.tone_distances = symmetric_distances

        # Same tone = 0 distance
        tones = ["Confident", "Warm", "Analytical", "Insightful", "Storytelling", "Curious", "Bold", "Quirky"]
        for tone in tones:
            self.tone_distances[(tone, tone)] = 0.0

    def get_tone_distance(self, tone1: str, tone2: str) -> float:
        """Get distance between two tones"""
        return self.tone_distances.get((tone1, tone2), 0.5)  # Default moderate distance

    def calculate_tone_jump_score(self, sentence1: Dict, sentence2: Dict) -> float:
        """
        Calculate tone jump score between two consecutive sentences
        Uses numpy for mathematical calculations - loads numpy on-demand if needed
        """
        # Ensure numpy is loaded when tone analysis is performed
        np = _ensure_numpy_loaded()
        """
        Calculate Tone Jump Score between two consecutive sentences
        TJS = ToneDistance * Avg(Strength_SentenceA, Strength_SentenceB)
        """
        tone_distance = self.get_tone_distance(sentence1["tone"], sentence2["tone"])
        avg_strength = (sentence1["tone_strength"] + sentence2["tone_strength"]) / 2
        return tone_distance * avg_strength

    def analyze_document_tone(self, sentences: List[Dict]) -> Dict:
        """
        Analyze tone coherence for a complete document

        Args:
            sentences: List of sentence dicts with 'text', 'tone', 'tone_strength'

        Returns:
            Dict with tone analysis metrics
        """
        if len(sentences) < 2:
            return {
                "sentences": sentences,
                "tone_jump_scores": [],
                "total_tone_travel": 0.0,
                "tone_coherence_score": 1.0,
                "average_tone_jump": 0.0,
            }

        tone_jump_scores = []

        # Calculate tone jump between each consecutive pair
        for i in range(len(sentences) - 1):
            tjs = self.calculate_tone_jump_score(sentences[i], sentences[i + 1])
            tone_jump_scores.append(tjs)

        # Total Tone Travel (TTT) = sum of all tone jumps
        total_tone_travel = sum(tone_jump_scores)

        # Calculate maximum possible tone travel for normalization
        max_possible_distance = max(self.tone_distances.values())
        max_strength = 1.0
        max_possible_jump = max_possible_distance * max_strength
        max_possible_ttt = max_possible_jump * (len(sentences) - 1)

        # Tone Coherence Score = 1 - (TTT / max_possible_TTT)
        if max_possible_ttt > 0:
            tone_coherence_score = 1 - (total_tone_travel / max_possible_ttt)
        else:
            tone_coherence_score = 1.0

        # Average tone jump
        average_tone_jump = total_tone_travel / len(tone_jump_scores) if tone_jump_scores else 0.0

        return {
            "sentences": sentences,
            "tone_jump_scores": tone_jump_scores,
            "total_tone_travel": total_tone_travel,
            "tone_coherence_score": max(0.0, tone_coherence_score),  # Ensure non-negative
            "average_tone_jump": average_tone_jump,
        }

    def calculate_sentence_contribution_score(
        self, sentence: Dict, prev_sentence: Dict = None, next_sentence: Dict = None
    ) -> float:
        """
        Calculate Sentence Contribution Score (SCS)
        SCS = Avg(Strength) * (1 - AvgToneJumpWithNeighbors)
        """
        strength = sentence["tone_strength"]

        if not prev_sentence and not next_sentence:
            return strength  # Single sentence gets full strength

        tone_jumps = []
        if prev_sentence:
            tone_jumps.append(self.calculate_tone_jump_score(prev_sentence, sentence))
        if next_sentence:
            tone_jumps.append(self.calculate_tone_jump_score(sentence, next_sentence))

        avg_tone_jump = sum(tone_jumps) / len(tone_jumps) if tone_jumps else 0.0

        return strength * (1 - avg_tone_jump)

    def analyze_and_store_document(
        self, document_type: str, sentences: List[Dict], job_id: str = None, application_id: str = None
    ) -> Dict:
        """
        Analyze document tone and store results in database
        """
        analysis = self.analyze_document_tone(sentences)

        # Store in database
        with self.db_client.get_session() as session:
            session.execute(
                text("""
                INSERT INTO document_tone_analysis (
                    document_type, job_id, application_id, sentences,
                    tone_jump_score, tone_coherence_score, total_tone_travel, average_tone_jump
                ) VALUES (:document_type, :job_id, :application_id, :sentences,
                         :tone_jump_score, :tone_coherence_score, :total_tone_travel, :average_tone_jump)
                """),
                {
                    "document_type": document_type,
                    "job_id": job_id,
                    "application_id": application_id,
                    "sentences": json.dumps(analysis["sentences"]),
                    "tone_jump_score": analysis["tone_jump_scores"][-1] if analysis["tone_jump_scores"] else 0.0,
                    "tone_coherence_score": analysis["tone_coherence_score"],
                    "total_tone_travel": analysis["total_tone_travel"],
                    "average_tone_jump": analysis["average_tone_jump"],
                },
            )

        logging.info(f"Tone analysis completed for {document_type}: Coherence={analysis['tone_coherence_score']:.3f}")
        return analysis

    def get_optimal_tone_sequence(self, target_tones: List[str]) -> List[str]:
        """
        Find optimal ordering of tones to minimize tone travel
        Simple greedy algorithm - can be improved with dynamic programming
        """
        if len(target_tones) <= 1:
            return target_tones

        remaining_tones = target_tones.copy()
        sequence = [remaining_tones.pop(0)]  # Start with first tone

        while remaining_tones:
            current_tone = sequence[-1]
            # Find tone with minimum distance to current
            next_tone = min(remaining_tones, key=lambda t: self.get_tone_distance(current_tone, t))
            sequence.append(next_tone)
            remaining_tones.remove(next_tone)

        return sequence

    def suggest_tone_improvements(self, analysis: Dict, target_coherence: float = 0.8) -> List[Dict]:
        """
        Suggest improvements to achieve target coherence score
        """
        suggestions = []

        if analysis["tone_coherence_score"] >= target_coherence:
            return suggestions

        # Find sentences with highest tone jumps
        for i, jump_score in enumerate(analysis["tone_jump_scores"]):
            if jump_score > 0.3:  # Threshold for problematic jumps
                suggestions.append(
                    {
                        "type": "high_tone_jump",
                        "position": i,
                        "current_jump": jump_score,
                        "sentence1": analysis["sentences"][i]["text"],
                        "sentence2": analysis["sentences"][i + 1]["text"],
                        "recommendation": f"Consider smoothing transition between {analysis['sentences'][i]['tone']} and {analysis['sentences'][i + 1]['tone']}",
                    }
                )

        return suggestions
