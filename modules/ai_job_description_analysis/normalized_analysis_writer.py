"""
Normalized Analysis Writer - Store AI analysis results in normalized database tables
Used by BatchAIAnalyzer to store job analysis results in proper relational format

This module handles the storage of AI analysis results from Google Gemini into
the normalized database schema with proper foreign key relationships and data integrity.

Author: Automated Job Application System v2.16
Date: July 24, 2025
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class NormalizedAnalysisWriter:
    """
    Handles storage of AI analysis results in normalized database tables

    This class takes the JSON analysis results from Google Gemini AI and
    stores them across multiple normalized tables maintaining referential integrity.
    """

    def __init__(self):
        """Initialize the writer with database connection"""
        self.db = DatabaseManager()
        logger.info("NormalizedAnalysisWriter initialized")

    def save_analysis_results(self, job_id: UUID, analysis_data: Dict) -> Dict:
        """
        Save AI analysis results to normalized database tables

        Args:
            job_id: UUID of the job being analyzed
            analysis_data: Dictionary containing AI analysis results

        Returns:
            Dict: Save operation statistics
        """
        try:
            logger.info(f"Saving analysis results for job {job_id}")

            # Start with main job_analysis record
            analysis_id = self._save_main_analysis(job_id, analysis_data)

            # Save related data to normalized tables
            stats = {
                "analysis_id": analysis_id,
                "skills_saved": 0,
                "industries_saved": 0,
                "keywords_saved": 0,
                "requirements_saved": 0,
                "insights_saved": 0,
                "red_flags_saved": 0,
            }

            # Save skills analysis if present
            if "skills" in analysis_data:
                stats["skills_saved"] = self._save_skills_analysis(job_id, analysis_data["skills"])

            # Save secondary industries if present
            if "secondary_industries" in analysis_data:
                stats["industries_saved"] = self._save_secondary_industries(
                    analysis_id, analysis_data["secondary_industries"]
                )

            # Save ATS keywords if present in structured_data
            structured_data = analysis_data.get("structured_data", {})
            if "ats_optimization" in structured_data:
                ats_data = structured_data["ats_optimization"]
                if "keywords" in ats_data:
                    stats["keywords_saved"] = self._save_ats_keywords(job_id, ats_data["keywords"])

            # Save implicit requirements if present
            if "implicit_requirements" in analysis_data:
                stats["requirements_saved"] = self._save_implicit_requirements(
                    analysis_id, analysis_data["implicit_requirements"]
                )

            # Save cover letter insights if present
            if "cover_letter_insights" in analysis_data:
                stats["insights_saved"] = self._save_cover_letter_insights(
                    analysis_id, analysis_data["cover_letter_insights"]
                )

            # Save red flags if present
            if "red_flags" in analysis_data:
                stats["red_flags_saved"] = self._save_red_flags(analysis_id, analysis_data["red_flags"])

            logger.info(f"Successfully saved analysis results for job {job_id}: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to save analysis results for job {job_id}: {e}")
            raise

    def _save_main_analysis(self, job_id: UUID, analysis_data: Dict) -> UUID:
        """Save main job analysis record"""
        analysis_id = uuid4()

        # Extract main analysis fields with safe defaults
        query = """
            INSERT INTO analyzed_jobs (
                id, job_id, primary_industry, seniority_level, 
                authenticity_score, hiring_manager, department, 
                reporting_to, job_title_extracted, company_name_extracted,
                created_at, additional_insights
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        # Extract primary industry (default to 'Unknown' if not found)
        primary_industry = analysis_data.get("primary_industry", "Unknown")

        # Extract seniority level (default to 'Mid-Level' if not found)
        seniority_level = analysis_data.get("seniority_level", "Mid-Level")

        # Extract authenticity score (default to 0.5 if not found)
        authenticity_score = analysis_data.get("authenticity_score", 0.5)

        # Extract structured data fields for hiring organization information
        structured_data = analysis_data.get("structured_data", {})
        hiring_manager = structured_data.get("hiring_manager")
        department = structured_data.get("department") 
        reporting_to = structured_data.get("reporting_to")
        job_title_extracted = structured_data.get("job_title")
        company_name_extracted = structured_data.get("company_name")

        # Store remaining analysis data as JSON in additional_insights
        # Include secondary_industries, implicit_requirements, cover_letter_insights, red_flags
        # since their dedicated tables don't exist
        additional_insights = {
            k: v
            for k, v in analysis_data.items()
            if k
            not in [
                "primary_industry",
                "seniority_level",
                "authenticity_score",
                "skills",
                "structured_data",
            ]
        }

        import json

        params = (
            analysis_id,
            job_id,
            primary_industry,
            seniority_level,
            authenticity_score,
            hiring_manager,
            department,
            reporting_to,
            job_title_extracted,
            company_name_extracted,
            datetime.now(),
            json.dumps(additional_insights) if additional_insights else None,
        )

        result = self.db.execute_query(query, params)
        logger.info(f"Saved main analysis record with ID {analysis_id}")

        return analysis_id

    def _save_skills_analysis(self, job_id: UUID, skills_data: List[Dict]) -> int:
        """Save skills analysis to job_skills table"""
        if not skills_data:
            return 0

        skills_saved = 0

        for skill in skills_data:
            try:
                query = """
                    INSERT INTO job_skills (
                        job_id, skill_name, importance_rating, reasoning, is_required
                    ) VALUES (%s, %s, %s, %s, %s)
                """

                params = (
                    job_id,
                    skill.get("name", "Unknown Skill"),
                    skill.get("importance", 5),  # Default to medium importance
                    skill.get("reasoning", "No reasoning provided"),
                    skill.get("required", False),  # Map to is_required column
                )

                self.db.execute_query(query, params)
                skills_saved += 1

            except Exception as e:
                logger.error(f"Failed to save skill {skill}: {e}")
                continue

        logger.info(f"Saved {skills_saved} skills for job {job_id}")
        return skills_saved

    def _save_secondary_industries(self, analysis_id: UUID, industries_data: List[str]) -> int:
        """Secondary industries data stored in analyzed_jobs.additional_insights (table does not exist)"""
        if not industries_data:
            return 0
        
        logger.info(f"Secondary industries data for analysis {analysis_id} stored in additional_insights JSON field")
        return len(industries_data)

    def _save_ats_keywords(self, job_id: UUID, keywords_data: List[Dict]) -> int:
        """Save ATS keywords to job_ats_keywords table"""
        if not keywords_data:
            return 0

        keywords_saved = 0

        for keyword in keywords_data:
            try:
                query = """
                    INSERT INTO job_ats_keywords (
                        job_id, keyword, keyword_category, frequency_in_posting
                    ) VALUES (%s, %s, %s, %s)
                """

                # Handle both string and dict formats
                if isinstance(keyword, str):
                    keyword_name = keyword
                    importance = "medium"
                    category = "general"
                else:
                    keyword_name = keyword.get("keyword", keyword.get("name", "Unknown"))
                    importance = keyword.get("importance", "medium")
                    category = keyword.get("category", "general")

                # Map importance level to frequency (high=3, medium=2, low=1)
                frequency = {"high": 3, "medium": 2, "low": 1}.get(importance.lower(), 2)

                params = (job_id, keyword_name, category, frequency)
                self.db.execute_query(query, params)
                keywords_saved += 1

            except Exception as e:
                logger.error(f"Failed to save ATS keyword {keyword}: {e}")
                continue

        logger.info(f"Saved {keywords_saved} ATS keywords for job {job_id}")
        return keywords_saved

    def _save_implicit_requirements(self, analysis_id: UUID, requirements_data: List[Dict]) -> int:
        """Implicit requirements data stored in analyzed_jobs.additional_insights (table does not exist)"""
        if not requirements_data:
            return 0
        
        logger.info(f"Implicit requirements data for analysis {analysis_id} stored in additional_insights JSON field")
        return len(requirements_data)

    def _save_cover_letter_insights(self, analysis_id: UUID, insights_data: Dict) -> int:
        """Cover letter insights data stored in analyzed_jobs.additional_insights (table does not exist)"""
        if not insights_data:
            return 0
        
        logger.info(f"Cover letter insights data for analysis {analysis_id} stored in additional_insights JSON field")
        return 1

    def _save_red_flags(self, analysis_id: UUID, red_flags_data: List[Dict]) -> int:
        """Red flags data stored in analyzed_jobs.additional_insights (table does not exist)"""
        if not red_flags_data:
            return 0
        
        logger.info(f"Red flags data for analysis {analysis_id} stored in additional_insights JSON field")
        return len(red_flags_data)
