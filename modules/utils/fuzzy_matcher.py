"""
Enhanced Fuzzy Matching Utilities
Provides sophisticated similarity algorithms for job and company matching
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """
    Advanced fuzzy matching for job titles and company names
    Uses multiple algorithms to determine similarity scores
    """

    def __init__(self):
        self.job_title_weights = {
            "exact_match": 1.0,
            "normalized_match": 0.95,
            "sequence_similarity": 0.8,
            "keyword_overlap": 0.7,
            "core_terms_match": 0.85,
            "abbreviation_match": 0.9,
        }

        self.company_name_weights = {
            "exact_match": 1.0,
            "normalized_match": 0.95,
            "sequence_similarity": 0.85,
            "legal_suffix_removed": 0.9,
            "word_order_flexible": 0.8,
        }

        # Common job title keywords for matching
        self.job_keywords = {
            "senior",
            "junior",
            "lead",
            "principal",
            "manager",
            "director",
            "analyst",
            "specialist",
            "coordinator",
            "associate",
            "developer",
            "engineer",
            "architect",
            "consultant",
            "executive",
            "assistant",
        }

        # Company legal suffixes to normalize
        self.company_suffixes = {
            "inc",
            "corp",
            "corporation",
            "ltd",
            "limited",
            "llc",
            "co",
            "company",
            "group",
            "enterprises",
            "solutions",
            "systems",
        }

    def calculate_job_similarity(self, job1: str, job2: str) -> float:
        """
        Calculate similarity score between two job titles

        Args:
            job1: First job title
            job2: Second job title

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not job1 or not job2:
            return 0.0

        # Normalize inputs
        norm1 = self._normalize_job_title(job1)
        norm2 = self._normalize_job_title(job2)

        # Exact match check
        if norm1 == norm2:
            return self.job_title_weights["exact_match"]

        # Multiple similarity checks with improved algorithms
        scores = []

        # 1. Sequence similarity (overall string similarity)
        seq_score = SequenceMatcher(None, norm1, norm2).ratio()
        scores.append(seq_score * self.job_title_weights["sequence_similarity"])

        # 2. Keyword overlap (important job terms)
        keyword_score = self._calculate_keyword_overlap(norm1, norm2)
        scores.append(keyword_score * self.job_title_weights["keyword_overlap"])

        # 3. Core terms matching (remove common words and compare)
        core_score = self._calculate_core_terms_similarity(norm1, norm2)
        scores.append(core_score * self.job_title_weights["core_terms_match"])

        # 4. Check if one is subset of the other (for variations like "Senior X" vs "X")
        subset_score = self._calculate_subset_similarity(norm1, norm2)
        if subset_score > 0.5:
            scores.append(subset_score * 0.85)

        # Return the highest score from all methods
        return max(scores) if scores else 0.0

    def calculate_company_similarity(self, company1: str, company2: str) -> float:
        """
        Calculate similarity score between two company names

        Args:
            company1: First company name
            company2: Second company name

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not company1 or not company2:
            return 0.0

        # Normalize inputs
        norm1 = self._normalize_company_name(company1)
        norm2 = self._normalize_company_name(company2)

        # Exact match check
        if norm1 == norm2:
            return self.company_name_weights["exact_match"]

        # Remove legal suffixes for comparison
        clean1 = self._remove_legal_suffixes(norm1)
        clean2 = self._remove_legal_suffixes(norm2)

        if clean1 == clean2:
            return self.company_name_weights["legal_suffix_removed"]

        # Multiple similarity approaches
        scores = []

        # 1. Sequence similarity on cleaned names
        seq_score = SequenceMatcher(None, clean1, clean2).ratio()
        scores.append(seq_score * self.company_name_weights["sequence_similarity"])

        # 2. Word order flexible matching
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        if words1 and words2:
            word_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
            scores.append(word_overlap * self.company_name_weights["word_order_flexible"])

        # 3. Check if one company name contains the other
        if clean1 in clean2 or clean2 in clean1:
            containment_score = min(len(clean1), len(clean2)) / max(len(clean1), len(clean2))
            scores.append(containment_score * 0.85)

        return max(scores) if scores else 0.0

    def find_best_match(
        self, target: str, candidates: List[Dict], field_name: str, match_type: str = "job", threshold: float = 0.7
    ) -> Optional[Dict]:
        """
        Find the best matching candidate from a list

        Args:
            target: Target string to match
            candidates: List of candidate dictionaries
            field_name: Field name in candidates to compare against
            match_type: 'job' or 'company' matching algorithm
            threshold: Minimum similarity threshold

        Returns:
            Best matching candidate or None if no match above threshold
        """
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            candidate_value = candidate.get(field_name, "")

            if match_type == "job":
                score = self.calculate_job_similarity(target, candidate_value)
            else:
                score = self.calculate_company_similarity(target, candidate_value)

            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
                best_match["_similarity_score"] = score

        return best_match

    def _normalize_job_title(self, title: str) -> str:
        """Normalize job title for comparison"""
        # Convert to lowercase
        normalized = title.lower().strip()

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)

        # Remove common punctuation but keep important separators
        normalized = re.sub(r"[^\w\s\-/&]", "", normalized)

        # Standardize common variations and abbreviations
        replacements = {
            "sr.": "senior",
            "sr ": "senior ",
            "jr.": "junior",
            "jr ": "junior ",
            "mgr": "manager",
            "dev": "developer",
            "eng": "engineer",
            "admin": "administrator",
            "coord": "coordinator",
            "spec": "specialist",
            "assoc": "associate",
            "asst": "assistant",
            "exec": "executive",
        }

        for abbrev, full in replacements.items():
            normalized = normalized.replace(abbrev, full)

        return normalized

    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for comparison"""
        # Convert to lowercase and strip
        normalized = name.lower().strip()

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)

        # Remove special characters except important ones
        normalized = re.sub(r"[^\w\s&\-.]", "", normalized)

        return normalized

    def _calculate_keyword_overlap(self, title1: str, title2: str) -> float:
        """Calculate overlap of important job keywords"""
        words1 = set(title1.split())
        words2 = set(title2.split())

        # Find keyword intersections
        keywords1 = words1.intersection(self.job_keywords)
        keywords2 = words2.intersection(self.job_keywords)

        if not keywords1 and not keywords2:
            return 0.0

        # Calculate Jaccard similarity for keywords
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)

        return len(intersection) / len(union) if union else 0.0

    def _calculate_core_terms_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity of core terms (non-common words)"""
        # Remove common words
        common_words = {"the", "and", "or", "of", "in", "at", "for", "to", "a", "an"}

        words1 = set(word for word in title1.split() if word not in common_words)
        words2 = set(word for word in title2.split() if word not in common_words)

        if not words1 and not words2:
            return 1.0  # Both empty
        if not words1 or not words2:
            return 0.0  # One empty

        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _remove_legal_suffixes(self, company_name: str) -> str:
        """Remove common legal suffixes from company names"""
        words = company_name.split()

        # Remove trailing legal suffixes
        while words and words[-1] in self.company_suffixes:
            words.pop()

        return " ".join(words)

    def _calculate_subset_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity when one title is a subset of another"""
        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return 0.0

        # Check if smaller set is subset of larger set
        smaller = words1 if len(words1) <= len(words2) else words2
        larger = words2 if len(words1) <= len(words2) else words1

        if smaller.issubset(larger):
            # Calculate how much of the larger set is covered
            return len(smaller) / len(larger)

        return 0.0


# Global fuzzy matcher instance
fuzzy_matcher = FuzzyMatcher()
