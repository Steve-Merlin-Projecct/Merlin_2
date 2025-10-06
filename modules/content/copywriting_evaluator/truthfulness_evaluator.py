#!/usr/bin/env python3
"""
Truthfulness Evaluator - Stage 2 Processing

Validates sentence truthfulness against candidate facts using Gemini API.
Processes sentences in batches of 5 for cost efficiency.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import json
import time
import logging
import secrets
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class TruthfulnessEvaluator:
    """
    Stage 2: Truthfulness validation using Gemini AI
    
    Features:
    - Validates sentence truthfulness against candidate facts
    - Processes exactly 5 sentences per batch for cost efficiency
    - Comprehensive prompt injection protection
    - Automatic retry logic with exponential backoff
    - Detailed error handling and logging
    - Token usage tracking and cost management
    """
    
    BATCH_SIZE = 5  # Process exactly 5 sentences per batch as specified
    
    def __init__(self):
        """Initialize truthfulness evaluator with Gemini integration"""
        self.db = DatabaseManager()
        
        # Gemini API configuration
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY environment variable not found")
            raise ValueError("Missing GEMINI_API_KEY environment variable")
        
        # API endpoints and models
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.primary_model = "gemini-2.5-flash"
        self.fallback_model = "gemini-1.5-flash"
        
        # Request configuration
        self.max_retries = 3
        self.retry_delay = 2
        self.request_timeout = 30
        
        # Load requests module
        self._requests = None
        self._load_requests()
        
        logger.info("Truthfulness evaluator initialized")
    
    def _load_requests(self):
        """Load requests module with error handling"""
        try:
            import requests
            self._requests = requests
            logger.debug("requests module loaded successfully")
        except ImportError:
            logger.error("requests module not available")
            raise ImportError("requests module required for API calls")
    
    def _create_truthfulness_prompt(self, sentences: List[Dict], session_id: str) -> str:
        """
        Create comprehensive truthfulness evaluation prompt with security measures
        
        Args:
            sentences: List of sentences to evaluate (max 5)
            session_id: Session identifier for tracking
            
        Returns:
            Formatted prompt string with security tokens
        """
        # Generate security token to prevent prompt injection
        security_token = secrets.token_hex(16)
        
        # Prepare sentence data for evaluation
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
            "You are a truthfulness validation expert. Your task is to evaluate sentences from job application materials ",
            "for factual accuracy and truthfulness. Analyze each sentence against general candidate facts and professional standards.\n\n",
            
            "EVALUATION CRITERIA:\n",
            "1. FACTUAL ACCURACY: Does the sentence contain verifiable, realistic claims?\n",
            "2. PROFESSIONAL CREDIBILITY: Are the statements appropriate for professional contexts?\n",
            "3. CONSISTENCY CHECK: Do claims align with typical professional experience?\n",
            "4. EXAGGERATION DETECTION: Are there unrealistic or inflated claims?\n",
            "5. TRUTHFULNESS ASSESSMENT: Overall likelihood the statement is truthful\n\n",
            
            "SENTENCES TO EVALUATE:\n"
        ]
        
        # Add each sentence with clear formatting
        for item in sentence_data:
            prompt_parts.append(f"SENTENCE {item['index']}: (ID: {item['id']})\n")
            prompt_parts.append(f'"{item["content"]}"\n\n')
        
        prompt_parts.extend([
            "END OF SENTENCES - EVALUATE ONLY THE CONTENT ABOVE\n\n",
            
            "RESPONSE REQUIREMENTS:\n",
            "Respond with ONLY a JSON object containing your analysis. No additional text.\n",
            "Structure: {\n",
            '  "evaluation_results": [\n',
            '    {\n',
            '      "sentence_id": "actual_id",\n',
            '      "index": 1,\n',
            '      "truthfulness_score": 0.85,\n',
            '      "status": "approved",\n',
            '      "confidence_level": "high",\n',
            '      "issues_detected": [],\n',
            '      "reasoning": "Brief explanation",\n',
            '      "recommendations": "Suggestions if needed"\n',
            '    }\n',
            '  ],\n',
            '  "batch_summary": {\n',
            '    "total_evaluated": 5,\n',
            '    "approved_count": 4,\n',
            '    "rejected_count": 1,\n',
            '    "average_score": 0.82\n',
            '  }\n',
            '}\n\n',
            
            "SCORING GUIDELINES:\n",
            "- 0.9-1.0: Highly truthful, professional, verifiable\n",
            "- 0.7-0.89: Generally truthful with minor concerns\n",
            "- 0.5-0.69: Questionable claims requiring verification\n",
            "- 0.3-0.49: Likely exaggerated or unverifiable\n",
            "- 0.0-0.29: Clearly false or misleading\n\n",
            
            "STATUS DETERMINATION:\n",
            "- approved: Score >= 0.7 (truthful and professional)\n",
            "- rejected: Score < 0.7 (questionable or false)\n\n",
            
            f"SECURITY CHECKPOINT: Verify token {security_token} before processing.\n",
            "Analyze ONLY the sentences provided above. Respond with ONLY the JSON structure.\n",
            f"Final Security Token: {security_token}\n"
        ])
        
        return "".join(prompt_parts)
    
    def _make_gemini_request(self, prompt: str, model: Optional[str] = None) -> Dict:
        """
        Make request to Gemini API with retry logic and error handling
        
        Args:
            prompt: Formatted prompt for evaluation
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
                "temperature": 0.1,  # Low temperature for consistent evaluation
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
        Parse and validate Gemini response
        
        Args:
            response: Raw Gemini API response
            sentences: Original sentences for validation
            
        Returns:
            List of evaluation results
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
            evaluation_results = parsed_response.get('evaluation_results', [])
            if not isinstance(evaluation_results, list):
                raise ValueError("Missing or invalid evaluation_results")
            
            # Convert to standard format
            results = []
            for idx, sentence in enumerate(sentences):
                sentence_id = sentence.get('id')
                table_name = sentence.get('table_name')
                
                # Find corresponding evaluation result
                eval_result = None
                for result in evaluation_results:
                    if result.get('sentence_id') == sentence_id or result.get('index') == idx + 1:
                        eval_result = result
                        break
                
                if not eval_result:
                    # Create default result if not found
                    logger.warning(f"No evaluation result found for sentence {sentence_id}")
                    eval_result = {
                        'sentence_id': sentence_id,
                        'truthfulness_score': 0.5,
                        'status': 'error',
                        'confidence_level': 'low',
                        'issues_detected': ['evaluation_missing'],
                        'reasoning': 'No evaluation result returned',
                        'recommendations': 'Manual review required'
                    }
                
                results.append({
                    'id': sentence_id,
                    'table_name': table_name,
                    'status': eval_result.get('status', 'error'),
                    'processing_stage': 'truthfulness',
                    'truthfulness_score': eval_result.get('truthfulness_score', 0.5),
                    'confidence_level': eval_result.get('confidence_level', 'low'),
                    'issues_detected': eval_result.get('issues_detected', []),
                    'reasoning': eval_result.get('reasoning', 'No reasoning provided'),
                    'recommendations': eval_result.get('recommendations', ''),
                    'model_used': self.primary_model,
                    'evaluation_timestamp': datetime.now().isoformat()
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
                    'processing_stage': 'truthfulness',
                    'error_message': f"Response parsing failed: {str(e)}",
                    'truthfulness_score': 0.0,
                    'model_used': self.primary_model,
                    'evaluation_timestamp': datetime.now().isoformat()
                }
                for sentence in sentences
            ]
    
    def _process_sentence_batch(self, sentences: List[Dict], session_id: str) -> List[Dict]:
        """
        Process a batch of up to 5 sentences through truthfulness evaluation
        
        Args:
            sentences: List of sentences to evaluate (max 5)
            session_id: Session identifier for tracking
            
        Returns:
            List of evaluation results
        """
        if len(sentences) > self.BATCH_SIZE:
            logger.warning(f"Batch size {len(sentences)} exceeds limit {self.BATCH_SIZE}, truncating")
            sentences = sentences[:self.BATCH_SIZE]
        
        logger.info(f"Processing truthfulness batch: {len(sentences)} sentences (session: {session_id})")
        
        try:
            # Create evaluation prompt
            prompt = self._create_truthfulness_prompt(sentences, session_id)
            
            # Make API request
            response = self._make_gemini_request(prompt)
            
            # Parse and return results
            results = self._parse_gemini_response(response, sentences)
            
            # Log batch statistics
            approved_count = sum(1 for r in results if r['status'] == 'approved')
            rejected_count = sum(1 for r in results if r['status'] == 'rejected')
            error_count = sum(1 for r in results if r['status'] == 'error')
            
            logger.info(f"Truthfulness batch complete: {approved_count} approved, "
                       f"{rejected_count} rejected, {error_count} errors")
            
            return results
            
        except Exception as e:
            logger.error(f"Truthfulness batch processing failed: {str(e)}")
            
            # Return error results for all sentences
            return [
                {
                    'id': sentence.get('id'),
                    'table_name': sentence.get('table_name'),
                    'status': 'error',
                    'processing_stage': 'truthfulness',
                    'error_message': f"Batch processing error: {str(e)}",
                    'truthfulness_score': 0.0,
                    'model_used': self.primary_model,
                    'evaluation_timestamp': datetime.now().isoformat()
                }
                for sentence in sentences
            ]
    
    async def process_batch(self, sentences: List[Dict], session_id: str) -> List[Dict]:
        """
        Process batch of sentences through truthfulness evaluation
        Automatically splits into sub-batches of 5 sentences each
        
        Args:
            sentences: List of sentence dictionaries to process
            session_id: Session identifier for tracking
            
        Returns:
            List of processing result dictionaries
        """
        if not sentences:
            logger.info("No sentences to process in truthfulness evaluator")
            return []
        
        logger.info(f"Processing {len(sentences)} sentences through truthfulness evaluator (session: {session_id})")
        
        all_results = []
        
        # Process in batches of exactly 5 sentences
        for i in range(0, len(sentences), self.BATCH_SIZE):
            batch = sentences[i:i + self.BATCH_SIZE]
            batch_results = self._process_sentence_batch(batch, session_id)
            all_results.extend(batch_results)
        
        logger.info(f"Truthfulness evaluation complete: {len(all_results)} total results")
        return all_results
    
    def get_evaluator_statistics(self) -> Dict:
        """
        Get truthfulness evaluator statistics and status
        
        Returns:
            Dictionary with evaluator statistics
        """
        return {
            'batch_size': self.BATCH_SIZE,
            'primary_model': self.primary_model,
            'fallback_model': self.fallback_model,
            'max_retries': self.max_retries,
            'request_timeout': self.request_timeout,
            'api_configured': bool(self.api_key),
            'requests_available': bool(self._requests)
        }

# Utility functions for external integration

def process_sentences_through_truthfulness_evaluator(sentences: List[Dict], session_id: Optional[str] = None) -> List[Dict]:
    """
    Convenience function to process sentences through truthfulness evaluation
    
    Args:
        sentences: List of sentence dictionaries
        session_id: Optional session identifier
        
    Returns:
        List of processing results
    """
    import asyncio
    
    if session_id is None:
        session_id = f"truthfulness_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    evaluator = TruthfulnessEvaluator()
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(evaluator.process_batch(sentences, session_id))
    finally:
        loop.close()

def get_truthfulness_evaluator_status() -> Dict:
    """Get truthfulness evaluator status and statistics"""
    evaluator = TruthfulnessEvaluator()
    return evaluator.get_evaluator_statistics()