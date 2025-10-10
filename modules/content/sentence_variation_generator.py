#!/usr/bin/env python3
"""
Sentence Variation Generator - Gemini API Integration

Generates multiple variations of seed sentences for cover letters and resumes
using Google Gemini AI. Takes 15 high-quality seed sentences and produces
5-10 variations per seed with appropriate tone and style diversity.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

logger = logging.getLogger(__name__)


class SentenceVariationGenerator:
    """
    Generates sentence variations using Gemini AI

    Features:
    - Processes seed sentences in batches
    - Generates 5-10 variations per seed
    - Maintains tone and intent consistency
    - Produces CSV-ready output with metadata
    - Comprehensive error handling and retry logic
    """

    def __init__(self):
        """Initialize variation generator with Gemini API"""

        # Gemini API configuration
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY environment variable not found")
            raise ValueError("Missing GEMINI_API_KEY environment variable")

        # API endpoints and models
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        # Use experimental model for free tier and high capability
        self.model = "gemini-2.0-flash-exp"
        self.fallback_model = "gemini-1.5-flash"

        # Request configuration
        self.max_retries = 3
        self.retry_delay = 2
        self.request_timeout = 60  # Longer timeout for generation

        # Variation settings
        self.variations_per_seed = 7  # Default: 7 variations per seed sentence

        # Load requests module
        self._requests = None
        self._load_requests()

        logger.info(f"Sentence variation generator initialized with model: {self.model}")

    def _load_requests(self):
        """Load requests module with error handling"""
        try:
            import requests
            self._requests = requests
            logger.debug("requests module loaded successfully")
        except ImportError:
            logger.error("requests module not available")
            raise ImportError("requests module required for API calls")

    def generate_variations(self, seed_sentences: List[Dict],
                          variations_per_seed: Optional[int] = None,
                          target_position: Optional[str] = None) -> Dict:
        """
        Generate variations for a list of seed sentences

        Args:
            seed_sentences: List of seed sentence dictionaries with:
                - content_text: The sentence text
                - tone: Desired tone (optional)
                - category: Sentence category (optional)
                - intended_document: 'resume' or 'cover_letter'
            variations_per_seed: Number of variations to generate (default: 7)
            target_position: Target job position label (e.g., "Marketing Automation Manager")

        Returns:
            Dictionary with generated variations and metadata
        """

        if variations_per_seed is None:
            variations_per_seed = self.variations_per_seed

        logger.info(f"Generating {variations_per_seed} variations for {len(seed_sentences)} seed sentences")

        all_variations = []
        generation_stats = {
            'total_seeds': len(seed_sentences),
            'variations_per_seed': variations_per_seed,
            'total_generated': 0,
            'successful_seeds': 0,
            'failed_seeds': 0,
            'start_time': datetime.now().isoformat()
        }

        # Process each seed sentence
        for idx, seed in enumerate(seed_sentences, 1):
            try:
                logger.info(f"Processing seed {idx}/{len(seed_sentences)}")

                # Generate variations for this seed
                variations = self._generate_variations_for_seed(
                    seed,
                    variations_per_seed,
                    target_position
                )

                all_variations.extend(variations)
                generation_stats['successful_seeds'] += 1
                generation_stats['total_generated'] += len(variations)

                # Small delay between API calls to avoid rate limiting
                if idx < len(seed_sentences):
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Failed to generate variations for seed {idx}: {str(e)}")
                generation_stats['failed_seeds'] += 1
                continue

        generation_stats['end_time'] = datetime.now().isoformat()

        return {
            'success': True,
            'variations': all_variations,
            'stats': generation_stats
        }

    def _generate_variations_for_seed(self, seed: Dict,
                                     variations_count: int,
                                     target_position: Optional[str]) -> List[Dict]:
        """
        Generate variations for a single seed sentence using Gemini

        Args:
            seed: Seed sentence dictionary
            variations_count: Number of variations to generate
            target_position: Target job position

        Returns:
            List of variation dictionaries
        """

        # Create prompt for variation generation
        prompt = self._create_variation_prompt(seed, variations_count, target_position)

        # Call Gemini API
        response = self._call_gemini_api(prompt)

        # Parse and structure variations
        variations = self._parse_variations_response(response, seed)

        return variations

    def _create_variation_prompt(self, seed: Dict,
                                 variations_count: int,
                                 target_position: Optional[str]) -> str:
        """
        Create comprehensive prompt for Gemini to generate variations

        Args:
            seed: Seed sentence with metadata
            variations_count: How many variations to generate
            target_position: Target job position

        Returns:
            Formatted prompt string
        """

        content_text = seed.get('content_text', '')
        tone = seed.get('tone', 'Confident')
        category = seed.get('category', 'Achievement')
        intended_doc = seed.get('intended_document', 'cover_letter')

        position_context = f" for a {target_position} position" if target_position else ""

        prompt = f"""You are an expert professional resume and cover letter writer specializing in job applications{position_context}.

TASK: Generate {variations_count} distinct variations of the seed sentence below. Each variation should:
1. Maintain the CORE MESSAGE and truthfulness of the original
2. Use the specified TONE: {tone}
3. Preserve the CATEGORY purpose: {category}
4. Be appropriate for: {intended_doc}
5. Use ACTIVE VOICE and CRISP SYNTAX
6. Vary in LENGTH (some shorter, some longer than original)
7. Vary in WORD CHOICE and STRUCTURE
8. Avoid corporate jargon and clichés

SEED SENTENCE:
"{content_text}"

TONE GUIDELINES:
- Confident: Shows ownership and capability without arrogance
- Warm: Friendly, respectful, approachable
- Bold: Direct, provocative, impact-focused
- Curious: Emphasizes exploration and learning
- Storytelling: Uses narrative elements
- Insightful: Offers new perspectives
- Quirky: Personal, idiosyncratic (use sparingly)

STYLE REQUIREMENTS:
✓ Active voice (not passive)
✓ Specific achievements with metrics when appropriate
✓ Professional but conversational
✓ Scannable and punchy
✗ Avoid "very", "really", "quite", "incredibly"
✗ No clichés: "results-oriented", "team player", "think outside the box"
✗ No overuse of adjectives

RESPONSE FORMAT:
Respond with ONLY a JSON object. No additional text before or after.

{{
  "variations": [
    {{
      "variation_number": 1,
      "text": "Variation sentence here",
      "length_category": "short|medium|long",
      "tone_strength": 0.85,
      "notes": "Brief note on what makes this variation unique"
    }}
  ]
}}

Generate exactly {variations_count} variations now."""

        return prompt

    def _call_gemini_api(self, prompt: str) -> Dict:
        """
        Call Gemini API with retry logic

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            API response dictionary
        """

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.9,  # Higher creativity for variations
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
        }

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"API call attempt {attempt + 1}/{self.max_retries}")

                response = self._requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.request_timeout
                )

                if response.status_code == 200:
                    response_data = response.json()

                    # Extract text from Gemini response structure
                    if 'candidates' in response_data and len(response_data['candidates']) > 0:
                        content = response_data['candidates'][0].get('content', {})
                        parts = content.get('parts', [])
                        if parts and 'text' in parts[0]:
                            return {'text': parts[0]['text']}

                    raise ValueError("Unexpected Gemini API response structure")

                elif response.status_code == 429:
                    # Rate limit - wait longer
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue

                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    response.raise_for_status()

            except self._requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise

            except Exception as e:
                logger.error(f"API call failed on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise

        raise Exception("Max retries exceeded for Gemini API call")

    def _parse_variations_response(self, response: Dict, seed: Dict) -> List[Dict]:
        """
        Parse Gemini response and structure variations with metadata

        Args:
            response: Raw API response
            seed: Original seed sentence for metadata inheritance

        Returns:
            List of structured variation dictionaries
        """

        try:
            # Extract JSON from response text
            response_text = response.get('text', '')

            # Handle markdown code blocks if present
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()

            # Parse JSON
            parsed = json.loads(response_text)
            variations_list = parsed.get('variations', [])

            # Structure each variation with full metadata
            structured_variations = []

            for var in variations_list:
                structured_var = {
                    'content_text': var.get('text', ''),
                    'tone': seed.get('tone', 'Confident'),
                    'tone_strength': var.get('tone_strength', 0.8),
                    'category': seed.get('category'),
                    'intended_document': seed.get('intended_document', 'cover_letter'),
                    'position_label': seed.get('position_label', 'Marketing Automation Manager'),
                    'matches_job_skill': seed.get('matches_job_skill'),
                    'length': var.get('length_category', 'medium'),
                    'status': 'Draft',  # Start as draft, will be evaluated by pipeline
                    'variation_notes': var.get('notes', ''),
                    'seed_sentence': seed.get('content_text', ''),
                    'generated_date': datetime.now().isoformat()
                }

                structured_variations.append(structured_var)

            return structured_variations

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {str(e)}")
            logger.debug(f"Response text: {response.get('text', '')[:500]}")
            raise ValueError(f"Invalid JSON in Gemini response: {str(e)}")

        except Exception as e:
            logger.error(f"Error parsing variations response: {str(e)}")
            raise

    def export_to_csv_format(self, variations: List[Dict]) -> str:
        """
        Convert variations to CSV-formatted string

        Args:
            variations: List of variation dictionaries

        Returns:
            CSV-formatted string
        """

        import csv
        from io import StringIO

        output = StringIO()

        # Define CSV columns matching database schema
        fieldnames = [
            'content_text',
            'tone',
            'tone_strength',
            'status',
            'position_label',
            'matches_job_skill',
            'intended_document',
            'category',
            'length',
            'seed_sentence',
            'variation_notes'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for var in variations:
            row = {field: var.get(field, '') for field in fieldnames}
            writer.writerow(row)

        return output.getvalue()
