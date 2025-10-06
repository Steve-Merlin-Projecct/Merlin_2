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
            "jobs_updated": 0,
            "job_skills": 0,
            "job_benefits": 0,
            "job_required_documents": 0,
            "job_stress_indicators": 0,
            "job_certifications": 0,
            "job_ats_keywords": 0,
            "job_red_flags_details": 0,
            "job_education_requirements": 0,
            "errors": 0,
        }

        for result in results:
            try:
                # Update jobs table with analysis results
                if self._update_job_with_analysis(result):
                    stats["jobs_updated"] += 1

                    # Save related records to normalized tables
                    stats["job_skills"] += self._save_job_skills(result)
                    stats["job_benefits"] += self._save_job_benefits(result)
                    stats["job_required_documents"] += self._save_required_documents(result)
                    stats["job_stress_indicators"] += self._save_stress_indicators(result)
                    stats["job_certifications"] += self._save_certifications(result)
                    stats["job_ats_keywords"] += self._save_ats_keywords(result)
                    stats["job_red_flags_details"] += self._save_red_flags_details(result)
                    stats["job_education_requirements"] += self._save_education_requirements(result)

                else:
                    stats["errors"] += 1

            except Exception as e:
                logger.error(f"Failed to save analysis for job {result.get('job_id')}: {str(e)}")
                stats["errors"] += 1

        return stats

    def _update_job_with_analysis(self, result: Dict) -> bool:
        """Update jobs table with AI analysis results"""

        try:
            job_id = result.get("job_id")
            if not job_id:
                logger.error("No job_id found in analysis result")
                return False

            # Extract data from various sections
            auth_check = result.get("authenticity_check", {})
            classification = result.get("classification", {})
            structured_data = result.get("structured_data", {})
            stress_analysis = result.get("stress_level_analysis", {})
            red_flags = result.get("red_flags", {})
            cover_letter_insight = result.get("cover_letter_insight", {})
            prestige_analysis = result.get("prestige_analysis", {})

            # Extract nested data
            skill_requirements = structured_data.get("skill_requirements", {})
            work_arrangement = structured_data.get("work_arrangement", {})
            compensation = structured_data.get("compensation", {})
            application_details = structured_data.get("application_details", {})

            # Parse office location into components
            office_location = work_arrangement.get("office_location", "")
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
                    
                    -- Prestige Analysis
                    prestige_factor = %s,
                    prestige_reasoning = %s,
                    supervision_count = %s,
                    budget_size_category = %s,
                    company_size_category = %s,
                    
                    -- Analysis metadata
                    analysis_completed = TRUE
                WHERE id = %s
            """

            # Extract cover letter insight details
            pain_point_data = cover_letter_insight.get("employer_pain_point", {})

            params = [
                # Authenticity Analysis
                auth_check.get("title_matches_role"),
                auth_check.get("mismatch_explanation"),
                auth_check.get("is_authentic"),
                auth_check.get("reasoning"),
                # Classification
                classification.get("sub_industry"),
                classification.get("job_function"),
                # Work Arrangement
                work_arrangement.get("in_office_requirements"),
                office_parts.get("address"),
                office_parts.get("city"),
                office_parts.get("province"),
                office_parts.get("country"),
                work_arrangement.get("working_hours_per_week"),
                work_arrangement.get("work_schedule"),
                work_arrangement.get("specific_schedule"),
                work_arrangement.get("travel_requirements"),
                # Compensation
                compensation.get("salary_mentioned"),
                compensation.get("equity_stock_options"),
                compensation.get("commission_or_performance_incentive"),
                compensation.get("est_total_compensation"),
                compensation.get("compensation_currency"),
                # Application Details
                application_details.get("application_email"),
                application_details.get("special_instructions"),
                # Stress Analysis
                stress_analysis.get("estimated_stress_level"),
                stress_analysis.get("reasoning"),
                # Education & Experience
                skill_requirements.get("education_requirements"),
                # Red Flags
                red_flags.get("overall_red_flag_reasoning"),
                # Cover Letter Insight
                pain_point_data.get("pain_point"),
                pain_point_data.get("evidence"),
                pain_point_data.get("solution_angle"),
                # Prestige Analysis
                prestige_analysis.get("prestige_factor"),
                prestige_analysis.get("prestige_reasoning"),
                prestige_analysis.get("supervision_scope", {}).get("supervision_count", 0),
                prestige_analysis.get("budget_responsibility", {}).get("budget_size_category"),
                prestige_analysis.get("company_prestige", {}).get("company_size_category"),
                # Job ID for WHERE clause
                job_id,
            ]

            # Use database manager's execute_query method instead of direct connection
            self.db_manager.execute_query(update_query, params)

            logger.info(f"Updated job {job_id} with AI analysis results")
            return True

        except Exception as e:
            logger.error(f"Failed to update job with analysis: {str(e)}")
            return False

    def _parse_office_location(self, office_location: str) -> Dict[str, str]:
        """Parse office location string into components"""
        parts = {"address": "", "city": "", "province": "", "country": ""}

        if not office_location:
            return parts

        # Split by comma and clean up
        location_parts = [part.strip() for part in office_location.split(",")]

        if len(location_parts) == 4:
            parts["address"] = location_parts[0]
            parts["city"] = location_parts[1]
            parts["province"] = location_parts[2]
            parts["country"] = location_parts[3]
        elif len(location_parts) == 3:
            parts["city"] = location_parts[0]
            parts["province"] = location_parts[1]
            parts["country"] = location_parts[2]
        elif len(location_parts) == 2:
            parts["city"] = location_parts[0]
            parts["province"] = location_parts[1]
        elif len(location_parts) == 1:
            parts["city"] = location_parts[0]

        return parts

    def _save_job_skills(self, result: Dict) -> int:
        """Save job skills to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        structured_data = result.get("structured_data", {})
        skill_requirements = structured_data.get("skill_requirements", {})
        skills = skill_requirements.get("skills", [])

        # Delete existing skills for this job
        self.db_manager.execute_query("DELETE FROM job_skills WHERE job_id = %s", (job_id,))

        # Insert new skills (Note: NOT adding skill_category per user requirement #4)
        for skill in skills:
            skill_name = skill.get("skill_name")
            importance_rating = skill.get("importance_rating")
            reasoning = skill.get("reasoning")

            if skill_name:
                insert_query = """
                    INSERT INTO job_skills (job_id, skill_name, importance_rating, reasoning, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.db_manager.execute_query(
                    insert_query, (job_id, skill_name, importance_rating, reasoning, datetime.now())
                )
                count += 1

        return count

    def _save_job_benefits(self, result: Dict) -> int:
        """Save job benefits to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        structured_data = result.get("structured_data", {})
        compensation = structured_data.get("compensation", {})
        benefits = compensation.get("benefits", [])

        # Delete existing benefits for this job
        self.db_manager.execute_query("DELETE FROM job_benefits WHERE job_id = %s", (job_id,))

        # Insert new benefits
        for benefit in benefits:
            if benefit:  # Skip empty benefits
                insert_query = """
                    INSERT INTO job_benefits (job_id, benefit_name, created_at)
                    VALUES (%s, %s, %s)
                """
                self.db_manager.execute_query(insert_query, (job_id, benefit, datetime.now()))
                count += 1

        return count

    def _save_required_documents(self, result: Dict) -> int:
        """Save required documents to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        structured_data = result.get("structured_data", {})
        application_details = structured_data.get("application_details", {})
        required_documents = application_details.get("required_documents", [])

        # Delete existing documents for this job
        self.db_manager.execute_query("DELETE FROM job_required_documents WHERE job_id = %s", (job_id,))

        # Insert new required documents
        for doc_type in required_documents:
            if doc_type:  # Skip empty document types
                insert_query = """
                    INSERT INTO job_required_documents (job_id, document_type, is_required, created_at)
                    VALUES (%s, %s, %s, %s)
                """
                self.db_manager.execute_query(insert_query, (job_id, doc_type, True, datetime.now()))
                count += 1

        return count

    def _save_stress_indicators(self, result: Dict) -> int:
        """Save stress indicators to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        stress_analysis = result.get("stress_level_analysis", {})
        stress_indicators = stress_analysis.get("stress_indicators", [])

        # Delete existing stress indicators for this job
        self.db_manager.execute_query("DELETE FROM job_stress_indicators WHERE job_id = %s", (job_id,))

        # Insert new stress indicators
        for indicator in stress_indicators:
            if indicator:  # Skip empty indicators
                insert_query = """
                    INSERT INTO job_stress_indicators (job_id, indicator, created_at)
                    VALUES (%s, %s, %s)
                """
                self.db_manager.execute_query(insert_query, (job_id, indicator, datetime.now()))
                count += 1

        return count

    def _save_certifications(self, result: Dict) -> int:
        """Save certifications to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        structured_data = result.get("structured_data", {})
        skill_requirements = structured_data.get("skill_requirements", {})
        certifications = skill_requirements.get("certifications", [])

        # Delete existing certifications for this job
        self.db_manager.execute_query("DELETE FROM job_certifications WHERE job_id = %s", (job_id,))

        # Insert new certifications
        for cert in certifications:
            if cert:  # Skip empty certifications
                insert_query = """
                    INSERT INTO job_certifications (job_id, certification_name, is_required, created_at)
                    VALUES (%s, %s, %s, %s)
                """
                self.db_manager.execute_query(insert_query, (job_id, cert, True, datetime.now()))
                count += 1

        return count

    def _save_ats_keywords(self, result: Dict) -> int:
        """Save ATS keywords to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        structured_data = result.get("structured_data", {})
        ats_optimization = structured_data.get("ats_optimization", {})

        # Delete existing ATS keywords for this job
        self.db_manager.execute_query("DELETE FROM job_ats_keywords WHERE job_id = %s", (job_id,))

        # Save primary keywords
        primary_keywords = ats_optimization.get("primary_keywords", [])
        for keyword in primary_keywords:
            if keyword:
                insert_query = """
                    INSERT INTO job_ats_keywords (job_id, keyword_type, keyword, created_at)
                    VALUES (%s, %s, %s, %s)
                """
                self.db_manager.execute_query(insert_query, (job_id, "primary", keyword, datetime.now()))
                count += 1

        # Save industry keywords
        industry_keywords = ats_optimization.get("industry_keywords", [])
        for keyword in industry_keywords:
            if keyword:
                insert_query = """
                    INSERT INTO job_ats_keywords (job_id, keyword_type, keyword, created_at)
                    VALUES (%s, %s, %s, %s)
                """
                self.db_manager.execute_query(insert_query, (job_id, "industry", keyword, datetime.now()))
                count += 1

        # Save must-have phrases
        must_have_phrases = ats_optimization.get("must_have_phrases", [])
        for phrase in must_have_phrases:
            if phrase:
                insert_query = """
                    INSERT INTO job_ats_keywords (job_id, keyword_type, keyword, created_at)
                    VALUES (%s, %s, %s, %s)
                """
                self.db_manager.execute_query(insert_query, (job_id, "must_have_phrase", phrase, datetime.now()))
                count += 1

        return count

    def _save_red_flags_details(self, result: Dict) -> int:
        """Save red flag details to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        red_flags = result.get("red_flags", {})

        # Delete existing red flags for this job
        self.db_manager.execute_query("DELETE FROM job_red_flags_details WHERE job_id = %s", (job_id,))

        # Save unrealistic expectations red flag
        unrealistic = red_flags.get("unrealistic_expectations", {})
        if unrealistic:
            insert_query = """
                INSERT INTO job_red_flags_details (job_id, flag_type, detected, details, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db_manager.execute_query(
                insert_query,
                (
                    job_id,
                    "unrealistic_expectations",
                    unrealistic.get("detected", False),
                    unrealistic.get("details", ""),
                    datetime.now(),
                ),
            )
            count += 1

        # Save potential scam indicators red flag
        scam_indicators = red_flags.get("potential_scam_indicators", {})
        if scam_indicators:
            insert_query = """
                INSERT INTO job_red_flags_details (job_id, flag_type, detected, details, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db_manager.execute_query(
                insert_query,
                (
                    job_id,
                    "potential_scam_indicators",
                    scam_indicators.get("detected", False),
                    scam_indicators.get("details", ""),
                    datetime.now(),
                ),
            )
            count += 1

        return count

    def _save_education_requirements(self, result: Dict) -> int:
        """Save education requirements to normalized table"""
        count = 0
        job_id = result.get("job_id")
        if not job_id:
            return count

        structured_data = result.get("structured_data", {})
        skill_requirements = structured_data.get("skill_requirements", {})
        education_requirements = skill_requirements.get("education_requirements", [])

        # Delete existing education requirements for this job
        self.db_manager.execute_query("DELETE FROM job_education_requirements WHERE job_id = %s", (job_id,))

        # Handle both list format (new) and string format (legacy)
        if isinstance(education_requirements, list):
            # New list format
            for edu_req in education_requirements:
                if isinstance(edu_req, dict):
                    insert_query = """
                        INSERT INTO job_education_requirements (
                            job_id, degree_level, field_of_study, institution_type, 
                            years_required, is_required, alternative_experience, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    self.db_manager.execute_query(
                        insert_query,
                        (
                            job_id,
                            edu_req.get("degree_level"),
                            edu_req.get("field_of_study"),
                            edu_req.get("institution_type"),
                            edu_req.get("years_required"),
                            edu_req.get("is_required", True),
                            edu_req.get("alternative_experience"),
                            datetime.now(),
                        ),
                    )
                    count += 1
        elif isinstance(education_requirements, str) and education_requirements:
            # Legacy string format - create a single requirement record
            insert_query = """
                INSERT INTO job_education_requirements (
                    job_id, degree_level, field_of_study, is_required, alternative_experience, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.db_manager.execute_query(
                insert_query, (job_id, "Not specified", education_requirements, True, None, datetime.now())
            )
            count += 1

        return count
