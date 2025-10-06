#!/usr/bin/env python3
"""
Canadian Spelling Processor - Stage 3 Processing

Applies Canadian Press spelling corrections using 183 conversion pairs.
Processes text locally without LLM calls for efficiency.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import re
import logging
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class CanadianSpellingProcessor:
    """
    Stage 3: Canadian spelling corrections
    
    Features:
    - Applies 183 Canadian Press spelling conversion pairs
    - Word-boundary aware replacements to avoid partial matches
    - Case-sensitive and case-insensitive matching
    - Database-driven spelling rules with caching
    - Comprehensive change tracking and statistics
    - High-performance local processing (no LLM calls)
    """
    
    def __init__(self):
        """Initialize Canadian spelling processor"""
        self.db = DatabaseManager()
        self._cached_spellings: Optional[Dict[str, str]] = None
        self._cache_updated: Optional[datetime] = None
        self._cache_duration_minutes = 120  # Cache spellings for 2 hours
        
        logger.info("Canadian spelling processor initialized")
    
    def _get_spelling_conversions(self) -> Dict[str, str]:
        """
        Get Canadian spelling conversions from database with caching
        
        Returns:
            Dictionary mapping American spellings to Canadian spellings
        """
        # Check if cache is valid
        if (self._cached_spellings is not None and 
            self._cache_updated is not None and
            (datetime.now() - self._cache_updated).total_seconds() < (self._cache_duration_minutes * 60)):
            return self._cached_spellings
        
        try:
            # Fetch spelling conversions from database
            query = "SELECT american_spelling, canadian_spelling FROM canadian_spellings"
            results = self.db.execute_query(query, ())
            
            # Create conversion dictionary
            conversions = {}
            for row in results:
                american_spelling = row[0].strip() if row[0] else ""
                canadian_spelling = row[1].strip() if row[1] else ""
                
                if american_spelling and canadian_spelling:
                    conversions[american_spelling] = canadian_spelling
            
            # Update cache
            self._cached_spellings = conversions
            self._cache_updated = datetime.now()
            
            logger.info(f"Loaded {len(conversions)} Canadian spelling conversions")
            return conversions
            
        except Exception as e:
            logger.error(f"Failed to load spelling conversions from database: {str(e)}")
            # Return empty dict on error to avoid blocking processing
            return {}
    
    def _apply_spelling_conversions(self, text: str, conversions: Dict[str, str]) -> Tuple[str, List[Dict]]:
        """
        Apply Canadian spelling conversions to text with word boundaries
        
        Args:
            text: Text to process
            conversions: Dictionary of American->Canadian spelling mappings
            
        Returns:
            Tuple of (converted_text, list_of_changes_made)
        """
        if not text or not conversions:
            return text, []
        
        converted_text = text
        changes_made = []
        
        # Sort conversions by length (longest first) to handle overlapping patterns
        sorted_conversions = sorted(conversions.items(), key=lambda x: len(x[0]), reverse=True)
        
        for american_spelling, canadian_spelling in sorted_conversions:
            # Create case-sensitive pattern with word boundaries
            pattern_exact = r'\b' + re.escape(american_spelling) + r'\b'
            
            # Find all matches for tracking
            matches = list(re.finditer(pattern_exact, converted_text))
            
            if matches:
                # Apply replacement
                converted_text = re.sub(pattern_exact, canadian_spelling, converted_text)
                
                # Track changes
                for match in matches:
                    changes_made.append({
                        'original': american_spelling,
                        'replacement': canadian_spelling,
                        'position': match.start(),
                        'match_type': 'exact_case'
                    })
            
            # Also check for capitalized versions
            american_capitalized = american_spelling.capitalize()
            canadian_capitalized = canadian_spelling.capitalize()
            
            if american_capitalized != american_spelling:
                pattern_cap = r'\b' + re.escape(american_capitalized) + r'\b'
                matches_cap = list(re.finditer(pattern_cap, converted_text))
                
                if matches_cap:
                    converted_text = re.sub(pattern_cap, canadian_capitalized, converted_text)
                    
                    for match in matches_cap:
                        changes_made.append({
                            'original': american_capitalized,
                            'replacement': canadian_capitalized,
                            'position': match.start(),
                            'match_type': 'capitalized'
                        })
            
            # Check for uppercase versions
            american_upper = american_spelling.upper()
            canadian_upper = canadian_spelling.upper()
            
            if american_upper != american_spelling and len(american_spelling) > 2:  # Avoid single-letter words
                pattern_upper = r'\b' + re.escape(american_upper) + r'\b'
                matches_upper = list(re.finditer(pattern_upper, converted_text))
                
                if matches_upper:
                    converted_text = re.sub(pattern_upper, canadian_upper, converted_text)
                    
                    for match in matches_upper:
                        changes_made.append({
                            'original': american_upper,
                            'replacement': canadian_upper,
                            'position': match.start(),
                            'match_type': 'uppercase'
                        })
        
        return converted_text, changes_made
    
    def _process_sentence(self, sentence: Dict, conversions: Dict[str, str], session_id: str) -> Dict:
        """
        Process a single sentence through Canadian spelling conversion
        
        Args:
            sentence: Sentence dictionary with content and metadata
            conversions: Spelling conversion mappings
            session_id: Session identifier for tracking
            
        Returns:
            Processing result dictionary
        """
        try:
            content_text = sentence.get('content_text', '').strip()
            sentence_id = sentence.get('id')
            table_name = sentence.get('table_name')
            
            if not content_text:
                logger.warning(f"Empty content_text for sentence {sentence_id}")
                return {
                    'id': sentence_id,
                    'table_name': table_name,
                    'status': 'approved',  # Empty content doesn't need spelling changes
                    'processing_stage': 'canadian_spelling',
                    'original_text': content_text,
                    'corrected_text': content_text,
                    'changes_made': [],
                    'changes_count': 0,
                    'content_length': 0
                }
            
            # Apply spelling conversions
            corrected_text, changes_made = self._apply_spelling_conversions(content_text, conversions)
            
            # Determine if any changes were made
            has_changes = len(changes_made) > 0
            changes_count = len(changes_made)
            
            logger.debug(f"Sentence {sentence_id}: {changes_count} spelling changes applied")
            
            return {
                'id': sentence_id,
                'table_name': table_name,
                'status': 'approved',  # All sentences are approved after spelling correction
                'processing_stage': 'canadian_spelling',
                'original_text': content_text,
                'corrected_text': corrected_text,
                'changes_made': changes_made,
                'changes_count': changes_count,
                'has_changes': has_changes,
                'content_length': len(content_text),
                'corrected_length': len(corrected_text),
                'processing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing sentence {sentence.get('id')}: {str(e)}")
            return {
                'id': sentence.get('id'),
                'table_name': sentence.get('table_name'),
                'status': 'error',
                'error_message': str(e),
                'processing_stage': 'canadian_spelling',
                'original_text': sentence.get('content_text', ''),
                'corrected_text': sentence.get('content_text', ''),
                'changes_made': [],
                'changes_count': 0,
                'has_changes': False,
                'content_length': 0
            }
    
    async def process_batch(self, sentences: List[Dict], session_id: str) -> List[Dict]:
        """
        Process batch of sentences through Canadian spelling corrections
        
        Args:
            sentences: List of sentence dictionaries to process
            session_id: Session identifier for tracking
            
        Returns:
            List of processing result dictionaries
        """
        if not sentences:
            logger.info("No sentences to process in Canadian spelling processor")
            return []
        
        logger.info(f"Processing {len(sentences)} sentences through Canadian spelling processor (session: {session_id})")
        
        try:
            # Load spelling conversions
            conversions = self._get_spelling_conversions()
            
            if not conversions:
                logger.warning("No spelling conversions loaded - sentences will pass through unchanged")
            
            # Process each sentence
            results = []
            total_changes = 0
            sentences_with_changes = 0
            
            for sentence in sentences:
                result = self._process_sentence(sentence, conversions, session_id)
                results.append(result)
                
                # Track statistics
                if result.get('has_changes', False):
                    sentences_with_changes += 1
                    total_changes += result.get('changes_count', 0)
            
            # Log batch statistics
            logger.info(f"Canadian spelling batch complete: {sentences_with_changes}/{len(sentences)} sentences modified, "
                       f"{total_changes} total spelling changes applied")
            
            return results
            
        except Exception as e:
            logger.error(f"Canadian spelling batch processing failed: {str(e)}")
            # Return error results for all sentences
            return [
                {
                    'id': sentence.get('id'),
                    'table_name': sentence.get('table_name'),
                    'status': 'error',
                    'error_message': f"Batch processing error: {str(e)}",
                    'processing_stage': 'canadian_spelling',
                    'original_text': sentence.get('content_text', ''),
                    'corrected_text': sentence.get('content_text', ''),
                    'changes_made': [],
                    'changes_count': 0,
                    'has_changes': False,
                    'content_length': 0
                }
                for sentence in sentences
            ]
    
    def get_processor_statistics(self) -> Dict:
        """
        Get Canadian spelling processor statistics and status
        
        Returns:
            Dictionary with processor statistics
        """
        try:
            conversions = self._get_spelling_conversions()
            
            # Analyze conversion patterns
            conversion_types = {}
            for american, canadian in conversions.items():
                # Categorize by common patterns
                if 'or' in american and 'our' in canadian:
                    conversion_types['or_to_our'] = conversion_types.get('or_to_our', 0) + 1
                elif 'er' in american and 're' in canadian:
                    conversion_types['er_to_re'] = conversion_types.get('er_to_re', 0) + 1
                elif 'ize' in american and 'ise' in canadian:
                    conversion_types['ize_to_ise'] = conversion_types.get('ize_to_ise', 0) + 1
                elif 'ization' in american and 'isation' in canadian:
                    conversion_types['ization_to_isation'] = conversion_types.get('ization_to_isation', 0) + 1
                else:
                    conversion_types['other'] = conversion_types.get('other', 0) + 1
            
            return {
                'total_conversions': len(conversions),
                'conversion_patterns': conversion_types,
                'cache_status': 'valid' if self._cached_spellings is not None else 'empty',
                'cache_updated': self._cache_updated.isoformat() if self._cache_updated else None,
                'cache_duration_minutes': self._cache_duration_minutes,
                'sample_conversions': dict(list(conversions.items())[:5]) if conversions else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get processor statistics: {str(e)}")
            return {
                'error': str(e),
                'total_conversions': 0,
                'conversion_patterns': {},
                'cache_status': 'error'
            }
    
    def refresh_spelling_cache(self) -> Dict:
        """
        Force refresh of spelling conversion cache
        
        Returns:
            Cache refresh result
        """
        try:
            self._cached_spellings = None
            self._cache_updated = None
            
            conversions = self._get_spelling_conversions()
            
            return {
                'success': True,
                'message': f'Spelling cache refreshed: {len(conversions)} conversions loaded',
                'conversions_count': len(conversions),
                'sample_conversions': dict(list(conversions.items())[:10]) if conversions else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh spelling cache: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def preview_spelling_changes(self, text: str) -> Dict:
        """
        Preview what spelling changes would be made to text without applying them
        
        Args:
            text: Text to preview changes for
            
        Returns:
            Dictionary with preview information
        """
        try:
            conversions = self._get_spelling_conversions()
            
            if not text or not conversions:
                return {
                    'original_text': text,
                    'preview_text': text,
                    'changes_preview': [],
                    'changes_count': 0
                }
            
            preview_text, changes_made = self._apply_spelling_conversions(text, conversions)
            
            return {
                'original_text': text,
                'preview_text': preview_text,
                'changes_preview': changes_made,
                'changes_count': len(changes_made),
                'has_changes': len(changes_made) > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to preview spelling changes: {str(e)}")
            return {
                'error': str(e),
                'original_text': text,
                'preview_text': text,
                'changes_preview': [],
                'changes_count': 0
            }

# Utility functions for external integration

def process_sentences_through_canadian_spelling(sentences: List[Dict], session_id: Optional[str] = None) -> List[Dict]:
    """
    Convenience function to process sentences through Canadian spelling correction
    
    Args:
        sentences: List of sentence dictionaries
        session_id: Optional session identifier
        
    Returns:
        List of processing results
    """
    import asyncio
    
    if session_id is None:
        session_id = f"canadian_spelling_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    processor = CanadianSpellingProcessor()
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(processor.process_batch(sentences, session_id))
    finally:
        loop.close()

def get_canadian_spelling_processor_status() -> Dict:
    """Get Canadian spelling processor status and statistics"""
    processor = CanadianSpellingProcessor()
    return processor.get_processor_statistics()

def preview_text_spelling_changes(text: str) -> Dict:
    """Preview Canadian spelling changes for given text"""
    processor = CanadianSpellingProcessor()
    return processor.preview_spelling_changes(text)