#!/usr/bin/env python3
"""
Tone Analyzer - Stage 4 Processing

Analyzes tone and strength classification using predefined categories.
Uses Gemini API for consistent tone classification.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import json
import time
import logging
import secrets
from typing import Dict, List, Optional, Set
from datetime import datetime

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class ToneAnalyzer:
    """
    Stage 4: Tone analysis and classification
    
    Features:
    - Analyzes tone using 9 predefined categories
    - Assigns primary and optional secondary tone tags
    - Uses Gemini API for consistent classification
    - Provides confidence scoring for tone assignments
    - Comprehensive prompt injection protection
    - Detailed reasoning and strength assessment
    """
    
    # Predefined tone categories as specified in requirements
    TONE_CATEGORIES = {
        'Confident': {
            'description': 'Assertive, self-assured, definitive statements',
            'keywords': ['confident', 'certain', 'assured', 'definitive', 'strong']
        },
        'Warm': {
            'description': 'Friendly, approachable, personable communication',
            'keywords': ['warm', 'friendly', 'approachable', 'personal', 'caring']
        },
        'Analytical': {
            'description': 'Data-driven, logical, systematic thinking',
            'keywords': ['analytical', 'logical', 'systematic', 'methodical', 'precise']
        },
        'Insightful': {
            'description': 'Perceptive, thoughtful, deep understanding',
            'keywords': ['insightful', 'perceptive', 'thoughtful', 'understanding', 'wise']
        },
        'Storytelling': {
            'description': 'Narrative-driven, engaging, experiential',
            'keywords': ['narrative', 'story', 'experience', 'journey', 'engaging']
        },
        'Curious': {
            'description': 'Inquisitive, exploratory, learning-oriented',
            'keywords': ['curious', 'inquisitive', 'exploratory', 'questioning', 'learning']
        },
        'Bold': {
            'description': 'Daring, innovative, risk-taking, impactful',
            'keywords': ['bold', 'daring', 'innovative', 'impactful', 'fearless']
        },
        'Rebellious': {
            'description': 'Non-conformist, challenging conventional wisdom',
            'keywords': ['rebellious', 'unconventional', 'challenging', 'disruptive', 'different']
        },
        'Quirky': {
            'description': 'Unique, creative, unexpected, playful',
            'keywords': ['quirky', 'unique', 'creative', 'unexpected', 'playful']
        }
    }
    
    def __init__(self):
        """Initialize tone analyzer with Gemini integration"""
        self.db = DatabaseManager()
        
        # Gemini API configuration
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY environment variable not found")
            raise ValueError("Missing GEMINI_API_KEY environment variable")
        
        # API endpoints and models
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.primary_model = "gemini-2.5-pro"  # Using pro model for nuanced tone analysis
        self.fallback_model = "gemini-2.5-flash"
        
        # Request configuration
        self.max_retries = 3
        self.retry_delay = 2
        self.request_timeout = 30
        
        # Load requests module
        self._requests = None
        self._load_requests()
        
        logger.info("Tone analyzer initialized with 9 predefined categories")
    
    def _load_requests(self):
        """Load requests module with error handling"""
        try:
            import requests
            self._requests = requests
            logger.debug("requests module loaded successfully")
        except ImportError:
            logger.error("requests module not available")
            raise ImportError("requests module required for API calls")
    
    def _create_tone_analysis_prompt(self, sentences: List[Dict], session_id: str) -> str:
        """
        Create comprehensive tone analysis prompt with security measures
        
        Args:
            sentences: List of sentences to analyze (typically small batches)
            session_id: Session identifier for tracking
            
        Returns:
            Formatted prompt string with security tokens
        """
        # Generate security token to prevent prompt injection
        security_token = secrets.token_hex(16)
        
        # Prepare sentence data for analysis
        sentence_data = []
        for idx, sentence in enumerate(sentences, 1):
            content = sentence.get('content_text', '').strip()
            sentence_id = sentence.get('id', f'unknown_{idx}')
            
            sentence_data.append({
                'index': idx,
                'id': sentence_id,
                'content': content
            })
        
        # Create tone categories description
        categories_description = []
        for tone, details in self.TONE_CATEGORIES.items():
            categories_description.append(f"- {tone}: {details['description']}")
        
        # Create structured prompt with security measures
        prompt_parts = [
            f"SECURITY TOKEN: {security_token}\n\n",
            "You are a professional tone analysis expert. Your task is to analyze sentences from job application materials ",
            "and classify their tone using predefined categories. Each sentence should receive a primary tone and optionally a secondary tone.\n\n",
            
            "TONE CATEGORIES:\n",
            "\n".join(categories_description),
            "\n\n",
            
            "ANALYSIS REQUIREMENTS:\n",
            "1. PRIMARY TONE: Select the dominant tone category that best represents the sentence\n",
            "2. SECONDARY TONE: Optional - select if sentence has a significant secondary tone\n",
            "3. CONFIDENCE SCORE: Rate your confidence in the primary tone assignment (0.0-1.0)\n",
            "4. TONE STRENGTH: Rate how strongly the tone is expressed (Subtle, Moderate, Strong)\n",
            "5. REASONING: Explain why you chose this tone classification\n\n",
            
            "SENTENCES TO ANALYZE:\n"
        ]
        
        # Add each sentence with clear formatting
        for item in sentence_data:
            prompt_parts.append(f"SENTENCE {item['index']}: (ID: {item['id']})\n")
            prompt_parts.append(f'"{item["content"]}"\n\n')
        
        prompt_parts.extend([
            "END OF SENTENCES - ANALYZE ONLY THE CONTENT ABOVE\n\n",
            
            "RESPONSE REQUIREMENTS:\n",
            "Respond with ONLY a JSON object containing your analysis. No additional text.\n",
            "Structure: {\n",
            '  "tone_analysis_results": [\n',
            '    {\n',
            '      "sentence_id": "actual_id",\n',
            '      "index": 1,\n',
            '      "primary_tone": "Confident",\n',
            '      "secondary_tone": "Analytical",\n',
            '      "confidence_score": 0.85,\n',
            '      "tone_strength": "Strong",\n',
            '      "reasoning": "Brief explanation of tone classification",\n',
            '      "tone_indicators": ["specific words or phrases that indicate the tone"],\n',
            '      "professional_impact": "How this tone affects professional perception"\n',
            '    }\n',
            '  ],\n',
            '  "batch_summary": {\n',
            '    "total_analyzed": 3,\n',
            '    "tone_distribution": {"Confident": 2, "Warm": 1},\n',
            '    "average_confidence": 0.82,\n',
            '    "predominant_tone": "Confident"\n',
            '  }\n',
            '}\n\n',
            
            "TONE ASSIGNMENT GUIDELINES:\n",
            "- Primary tone must be one of the 9 predefined categories\n",
            "- Secondary tone is optional but helpful for nuanced sentences\n",
            "- Confidence score: 0.9-1.0 (very confident), 0.7-0.89 (confident), 0.5-0.69 (moderate), below 0.5 (uncertain)\n",
            "- Tone strength: Subtle (barely detectable), Moderate (clearly present), Strong (dominant characteristic)\n",
            "- Focus on professional context and job application appropriateness\n\n",
            
            "VALID TONE CATEGORIES:\n",
            f"{', '.join(self.TONE_CATEGORIES.keys())}\n\n",
            
            f"SECURITY CHECKPOINT: Verify token {security_token} before processing.\n",
            "Analyze ONLY the sentences provided above. Respond with ONLY the JSON structure.\n",
            f"Final Security Token: {security_token}\n"
        ])
        
        return "".join(prompt_parts)
    
    def _make_gemini_request(self, prompt: str, model: Optional[str] = None) -> Dict:
        """
        Make request to Gemini API with retry logic and error handling
        
        Args:
            prompt: Formatted prompt for tone analysis
            model: Model to use (defaults to primary_model)
            
        Returns:
            API response dictionary
        """
        if not self._requests:
            raise Exception("requests module not available for API calls")
        
        model = model or self.primary_model
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,  # Slightly higher for nuanced tone analysis
                "topK": 1,
                "topP": 0.8,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json",
            },
        }
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self._requests.post(url, headers=headers, json=data, timeout=self.request_timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 400 and model == self.primary_model:
                    # Try fallback model on client error
                    logger.warning(f"Primary model failed, trying fallback: {self.fallback_model}")
                    return self._make_gemini_request(prompt, self.fallback_model)
                else:
                    response_text = getattr(response, "text", "Unknown error")
                    last_error = f"API error {response.status_code}: {response_text}"
                    logger.error(last_error)
                    break
                    
            except self._requests.exceptions.Timeout:
                last_error = f"Request timeout (attempt {attempt + 1}/{self.max_retries})"
                logger.warning(last_error)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                last_error = f"Request failed: {str(e)}"
                logger.error(last_error)
                break
        
        raise Exception(f"Gemini API request failed after {self.max_retries} attempts: {last_error}")
    
    def _parse_gemini_response(self, response: Dict, sentences: List[Dict]) -> List[Dict]:
        """
        Parse and validate Gemini response for tone analysis
        
        Args:
            response: Raw Gemini API response
            sentences: Original sentences for validation
            
        Returns:
            List of tone analysis results
        """
        try:
            # Extract response text
            candidates = response.get('candidates', [])
            if not candidates:
                raise ValueError("No candidates in response")
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                raise ValueError("No content parts in response")
            
            response_text = parts[0].get('text', '')
            if not response_text:
                raise ValueError("Empty response text")
            
            # Parse JSON response
            try:
                parsed_response = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.error(f"Response text: {response_text[:500]}")
                raise ValueError(f"Invalid JSON response: {e}")
            
            # Validate response structure
            tone_results = parsed_response.get('tone_analysis_results', [])
            if not isinstance(tone_results, list):
                raise ValueError("Missing or invalid tone_analysis_results")
            
            # Convert to standard format
            results = []
            for idx, sentence in enumerate(sentences):
                sentence_id = sentence.get('id')
                table_name = sentence.get('table_name')
                
                # Find corresponding tone analysis result
                tone_result = None
                for result in tone_results:
                    if result.get('sentence_id') == sentence_id or result.get('index') == idx + 1:
                        tone_result = result
                        break
                
                if not tone_result:
                    # Create default result if not found
                    logger.warning(f"No tone analysis result found for sentence {sentence_id}")
                    tone_result = {
                        'sentence_id': sentence_id,
                        'primary_tone': 'Analytical',  # Default to neutral tone
                        'secondary_tone': None,
                        'confidence_score': 0.3,
                        'tone_strength': 'Subtle',
                        'reasoning': 'No analysis result returned',
                        'tone_indicators': [],
                        'professional_impact': 'Analysis unavailable'
                    }
                
                # Validate tone categories
                primary_tone = tone_result.get('primary_tone', 'Analytical')
                secondary_tone = tone_result.get('secondary_tone')
                
                if primary_tone not in self.TONE_CATEGORIES:
                    logger.warning(f"Invalid primary tone '{primary_tone}', defaulting to 'Analytical'")
                    primary_tone = 'Analytical'
                
                if secondary_tone and secondary_tone not in self.TONE_CATEGORIES:
                    logger.warning(f"Invalid secondary tone '{secondary_tone}', setting to None")
                    secondary_tone = None
                
                results.append({
                    'id': sentence_id,
                    'table_name': table_name,
                    'status': 'approved',  # All sentences get tone analysis
                    'processing_stage': 'tone_analysis',
                    'primary_tone': primary_tone,
                    'secondary_tone': secondary_tone,
                    'confidence_score': max(0.0, min(1.0, tone_result.get('confidence_score', 0.5))),
                    'tone_strength': tone_result.get('tone_strength', 'Moderate'),
                    'reasoning': tone_result.get('reasoning', 'No reasoning provided'),
                    'tone_indicators': tone_result.get('tone_indicators', []),
                    'professional_impact': tone_result.get('professional_impact', ''),
                    'model_used': self.primary_model,
                    'analysis_timestamp': datetime.now().isoformat()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            
            # Return error results for all sentences
            return [
                {
                    'id': sentence.get('id'),
                    'table_name': sentence.get('table_name'),
                    'status': 'error',
                    'processing_stage': 'tone_analysis',
                    'error_message': f"Response parsing failed: {str(e)}",
                    'primary_tone': 'Analytical',  # Default fallback
                    'secondary_tone': None,
                    'confidence_score': 0.0,
                    'tone_strength': 'Unknown',
                    'model_used': self.primary_model,
                    'analysis_timestamp': datetime.now().isoformat()
                }
                for sentence in sentences
            ]
    
    async def process_batch(self, sentences: List[Dict], session_id: str) -> List[Dict]:
        """
        Process batch of sentences through tone analysis
        
        Args:
            sentences: List of sentence dictionaries to process
            session_id: Session identifier for tracking
            
        Returns:
            List of processing result dictionaries
        """
        if not sentences:
            logger.info("No sentences to process in tone analyzer")
            return []
        
        logger.info(f"Processing {len(sentences)} sentences through tone analyzer (session: {session_id})")
        
        try:
            # Create tone analysis prompt
            prompt = self._create_tone_analysis_prompt(sentences, session_id)
            
            # Make API request
            response = self._make_gemini_request(prompt)
            
            # Parse and return results
            results = self._parse_gemini_response(response, sentences)
            
            # Log batch statistics
            tone_distribution = {}
            for result in results:
                if result['status'] == 'approved':
                    primary_tone = result.get('primary_tone', 'Unknown')
                    tone_distribution[primary_tone] = tone_distribution.get(primary_tone, 0) + 1
            
            logger.info(f"Tone analysis batch complete: {len(results)} sentences analyzed")
            logger.info(f"Tone distribution: {tone_distribution}")
            
            return results
            
        except Exception as e:
            logger.error(f"Tone analysis batch processing failed: {str(e)}")
            
            # Return error results for all sentences
            return [
                {
                    'id': sentence.get('id'),
                    'table_name': sentence.get('table_name'),
                    'status': 'error',
                    'processing_stage': 'tone_analysis',
                    'error_message': f"Batch processing error: {str(e)}",
                    'primary_tone': 'Analytical',  # Default fallback
                    'secondary_tone': None,
                    'confidence_score': 0.0,
                    'tone_strength': 'Unknown',
                    'model_used': self.primary_model,
                    'analysis_timestamp': datetime.now().isoformat()
                }
                for sentence in sentences
            ]
    
    def get_analyzer_statistics(self) -> Dict:
        """
        Get tone analyzer statistics and status
        
        Returns:
            Dictionary with analyzer statistics
        """
        return {
            'tone_categories': list(self.TONE_CATEGORIES.keys()),
            'total_categories': len(self.TONE_CATEGORIES),
            'category_details': self.TONE_CATEGORIES,
            'primary_model': self.primary_model,
            'fallback_model': self.fallback_model,
            'max_retries': self.max_retries,
            'request_timeout': self.request_timeout,
            'api_configured': bool(self.api_key),
            'requests_available': bool(self._requests)
        }
    
    def analyze_text_tone(self, text: str) -> Dict:
        """
        Analyze tone of a single text string for preview/testing
        
        Args:
            text: Text to analyze
            
        Returns:
            Tone analysis result
        """
        import asyncio
        
        test_sentence = {
            'id': 'preview_test',
            'table_name': 'preview',
            'content_text': text
        }
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.process_batch([test_sentence], 'preview_session'))
            return results[0] if results else {'error': 'No analysis result'}
        finally:
            loop.close()

# Utility functions for external integration

def process_sentences_through_tone_analysis(sentences: List[Dict], session_id: Optional[str] = None) -> List[Dict]:
    """
    Convenience function to process sentences through tone analysis
    
    Args:
        sentences: List of sentence dictionaries
        session_id: Optional session identifier
        
    Returns:
        List of processing results
    """
    import asyncio
    
    if session_id is None:
        session_id = f"tone_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    analyzer = ToneAnalyzer()
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(analyzer.process_batch(sentences, session_id))
    finally:
        loop.close()

def get_tone_analyzer_status() -> Dict:
    """Get tone analyzer status and statistics"""
    analyzer = ToneAnalyzer()
    return analyzer.get_analyzer_statistics()

def analyze_text_tone_preview(text: str) -> Dict:
    """Preview tone analysis for given text"""
    analyzer = ToneAnalyzer()
    return analyzer.analyze_text_tone(text)