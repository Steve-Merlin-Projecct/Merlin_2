#!/usr/bin/env python3
"""
Skill Analyzer - Stage 5 Processing

Assigns primary skills to sentences using Gemini AI interpretation.
Final processing stage before sentence approval.

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

class SkillAnalyzer:
    """
    Stage 5: Primary skill assignment
    
    Features:
    - Assigns single primary skill to sentences using Gemini AI
    - Context-aware skill interpretation for job application materials
    """
    
    
    def __init__(self):
        """Initialize skill analyzer with Gemini integration"""
        self.db = DatabaseManager()
        
        # Gemini API configuration
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY environment variable not found")
            raise ValueError("Missing GEMINI_API_KEY environment variable")
        
        # API endpoints and models
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.primary_model = "gemini-2.5-flash"  # Flash model for efficient skill detection
        self.fallback_model = "gemini-1.5-flash"
        
        # Request configuration
        self.max_retries = 3
        self.retry_delay = 2
        self.request_timeout = 30
        
        # Load requests module
        self._requests = None
        self._load_requests()
        
        logger.info("Skill analyzer initialized for simple primary skill assignment")
    
    def _load_requests(self):
        """Load requests module with error handling"""
        try:
            import requests
            self._requests = requests
            logger.debug("requests module loaded successfully")
        except ImportError:
            logger.error("requests module not available")
            raise ImportError("requests module required for API calls")
    
    def _create_skill_analysis_prompt(self, sentences: List[Dict], session_id: str) -> str:
        """
        Create comprehensive skill analysis prompt with security measures
        
        Args:
            sentences: List of sentences to analyze for skills
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
        
        
        # Create structured prompt with security measures
        prompt_parts = [
            f"SECURITY TOKEN: {security_token}\n\n",
            "You are a professional skill identification expert. Your task is to analyze sentences from job application materials ",
            "and identify the primary professional skills demonstrated or mentioned. Focus on concrete, actionable skills that ",
            "employers value in professional contexts.\n\n",
            
            "SKILL ANALYSIS CONTEXT:\n",
            "You are analyzing sentences from resumes, cover letters, and professional profiles. Identify the single most prominent professional skill demonstrated or mentioned in each sentence.\n\n",
            
            "ANALYSIS REQUIREMENTS:\n",
            "1. PRIMARY SKILL: Identify the most prominent skill demonstrated in the sentence\n\n",
            
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
            '  "skill_analysis_results": [\n',
            '    {\n',
            '      "sentence_id": "actual_id",\n',
            '      "index": 1,\n',
            '      "primary_skill": "Project Management"\n',
            '    }\n',
            '  ],\n',
            '  "batch_summary": {\n',
            '    "total_analyzed": 3,\n',
            '    "skills_identified": {"Project Management": 2, "Communication": 1}\n',
            '  }\n',
            '}\n\n',
            
            "SKILL IDENTIFICATION GUIDELINES:\n",
            "- Focus on professional skills relevant to career advancement\n",
            "- Identify only the single most prominent skill demonstrated\n",
            "- Skill names should be professional and standardized\n",
            "- Avoid overly generic skills - focus on specific capabilities\n\n",
            
            f"SECURITY CHECKPOINT: Verify token {security_token} before processing.\n",
            "Analyze ONLY the sentences provided above. Respond with ONLY the JSON structure.\n",
            f"Final Security Token: {security_token}\n"
        ])
        
        return "".join(prompt_parts)
    
    def _make_gemini_request(self, prompt: str, model: Optional[str] = None) -> Dict:
        """
        Make request to Gemini API with retry logic and error handling
        
        Args:
            prompt: Formatted prompt for skill analysis
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
                "temperature": 0.3,  # Moderate temperature for balanced creativity and consistency
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
        Parse and validate Gemini response for skill analysis
        
        Args:
            response: Raw Gemini API response
            sentences: Original sentences for validation
            
        Returns:
            List of skill analysis results
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
            skill_results = parsed_response.get('skill_analysis_results', [])
            if not isinstance(skill_results, list):
                raise ValueError("Missing or invalid skill_analysis_results")
            
            # Convert to standard format
            results = []
            for idx, sentence in enumerate(sentences):
                sentence_id = sentence.get('id')
                table_name = sentence.get('table_name')
                
                # Find corresponding skill analysis result
                skill_result = None
                for result in skill_results:
                    if result.get('sentence_id') == sentence_id or result.get('index') == idx + 1:
                        skill_result = result
                        break
                
                if not skill_result:
                    # Create default result if not found
                    logger.warning(f"No skill analysis result found for sentence {sentence_id}")
                    skill_result = {
                        'sentence_id': sentence_id,
                        'primary_skill': 'General Professional Skills'
                    }
                
                # Validate and clean primary skill
                primary_skill = skill_result.get('primary_skill', 'General Professional Skills')
                
                results.append({
                    'id': sentence_id,
                    'table_name': table_name,
                    'status': 'approved',  # All sentences get skill analysis
                    'processing_stage': 'skill_analysis',
                    'primary_skill': primary_skill,
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
                    'processing_stage': 'skill_analysis',
                    'error_message': f"Response parsing failed: {str(e)}",
                    'primary_skill': 'General Professional Skills',
                    'model_used': self.primary_model,
                    'analysis_timestamp': datetime.now().isoformat()
                }
                for sentence in sentences
            ]
    
    async def process_batch(self, sentences: List[Dict], session_id: str) -> List[Dict]:
        """
        Process batch of sentences through skill analysis
        
        Args:
            sentences: List of sentence dictionaries to process
            session_id: Session identifier for tracking
            
        Returns:
            List of processing result dictionaries
        """
        if not sentences:
            logger.info("No sentences to process in skill analyzer")
            return []
        
        logger.info(f"Processing {len(sentences)} sentences through skill analyzer (session: {session_id})")
        
        try:
            # Create skill analysis prompt
            prompt = self._create_skill_analysis_prompt(sentences, session_id)
            
            # Make API request
            response = self._make_gemini_request(prompt)
            
            # Parse and return results
            results = self._parse_gemini_response(response, sentences)
            
            # Log batch statistics
            skill_distribution = {}
            
            for result in results:
                if result['status'] == 'approved':
                    primary_skill = result.get('primary_skill', 'Unknown')
                    skill_distribution[primary_skill] = skill_distribution.get(primary_skill, 0) + 1
            
            logger.info(f"Skill analysis batch complete: {len(results)} sentences analyzed")
            logger.info(f"Primary skills distribution: {skill_distribution}")
            
            return results
            
        except Exception as e:
            logger.error(f"Skill analysis batch processing failed: {str(e)}")
            
            # Return error results for all sentences
            return [
                {
                    'id': sentence.get('id'),
                    'table_name': sentence.get('table_name'),
                    'status': 'error',
                    'processing_stage': 'skill_analysis',
                    'error_message': f"Batch processing error: {str(e)}",
                    'primary_skill': 'General Professional Skills',
                    'model_used': self.primary_model,
                    'analysis_timestamp': datetime.now().isoformat()
                }
                for sentence in sentences
            ]
    
    def get_analyzer_statistics(self) -> Dict:
        """
        Get skill analyzer statistics and status
        
        Returns:
            Dictionary with analyzer statistics
        """
        return {
            'analyzer_type': 'Simple Primary Skill Assignment',
            'primary_model': self.primary_model,
            'fallback_model': self.fallback_model,
            'max_retries': self.max_retries,
            'request_timeout': self.request_timeout,
            'api_configured': bool(self.api_key),
            'requests_available': bool(self._requests)
        }
    
    def analyze_text_skills(self, text: str) -> Dict:
        """
        Analyze skills of a single text string for preview/testing
        
        Args:
            text: Text to analyze for skills
            
        Returns:
            Skill analysis result
        """
        import asyncio
        
        test_sentence = {
            'id': 'skill_preview_test',
            'table_name': 'preview',
            'content_text': text
        }
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.process_batch([test_sentence], 'skill_preview_session'))
            return results[0] if results else {'error': 'No analysis result'}
        finally:
            loop.close()

# Utility functions for external integration

def process_sentences_through_skill_analysis(sentences: List[Dict], session_id: Optional[str] = None) -> List[Dict]:
    """
    Convenience function to process sentences through skill analysis
    
    Args:
        sentences: List of sentence dictionaries
        session_id: Optional session identifier
        
    Returns:
        List of processing results
    """
    import asyncio
    
    if session_id is None:
        session_id = f"skill_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    analyzer = SkillAnalyzer()
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(analyzer.process_batch(sentences, session_id))
    finally:
        loop.close()

def get_skill_analyzer_status() -> Dict:
    """Get skill analyzer status and statistics"""
    analyzer = SkillAnalyzer()
    return analyzer.get_analyzer_statistics()

def analyze_text_skills_preview(text: str) -> Dict:
    """Preview skill analysis for given text"""
    analyzer = SkillAnalyzer()
    return analyzer.analyze_text_skills(text)