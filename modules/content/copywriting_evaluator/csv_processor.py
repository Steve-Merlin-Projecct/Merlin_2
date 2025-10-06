#!/usr/bin/env python3
"""
CSV Processor for Copywriting Evaluator System

Handles CSV file detection, parsing, and database ingestion for sentence data.
Supports both immediate and scheduled processing modes with comprehensive validation.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import csv
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

# Database integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class CSVValidationError(Exception):
    """Raised when CSV validation fails"""
    pass

class CSVProcessingError(Exception):
    """Raised when CSV processing fails"""
    pass

class CSVProcessor:
    """
    CSV file detection, parsing, and database ingestion for sentence data
    
    Features:
    - Automatic file detection and validation
    - Schema validation against database structure
    - Batch processing with transaction safety
    - Duplicate detection and handling
    - Comprehensive error reporting
    - Support for both sentence bank tables
    """
    
    def __init__(self):
        """Initialize CSV processor"""
        self.db = DatabaseManager()
        
        # Define expected CSV schemas for each table type
        self.cover_letter_schema = {
            'required': ['content_text'],
            'optional': ['tone', 'tone_strength', 'status', 'position_label', 
                        'matches_job_skill', 'variable'],
            'table_name': 'sentence_bank_cover_letter'
        }
        
        self.resume_schema = {
            'required': ['content_text'],
            'optional': ['tone', 'tone_strength', 'status', 'body_section',
                        'matches_job_skill', 'experience_id'],
            'table_name': 'sentence_bank_resume'
        }
        
        logger.info("CSV processor initialized")
    
    def detect_csv_files(self, directory_path: str, pattern: str = "*.csv") -> List[str]:
        """
        Detect CSV files in specified directory
        
        Args:
            directory_path: Directory to search for CSV files
            pattern: File pattern to match (default: "*.csv")
            
        Returns:
            List of CSV file paths found
        """
        try:
            directory = Path(directory_path)
            if not directory.exists():
                logger.warning(f"Directory does not exist: {directory_path}")
                return []
            
            csv_files = list(directory.glob(pattern))
            file_paths = [str(f) for f in csv_files if f.is_file()]
            
            logger.info(f"Found {len(file_paths)} CSV files in {directory_path}")
            return file_paths
            
        except Exception as e:
            logger.error(f"Error detecting CSV files: {str(e)}")
            return []
    
    def validate_csv_structure(self, csv_file_path: str, table_name: str) -> Tuple[bool, str, Dict]:
        """
        Validate CSV file structure against expected schema
        
        Args:
            csv_file_path: Path to CSV file
            table_name: Target database table name
            
        Returns:
            Tuple of (is_valid, error_message, file_info)
        """
        try:
            # Get appropriate schema
            schema = None
            if table_name == 'sentence_bank_cover_letter':
                schema = self.cover_letter_schema
            elif table_name == 'sentence_bank_resume':
                schema = self.resume_schema
            else:
                return False, f"Unknown table name: {table_name}", {}
            
            # Check file exists and is readable
            if not os.path.exists(csv_file_path):
                return False, f"File does not exist: {csv_file_path}", {}
            
            if not os.access(csv_file_path, os.R_OK):
                return False, f"File is not readable: {csv_file_path}", {}
            
            # Get file info
            file_stat = os.stat(csv_file_path)
            file_info = {
                'file_path': csv_file_path,
                'file_size_bytes': file_stat.st_size,
                'last_modified': datetime.fromtimestamp(file_stat.st_mtime),
                'target_table': table_name
            }
            
            # Read and validate CSV structure
            with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
                # Try to detect CSV dialect
                try:
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample, delimiters=',;\t')
                    has_header = sniffer.has_header(sample)
                    file_info['has_header'] = has_header
                except:
                    dialect = csv.excel
                    has_header = True
                    file_info['has_header'] = True
                
                reader = csv.reader(csvfile, dialect)
                
                try:
                    headers = next(reader)
                    file_info['headers'] = headers
                    file_info['column_count'] = len(headers)
                    
                    # Count rows
                    row_count = sum(1 for row in reader)
                    file_info['data_rows'] = row_count
                    
                except StopIteration:
                    return False, "CSV file is empty", file_info
            
            # Validate required columns
            missing_required = set(schema['required']) - set(headers)
            if missing_required:
                return False, f"Missing required columns: {', '.join(missing_required)}", file_info
            
            # Check for unknown columns (warning only)
            all_allowed = set(schema['required'] + schema['optional'])
            unknown_columns = set(headers) - all_allowed
            if unknown_columns:
                logger.warning(f"Unknown columns will be ignored: {', '.join(unknown_columns)}")
                file_info['unknown_columns'] = list(unknown_columns)
            
            file_info['valid_columns'] = [col for col in headers if col in all_allowed]
            
            return True, "CSV structure valid", file_info
            
        except Exception as e:
            logger.error(f"CSV validation error: {str(e)}")
            return False, f"Validation error: {str(e)}", {}
    
    def parse_csv_data(self, csv_file_path: str, file_info: Dict) -> List[Dict]:
        """
        Parse CSV data into standardized dictionaries
        
        Args:
            csv_file_path: Path to CSV file
            file_info: File information from validation
            
        Returns:
            List of parsed row dictionaries
        """
        parsed_rows = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Parse and clean row data
                        parsed_row = self._parse_row_data(row, file_info['target_table'], row_num)
                        if parsed_row:
                            parsed_rows.append(parsed_row)
                    except Exception as e:
                        logger.error(f"Error parsing row {row_num}: {str(e)}")
                        # Continue processing other rows
            
            logger.info(f"Parsed {len(parsed_rows)} valid rows from {csv_file_path}")
            return parsed_rows
            
        except Exception as e:
            logger.error(f"Error parsing CSV data: {str(e)}")
            raise CSVProcessingError(f"Failed to parse CSV data: {str(e)}")
    
    def _parse_row_data(self, row: Dict, table_name: str, row_num: int) -> Optional[Dict]:
        """
        Parse and validate individual row data
        
        Args:
            row: Raw CSV row dictionary
            table_name: Target table name
            row_num: Row number for error reporting
            
        Returns:
            Parsed and validated row dictionary or None if invalid
        """
        try:
            # Basic validation - content_text is required
            content_text = row.get('content_text', '').strip()
            if not content_text:
                logger.warning(f"Row {row_num}: Empty content_text, skipping")
                return None
            
            if len(content_text) > 10000:  # Reasonable limit
                logger.warning(f"Row {row_num}: content_text too long, truncating")
                content_text = content_text[:10000]
            
            # Build base row data
            parsed = {
                'content_text': content_text,
                'tone': row.get('tone', '').strip() or None,
                'tone_strength': self._parse_numeric(row.get('tone_strength')),
                'status': row.get('status', '').strip() or 'Draft',
                'matches_job_skill': row.get('matches_job_skill', '').strip() or None,
                # Processing status columns default to 'pending'
                'keyword_filter_status': 'pending',
                'truthfulness_status': 'pending',
                'canadian_spelling_status': 'pending', 
                'tone_analysis_status': 'pending',
                'skill_analysis_status': 'pending'
            }
            
            # Add table-specific columns
            if table_name == 'sentence_bank_cover_letter':
                parsed['position_label'] = row.get('position_label', '').strip() or None
                parsed['variable'] = self._parse_boolean(row.get('variable', 'false'))
            elif table_name == 'sentence_bank_resume':
                parsed['body_section'] = row.get('body_section', '').strip() or None
                parsed['experience_id'] = self._parse_uuid(row.get('experience_id'))
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing row {row_num}: {str(e)}")
            return None
    
    def _parse_numeric(self, value: Any) -> Optional[float]:
        """Parse numeric value with error handling"""
        if not value or str(value).strip() == '':
            return None
        try:
            return float(str(value).strip())
        except (ValueError, TypeError):
            return None
    
    def _parse_boolean(self, value: Any) -> bool:
        """Parse boolean value with error handling"""
        if not value:
            return False
        str_val = str(value).strip().lower()
        return str_val in ('true', '1', 'yes', 'y', 'on')
    
    def _parse_uuid(self, value: Any) -> Optional[str]:
        """Parse UUID value with validation"""
        if not value or str(value).strip() == '':
            return None
        try:
            # Validate UUID format
            uuid_val = str(value).strip()
            uuid.UUID(uuid_val)
            return uuid_val
        except (ValueError, TypeError):
            return None
    
    async def ingest_to_database(self, parsed_data: List[Dict], table_name: str) -> Dict:
        """
        Ingest parsed data into database with duplicate checking
        
        Args:
            parsed_data: List of parsed row dictionaries
            table_name: Target database table
            
        Returns:
            Dictionary with ingestion results
        """
        if not parsed_data:
            return {
                'success': True,
                'inserted_count': 0,
                'duplicate_count': 0,
                'error_count': 0,
                'sentence_ids': [],
                'message': 'No data to ingest'
            }
        
        inserted_ids = []
        duplicate_count = 0
        error_count = 0
        
        try:
            for row in parsed_data:
                try:
                    # Check for duplicates based on content_text
                    duplicate_check = """
                        SELECT id FROM {} WHERE content_text = %s
                    """.format(table_name)
                    
                    existing = self.db.execute_query(duplicate_check, (row['content_text'],))
                    
                    if existing:
                        duplicate_count += 1
                        logger.debug(f"Duplicate content found, skipping: {row['content_text'][:50]}...")
                        continue
                    
                    # Generate UUID for new record
                    sentence_id = str(uuid.uuid4())
                    
                    # Build insert query based on table
                    if table_name == 'sentence_bank_cover_letter':
                        insert_query = """
                            INSERT INTO sentence_bank_cover_letter (
                                id, content_text, tone, tone_strength, status, position_label,
                                matches_job_skill, variable, keyword_filter_status,
                                truthfulness_status, canadian_spelling_status,
                                tone_analysis_status, skill_analysis_status, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        params = (
                            sentence_id, row['content_text'], row['tone'], row['tone_strength'],
                            row['status'], row['position_label'], row['matches_job_skill'],
                            row['variable'], row['keyword_filter_status'], row['truthfulness_status'],
                            row['canadian_spelling_status'], row['tone_analysis_status'],
                            row['skill_analysis_status'], datetime.now()
                        )
                    else:  # sentence_bank_resume
                        insert_query = """
                            INSERT INTO sentence_bank_resume (
                                id, content_text, tone, tone_strength, status, body_section,
                                matches_job_skill, experience_id, keyword_filter_status,
                                truthfulness_status, canadian_spelling_status,
                                tone_analysis_status, skill_analysis_status, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        params = (
                            sentence_id, row['content_text'], row['tone'], row['tone_strength'],
                            row['status'], row['body_section'], row['matches_job_skill'],
                            row['experience_id'], row['keyword_filter_status'], row['truthfulness_status'],
                            row['canadian_spelling_status'], row['tone_analysis_status'],
                            row['skill_analysis_status'], datetime.now()
                        )
                    
                    self.db.execute_query(insert_query, params)
                    inserted_ids.append(sentence_id)
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error inserting row: {str(e)}")
            
            logger.info(f"Database ingestion complete: {len(inserted_ids)} inserted, "
                       f"{duplicate_count} duplicates, {error_count} errors")
            
            return {
                'success': True,
                'inserted_count': len(inserted_ids),
                'duplicate_count': duplicate_count,
                'error_count': error_count,
                'sentence_ids': inserted_ids,
                'message': f"Ingested {len(inserted_ids)} new sentences successfully"
            }
            
        except Exception as e:
            logger.error(f"Database ingestion failed: {str(e)}")
            raise CSVProcessingError(f"Database ingestion failed: {str(e)}")
    
    async def process_csv_file(self, csv_file_path: str, table_name: str) -> Dict:
        """
        Complete CSV file processing pipeline
        
        Args:
            csv_file_path: Path to CSV file to process
            table_name: Target database table ('sentence_bank_cover_letter' or 'sentence_bank_resume')
            
        Returns:
            Dictionary with comprehensive processing results
        """
        processing_start = datetime.now()
        
        try:
            logger.info(f"Starting CSV processing: {csv_file_path} -> {table_name}")
            
            # Step 1: Validate CSV structure
            is_valid, error_msg, file_info = self.validate_csv_structure(csv_file_path, table_name)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'file_info': file_info,
                    'sentence_ids': []
                }
            
            logger.info(f"CSV validation passed: {file_info['data_rows']} rows, "
                       f"{file_info['column_count']} columns")
            
            # Step 2: Parse CSV data
            parsed_data = self.parse_csv_data(csv_file_path, file_info)
            if not parsed_data:
                return {
                    'success': True,
                    'message': 'No valid data rows found in CSV',
                    'file_info': file_info,
                    'sentence_ids': []
                }
            
            # Step 3: Ingest to database
            ingestion_result = await self.ingest_to_database(parsed_data, table_name)
            
            # Combine results
            processing_time = (datetime.now() - processing_start).total_seconds()
            
            result = {
                'success': ingestion_result['success'],
                'file_info': file_info,
                'parsed_rows': len(parsed_data),
                'inserted_count': ingestion_result['inserted_count'],
                'duplicate_count': ingestion_result['duplicate_count'],
                'error_count': ingestion_result['error_count'],
                'sentence_ids': ingestion_result['sentence_ids'],
                'processing_time_seconds': processing_time,
                'message': ingestion_result['message']
            }
            
            logger.info(f"CSV processing complete: {result['message']} "
                       f"({processing_time:.2f}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"CSV processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'sentence_ids': [],
                'processing_time_seconds': (datetime.now() - processing_start).total_seconds()
            }

    async def process_directory(self, directory_path: str, table_name: str, 
                              file_pattern: str = "*.csv") -> Dict:
        """
        Process all CSV files in a directory
        
        Args:
            directory_path: Directory containing CSV files
            table_name: Target database table
            file_pattern: File pattern to match
            
        Returns:
            Dictionary with aggregated processing results
        """
        try:
            csv_files = self.detect_csv_files(directory_path, file_pattern)
            
            if not csv_files:
                return {
                    'success': True,
                    'message': f'No CSV files found in {directory_path}',
                    'processed_files': 0,
                    'total_sentences': 0,
                    'sentence_ids': []
                }
            
            all_results = []
            total_sentences = 0
            all_sentence_ids = []
            
            for csv_file in csv_files:
                logger.info(f"Processing file: {csv_file}")
                result = await self.process_csv_file(csv_file, table_name)
                all_results.append({
                    'file': csv_file,
                    'result': result
                })
                
                if result.get('success'):
                    total_sentences += result.get('inserted_count', 0)
                    all_sentence_ids.extend(result.get('sentence_ids', []))
            
            successful_files = sum(1 for r in all_results if r['result'].get('success'))
            
            return {
                'success': True,
                'processed_files': len(csv_files),
                'successful_files': successful_files,
                'failed_files': len(csv_files) - successful_files,
                'total_sentences': total_sentences,
                'sentence_ids': all_sentence_ids,
                'file_results': all_results,
                'message': f'Processed {successful_files}/{len(csv_files)} files successfully'
            }
            
        except Exception as e:
            logger.error(f"Directory processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processed_files': 0,
                'total_sentences': 0,
                'sentence_ids': []
            }