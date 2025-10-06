"""
Normalized Database Writer for AI Job Analysis
Saves AI analysis results to normalized relational tables instead of JSONB
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class NormalizedAnalysisWriter:
    """
    Writes AI analysis results to normalized database tables
    Replaces the JSONB approach with proper relational structure
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def save_analysis_results(self, results: List[Dict]) -> Dict[str, int]:
        """
        Save analysis results to normalized tables
        
        Args:
            results: List of analysis result dictionaries from AI analyzer
            
        Returns:
            Dictionary with counts of saved records per table
        """
        
        stats = {
            'jobs_updated': 0,
            'job_skills': 0,
            'job_benefits': 0,
            'job_required_documents': 0,
            'job_stress_indicators': 0,
            'job_certifications': 0,
            'job_ats_keywords': 0,
            'job_red_flags_details': 0,
            'errors': 0
        }
        
        for result in results:
            try:
                # Update jobs table with analysis results
                if self._update_job_with_analysis(result):
                    stats['jobs_updated'] += 1
                    
                    # Save related records to normalized tables
                    stats['job_skills'] += self._save_job_skills(result)
                    stats['job_benefits'] += self._save_job_benefits(result)
                    stats['job_required_documents'] += self._save_required_documents(result)
                    stats['job_stress_indicators'] += self._save_stress_indicators(result)
                    stats['job_certifications'] += self._save_certifications(result)
                    stats['job_ats_keywords'] += self._save_ats_keywords(result)
                    stats['job_red_flags_details'] += self._save_red_flags_details(result)
                    
                else:
                    stats['errors'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to save analysis for job {result.get('job_id')}: {str(e)}")
                stats['errors'] += 1
                
        return stats
    
    def _update_job_with_analysis(self, result: Dict) -> bool:
        """Update jobs table with AI analysis results"""
        
        try:
            job_id = result.get('job_id')
            if not job_id:
                logger.error("No job_id found in analysis result")
                return False
                
            # Extract data from various sections
            auth_check = result.get('authenticity_check', {})
            classification = result.get('classification', {})
            structured_data = result.get('structured_data', {})
            stress_analysis = result.get('stress_level_analysis', {})
            red_flags = result.get('red_flags', {})
            cover_letter_insight = result.get('cover_letter_insight', {})
            
            # Extract nested data
            skill_requirements = structured_data.get('skill_requirements', {})
            work_arrangement = structured_data.get('work_arrangement', {})
            compensation = structured_data.get('compensation', {})
            application_details = structured_data.get('application_details', {})
            
            # Parse office location into components
            office_location = work_arrangement.get('office_location', '')
            office_parts = self._parse_office_location(office_location)
            
            # Build update query for jobs table
            update_query = """
                UPDATE jobs SET
                    -- Authenticity Analysis
                    title_matches_role = %s,
                    mismatch_explanation = %s,
                    is_authentic = %s,
                    authenticity_reasoning = %s,
                    
                    -- Classification
                    sub_industry = %s,
                    job_function = %s,
                    
                    -- Work Arrangement
                    in_office_requirements = %s,
                    office_address = %s,
                    office_city = %s,
                    office_province = %s,
                    office_country = %s,
                    working_hours_per_week = %s,
                    work_schedule = %s,
                    specific_schedule = %s,
                    travel_requirements = %s,
                    
                    -- Compensation
                    salary_mentioned = %s,
                    equity_stock_options = %s,
                    commission_or_performance_incentive = %s,
                    est_total_compensation = %s,
                    compensation_currency = %s,
                    
                    -- Application Details
                    application_email = %s,
                    special_instructions = %s,
                    
                    -- Stress Analysis
                    estimated_stress_level = %s,
                    stress_reasoning = %s,
                    
                    -- Education & Experience
                    education_requirements = %s,
                    
                    -- Red Flags
                    overall_red_flag_reasoning = %s,
                    
                    -- Cover Letter Insight
                    cover_letter_pain_point = %s,
                    cover_letter_evidence = %s,
                    cover_letter_solution_angle = %s,
                    
                    -- Analysis metadata
                    analysis_completed = TRUE
                WHERE id = %s
            """
            
            # Extract cover letter insight details
            pain_point_data = cover_letter_insight.get('employer_pain_point', {})
            
            params = [
                # Authenticity Analysis
                auth_check.get('title_matches_role'),
                auth_check.get('mismatch_explanation'),
                auth_check.get('is_authentic'),
                auth_check.get('reasoning'),
                
                # Classification
                classification.get('sub_industry'),
                classification.get('job_function'),
                
                # Work Arrangement
                work_arrangement.get('in_office_requirements'),
                office_parts.get('address'),
                office_parts.get('city'),
                office_parts.get('province'),
                office_parts.get('country'),
                work_arrangement.get('working_hours_per_week'),
                work_arrangement.get('work_schedule'),
                work_arrangement.get('specific_schedule'),
                work_arrangement.get('travel_requirements'),
                
                # Compensation
                compensation.get('salary_mentioned'),
                compensation.get('equity_stock_options'),
                compensation.get('commission_or_performance_incentive'),
                compensation.get('est_total_compensation'),
                compensation.get('compensation_currency'),
                
                # Application Details
                application_details.get('application_email'),
                application_details.get('special_instructions'),
                
                # Stress Analysis
                stress_analysis.get('estimated_stress_level'),
                stress_analysis.get('reasoning'),
                
                # Education & Experience
                skill_requirements.get('education_requirements'),
                
                # Red Flags
                red_flags.get('overall_red_flag_reasoning'),
                
                # Cover Letter Insight
                pain_point_data.get('pain_point'),
                pain_point_data.get('evidence'),
                pain_point_data.get('solution_angle'),
                
                # Job ID for WHERE clause
                job_id
            ]
            
            cursor = self.db_manager.connection.cursor()
            cursor.execute(update_query, params)
            self.db_manager.connection.commit()
            cursor.close()
            
            logger.info(f"Updated job {job_id} with AI analysis results")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job with analysis: {str(e)}")
            return False
    
    def _parse_office_location(self, office_location: str) -> Dict[str, str]:
        """Parse office location string into components"""
        parts = {
            'address': '',
            'city': '',
            'province': '',
            'country': ''
        }
        
        if not office_location:
            return parts
            
        # Split by comma and clean up
        location_parts = [part.strip() for part in office_location.split(',')]
        
        if len(location_parts) == 4:
            parts['address'] = location_parts[0]
            parts['city'] = location_parts[1]
            parts['province'] = location_parts[2]
            parts['country'] = location_parts[3]
        elif len(location_parts) == 3:
            parts['city'] = location_parts[0]
            parts['province'] = location_parts[1]
            parts['country'] = location_parts[2]
        elif len(location_parts) == 2:
            parts['city'] = location_parts[0]
            parts['province'] = location_parts[1]
        elif len(location_parts) == 1:
            parts['city'] = location_parts[0]
            
        return parts
    
    def _save_job_skills(self, result: Dict) -> int:
        """Save job skills to normalized table"""
        count = 0
        job_id = result.get('job_id')
        if not job_id:
            return count
            
        structured_data = result.get('structured_data', {})
        skill_requirements = structured_data.get('skill_requirements', {})
        skills = skill_requirements.get('skills', [])
        
        # Delete existing skills for this job
        delete_query = "DELETE FROM job_skills WHERE job_id = %s"
        cursor = self.db_manager.connection.cursor()
        cursor.execute(delete_query, (job_id,))
        
        # Insert new skills (Note: NOT adding skill_category per user requirement #4)
        insert_query = """
            INSERT INTO job_skills (job_id, skill_name, importance_rating, reasoning, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        for skill in skills:
            skill_name = skill.get('skill_name')
            importance_rating = skill.get('importance_rating')
            reasoning = skill.get('reasoning')
            
            if skill_name:
                cursor.execute(insert_query, (
                    job_id, skill_name, importance_rating, reasoning, datetime.now()
                ))
                count += 1
                
        self.db_manager.connection.commit()
        cursor.close()
        return count
    
    def _save_job_benefits(self, result: Dict) -> int:
        """Save job benefits to normalized table"""
        count = 0
        job_id = result.get('job_id')
        if not job_id:
            return count
            
        structured_data = result.get('structured_data', {})
        compensation = structured_data.get('compensation', {})
        benefits = compensation.get('benefits', [])
        
        # Delete existing benefits for this job
        delete_query = "DELETE FROM job_benefits WHERE job_id = %s"
        cursor = self.db_manager.connection.cursor()
        cursor.execute(delete_query, (job_id,))
        
        # Insert new benefits
        insert_query = """
            INSERT INTO job_benefits (job_id, benefit_name, created_at)
            VALUES (%s, %s, %s)
        """
        
        for benefit in benefits:
            if benefit:  # Skip empty benefits
                cursor.execute(insert_query, (job_id, benefit, datetime.now()))
                count += 1
                
        self.db_manager.connection.commit()
        cursor.close()
        return count
    
    def _save_required_documents(self, result: Dict) -> int:
        """Save required documents to normalized table"""
        count = 0
        job_id = result.get('job_id')
        if not job_id:
            return count
            
        structured_data = result.get('structured_data', {})
        application_details = structured_data.get('application_details', {})
        required_documents = application_details.get('required_documents', [])
        
        # Delete existing documents for this job
        delete_query = "DELETE FROM job_required_documents WHERE job_id = %s"
        cursor = self.db_manager.connection.cursor()
        cursor.execute(delete_query, (job_id,))
        
        # Insert new required documents
        insert_query = """
            INSERT INTO job_required_documents (job_id, document_type, is_required, created_at)
            VALUES (%s, %s, %s, %s)
        """
        
        for doc_type in required_documents:
            if doc_type:  # Skip empty document types
                cursor.execute(insert_query, (job_id, doc_type, True, datetime.now()))
                count += 1
                
        self.db_manager.connection.commit()
        cursor.close()
        return count
    
    def _save_stress_indicators(self, result: Dict) -> int:
        """Save stress indicators to normalized table"""
        count = 0
        job_id = result.get('job_id')
        if not job_id:
            return count
            
        stress_analysis = result.get('stress_level_analysis', {})
        stress_indicators = stress_analysis.get('stress_indicators', [])
        
        # Delete existing stress indicators for this job
        delete_query = "DELETE FROM job_stress_indicators WHERE job_id = %s"
        cursor = self.db_manager.connection.cursor()
        cursor.execute(delete_query, (job_id,))
        
        # Insert new stress indicators
        insert_query = """
            INSERT INTO job_stress_indicators (job_id, indicator, created_at)
            VALUES (%s, %s, %s)
        """
        
        for indicator in stress_indicators:
            if indicator:  # Skip empty indicators
                cursor.execute(insert_query, (job_id, indicator, datetime.now()))
                count += 1
                
        self.db_manager.connection.commit()
        cursor.close()
        return count
    
    def _save_certifications(self, result: Dict) -> int:
        """Save certifications to normalized table"""
        count = 0
        job_id = result.get('job_id')
        if not job_id:
            return count
            
        structured_data = result.get('structured_data', {})
        skill_requirements = structured_data.get('skill_requirements', {})
        certifications = skill_requirements.get('certifications', [])
        
        # Delete existing certifications for this job
        delete_query = "DELETE FROM job_certifications WHERE job_id = %s"
        cursor = self.db_manager.connection.cursor()
        cursor.execute(delete_query, (job_id,))
        
        # Insert new certifications
        insert_query = """
            INSERT INTO job_certifications (job_id, certification_name, is_required, created_at)
            VALUES (%s, %s, %s, %s)
        """
        
        for cert in certifications:
            if cert:  # Skip empty certifications
                cursor.execute(insert_query, (job_id, cert, True, datetime.now()))
                count += 1
                
        self.db_manager.connection.commit()
        cursor.close()
        return count
    
    def _save_ats_keywords(self, result: Dict) -> int:
        """Save ATS keywords to normalized table"""
        count = 0
        job_id = result.get('job_id')
        if not job_id:
            return count
            
        structured_data = result.get('structured_data', {})
        ats_optimization = structured_data.get('ats_optimization', {})
        
        # Delete existing ATS keywords for this job
        delete_query = "DELETE FROM job_ats_keywords WHERE job_id = %s"
        cursor = self.db_manager.connection.cursor()
        cursor.execute(delete_query, (job_id,))
        
        # Insert new ATS keywords
        insert_query = """
            INSERT INTO job_ats_keywords (job_id, keyword_type, keyword, created_at)
            VALUES (%s, %s, %s, %s)
        """
        
        # Save primary keywords
        primary_keywords = ats_optimization.get('primary_keywords', [])
        for keyword in primary_keywords:
            if keyword:
                cursor.execute(insert_query, (job_id, 'primary', keyword, datetime.now()))
                count += 1
        
        # Save industry keywords
        industry_keywords = ats_optimization.get('industry_keywords', [])
        for keyword in industry_keywords:
            if keyword:
                cursor.execute(insert_query, (job_id, 'industry', keyword, datetime.now()))
                count += 1
        
        # Save must-have phrases
        must_have_phrases = ats_optimization.get('must_have_phrases', [])
        for phrase in must_have_phrases:
            if phrase:
                cursor.execute(insert_query, (job_id, 'must_have_phrase', phrase, datetime.now()))
                count += 1
                
        self.db_manager.connection.commit()
        cursor.close()
        return count
    
    def _save_red_flags_details(self, result: Dict) -> int:
        """Save red flag details to normalized table"""
        count = 0
        job_id = result.get('job_id')
        if not job_id:
            return count
            
        red_flags = result.get('red_flags', {})
        
        # Delete existing red flags for this job
        delete_query = "DELETE FROM job_red_flags_details WHERE job_id = %s"
        cursor = self.db_manager.connection.cursor()
        cursor.execute(delete_query, (job_id,))
        
        # Insert new red flag details
        insert_query = """
            INSERT INTO job_red_flags_details (job_id, flag_type, detected, details, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        # Save unrealistic expectations red flag
        unrealistic = red_flags.get('unrealistic_expectations', {})
        if unrealistic:
            cursor.execute(insert_query, (
                job_id, 
                'unrealistic_expectations',
                unrealistic.get('detected', False),
                unrealistic.get('details', ''),
                datetime.now()
            ))
            count += 1
        
        # Save potential scam indicators red flag
        scam_indicators = red_flags.get('potential_scam_indicators', {})
        if scam_indicators:
            cursor.execute(insert_query, (
                job_id,
                'potential_scam_indicators', 
                scam_indicators.get('detected', False),
                scam_indicators.get('details', ''),
                datetime.now()
            ))
            count += 1
                
        self.db_manager.connection.commit()
        cursor.close()
        return count
            additional_insights = result.get('additional_insights', {})
            structured_data = additional_insights.get('structured_data', {})
            stress_analysis = additional_insights.get('stress_level_analysis', {})
            
            # Build the main record
            job_analysis_data = {
                'job_id': result.get('job_id'),
                'analysis_timestamp': result.get('analysis_timestamp', datetime.now().isoformat()),
                'model_used': result.get('model_used'),
                'analysis_version': result.get('analysis_version'),
                
                # Authenticity check fields
                'is_authentic': auth_check.get('is_authentic'),
                'authenticity_confidence_score': auth_check.get('confidence_score'),
                'title_match_score': auth_check.get('title_match_score'),
                'authenticity_reasoning': auth_check.get('reasoning'),
                
                # Industry classification fields
                'primary_industry': industry_class.get('primary_industry'),
                'job_function': industry_class.get('job_function'),
                'seniority_level': industry_class.get('seniority_level'),
                'industry_confidence': industry_class.get('confidence'),
                
                # Additional insights fields
                'salary_transparency': additional_insights.get('salary_transparency'),
                'company_size_indicator': additional_insights.get('company_size_indicator'),
                'growth_opportunity': additional_insights.get('growth_opportunity'),
                'work_arrangement': additional_insights.get('work_arrangement'),
                
                # Structured data fields
                'estimated_salary_min': structured_data.get('estimated_salary_min'),
                'estimated_salary_max': structured_data.get('estimated_salary_max'),
                'salary_currency': structured_data.get('salary_currency', 'CAD'),
                'work_hours_per_week': structured_data.get('work_hours_per_week'),
                'overtime_expected': structured_data.get('overtime_expected'),
                'remote_work_percentage': structured_data.get('remote_work_percentage'),
                
                # Stress level analysis
                'stress_level_score': stress_analysis.get('stress_level_score'),
                'workload_intensity': stress_analysis.get('workload_intensity'),
                'deadline_pressure': stress_analysis.get('deadline_pressure'),
                
                # Metrics
                'total_skills_found': result.get('skills_analysis', {}).get('total_skills_found', 0)
            }
            
            # Clean None values and prepare for database
            clean_data = {k: v for k, v in job_analysis_data.items() if v is not None}
            
            # Build INSERT query
            columns = list(clean_data.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            values = list(clean_data.values())
            
            query = f"""
            INSERT INTO job_analysis ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT (job_id) DO UPDATE SET
                {', '.join([f'{col} = EXCLUDED.{col}' for col in columns if col != 'job_id'])}
            """
            
            self.db_manager.execute_query(query, values)
            return True
            
        except Exception as e:
            logger.error(f"Failed to save job_analysis: {str(e)}")
            return False
    
    def _save_job_skills(self, result: Dict) -> int:
        """Save skills analysis to job_skills table"""
        
        skills_analysis = result.get('skills_analysis', {})
        top_skills = skills_analysis.get('top_skills', [])
        job_id = result.get('job_id')
        
        if not top_skills or not job_id:
            return 0
            
        saved_count = 0
        
        # Clear existing skills for this job
        self.db_manager.execute_query(
            "DELETE FROM job_skills WHERE job_id = %s", (job_id,)
        )
        
        for skill in top_skills:
            try:
                query = """
                INSERT INTO job_skills (job_id, skill_name, importance_rating, skill_category, is_required)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                self.db_manager.execute_query(query, (
                    job_id,
                    skill.get('skill'),
                    skill.get('importance_rating'),
                    skill.get('category'),
                    skill.get('is_required', False)
                ))
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save skill {skill.get('skill')}: {str(e)}")
                
        return saved_count
    
    def _save_secondary_industries(self, result: Dict) -> int:
        """Save secondary industries to job_secondary_industries table"""
        
        industry_class = result.get('industry_classification', {})
        secondary_industries = industry_class.get('secondary_industries', [])
        job_id = result.get('job_id')
        
        if not secondary_industries or not job_id:
            return 0
            
        saved_count = 0
        
        # Clear existing secondary industries for this job
        self.db_manager.execute_query(
            "DELETE FROM job_secondary_industries WHERE job_id = %s", (job_id,)
        )
        
        for industry in secondary_industries:
            try:
                query = """
                INSERT INTO job_secondary_industries (job_id, industry_name)
                VALUES (%s, %s)
                """
                
                self.db_manager.execute_query(query, (job_id, industry))
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save secondary industry {industry}: {str(e)}")
                
        return saved_count
    
    def _save_authenticity_red_flags(self, result: Dict) -> int:
        """Save authenticity red flags to job_authenticity_red_flags table"""
        
        auth_check = result.get('authenticity_check', {})
        red_flags = auth_check.get('red_flags', [])
        job_id = result.get('job_id')
        
        if not red_flags or not job_id:
            return 0
            
        saved_count = 0
        
        # Clear existing red flags for this job
        self.db_manager.execute_query(
            "DELETE FROM job_authenticity_red_flags WHERE job_id = %s", (job_id,)
        )
        
        for flag in red_flags:
            try:
                query = """
                INSERT INTO job_authenticity_red_flags (job_id, red_flag_type, red_flag_description)
                VALUES (%s, %s, %s)
                """
                
                self.db_manager.execute_query(query, (job_id, flag, flag))
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save authenticity red flag {flag}: {str(e)}")
                
        return saved_count
    
    def _save_implicit_requirements(self, result: Dict) -> int:
        """Save implicit requirements to job_implicit_requirements table"""
        
        additional_insights = result.get('additional_insights', {})
        implicit_reqs = additional_insights.get('implicit_requirements', {})
        job_id = result.get('job_id')
        
        if not implicit_reqs or not job_id:
            return 0
            
        saved_count = 0
        
        # Clear existing implicit requirements for this job
        self.db_manager.execute_query(
            "DELETE FROM job_implicit_requirements WHERE job_id = %s", (job_id,)
        )
        
        for req_type, req_data in implicit_reqs.items():
            try:
                # Handle both string and dict formats
                if isinstance(req_data, dict):
                    description = req_data.get('description', str(req_data))
                    importance = req_data.get('importance_level', 'medium')
                else:
                    description = str(req_data)
                    importance = 'medium'
                
                query = """
                INSERT INTO job_implicit_requirements (job_id, requirement_type, requirement_description, importance_level)
                VALUES (%s, %s, %s, %s)
                """
                
                self.db_manager.execute_query(query, (job_id, req_type, description, importance))
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save implicit requirement {req_type}: {str(e)}")
                
        return saved_count
    
    def _save_cover_letter_insights(self, result: Dict) -> int:
        """Save cover letter insights to job_cover_letter_insights table"""
        
        additional_insights = result.get('additional_insights', {})
        cover_insights = additional_insights.get('cover_letter_insights', {})
        job_id = result.get('job_id')
        
        if not cover_insights or not job_id:
            return 0
            
        saved_count = 0
        
        # Clear existing cover letter insights for this job
        self.db_manager.execute_query(
            "DELETE FROM job_cover_letter_insights WHERE job_id = %s", (job_id,)
        )
        
        for insight_type, insight_data in cover_insights.items():
            try:
                # Handle both string and dict formats
                if isinstance(insight_data, dict):
                    description = insight_data.get('description', str(insight_data))
                    strategic_value = insight_data.get('strategic_value', 'medium')
                else:
                    description = str(insight_data)
                    strategic_value = 'medium'
                
                query = """
                INSERT INTO job_cover_letter_insights (job_id, insight_type, insight_description, strategic_value)
                VALUES (%s, %s, %s, %s)
                """
                
                self.db_manager.execute_query(query, (job_id, insight_type, description, strategic_value))
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save cover letter insight {insight_type}: {str(e)}")
                
        return saved_count
    
    def _save_ats_keywords(self, result: Dict) -> int:
        """Save ATS keywords to job_ats_keywords table"""
        
        additional_insights = result.get('additional_insights', {})
        structured_data = additional_insights.get('structured_data', {})
        ats_optimization = structured_data.get('ats_optimization', {})
        keywords = ats_optimization.get('keywords', [])
        job_id = result.get('job_id')
        
        if not keywords or not job_id:
            return 0
            
        saved_count = 0
        
        # Clear existing ATS keywords for this job
        self.db_manager.execute_query(
            "DELETE FROM job_ats_keywords WHERE job_id = %s", (job_id,)
        )
        
        for keyword_data in keywords:
            try:
                # Handle both string and dict formats
                if isinstance(keyword_data, dict):
                    keyword = keyword_data.get('keyword', str(keyword_data))
                    category = keyword_data.get('category', 'important')
                    frequency = keyword_data.get('frequency', 1)
                else:
                    keyword = str(keyword_data)
                    category = 'important'
                    frequency = 1
                
                query = """
                INSERT INTO job_ats_keywords (job_id, keyword, keyword_category, frequency_in_posting)
                VALUES (%s, %s, %s, %s)
                """
                
                self.db_manager.execute_query(query, (job_id, keyword, category, frequency))
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save ATS keyword {keyword}: {str(e)}")
                
        return saved_count
    
    def _save_red_flags(self, result: Dict) -> int:
        """Save general red flags to job_red_flags table"""
        
        additional_insights = result.get('additional_insights', {})
        red_flags = additional_insights.get('red_flags', {})
        job_id = result.get('job_id')
        
        if not red_flags or not job_id:
            return 0
            
        saved_count = 0
        
        # Clear existing red flags for this job
        self.db_manager.execute_query(
            "DELETE FROM job_red_flags WHERE job_id = %s", (job_id,)
        )
        
        for flag_category, flag_data in red_flags.items():
            try:
                # Handle both string and dict formats
                if isinstance(flag_data, dict):
                    description = flag_data.get('description', str(flag_data))
                    severity = flag_data.get('severity_level', 'medium')
                else:
                    description = str(flag_data)
                    severity = 'medium'
                
                query = """
                INSERT INTO job_red_flags (job_id, flag_category, flag_description, severity_level)
                VALUES (%s, %s, %s, %s)
                """
                
                self.db_manager.execute_query(query, (job_id, flag_category, description, severity))
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Failed to save red flag {flag_category}: {str(e)}")
                
        return saved_count