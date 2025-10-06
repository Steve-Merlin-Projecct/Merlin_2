"""
LLM Job Analysis System
Simulates OpenAI/Anthropic integration for job analysis
"""

import json
import logging
from typing import Dict, List, Optional
from ..database.database_client import DatabaseClient


class LLMJobAnalyzer:
    """
    Analyzes job postings using LLM to extract skills, classify roles, and determine application methods
    """

    def __init__(self):
        self.db_client = DatabaseClient()

    def simulate_llm_job_analysis(self, job_data: Dict) -> Dict:
        """
        Simulate LLM analysis of job posting
        In production, this would call OpenAI/Anthropic API
        """
        job_title = job_data.get("job_title", "").lower()
        job_description = job_data.get("job_description", "").lower()

        # Simulate intelligent analysis based on job content
        analysis = {
            "required_skills": [],
            "nice_to_have_skills": [],
            "experience_level": "mid",
            "industry": "technology",
            "remote_friendly": True,
            "salary_assessment": "market_rate",
            "application_method": "email",
            "culture_indicators": [],
            "career_path": "marketing",
            "priority_score": 0.0,
        }

        # Analyze job title and description for skills
        if "senior" in job_title or "5+" in job_description:
            analysis["experience_level"] = "senior"
        elif "junior" in job_title or "1-2" in job_description:
            analysis["experience_level"] = "junior"

        # Extract skills based on content
        skill_keywords = {
            "digital marketing": ["digital marketing", "online marketing", "digital campaigns"],
            "analytics": ["analytics", "google analytics", "data analysis", "metrics", "kpi"],
            "content creation": ["content", "writing", "copywriting", "editorial"],
            "social media": ["social media", "linkedin", "twitter", "facebook"],
            "marketing automation": ["automation", "hubspot", "marketo", "pardot"],
            "project management": ["project management", "coordination", "planning"],
            "leadership": ["leadership", "management", "team", "supervise"],
            "seo": ["seo", "search engine", "organic"],
            "sem": ["sem", "google ads", "ppc", "paid search"],
            "email marketing": ["email marketing", "email campaigns", "newsletter"],
            "crm": ["crm", "salesforce", "customer relationship"],
            "design": ["design", "creative", "adobe", "photoshop", "canva"],
            "strategy": ["strategy", "strategic", "planning", "growth"],
            "b2b": ["b2b", "business to business", "enterprise"],
            "saas": ["saas", "software as a service", "subscription"],
        }

        for skill, keywords in skill_keywords.items():
            if any(keyword in job_description for keyword in keywords):
                if any(keyword in job_description for keyword in ["required", "must", "essential"]):
                    analysis["required_skills"].append(skill)
                else:
                    analysis["nice_to_have_skills"].append(skill)

        # Determine industry
        if any(word in job_description for word in ["saas", "software", "technology", "tech"]):
            analysis["industry"] = "technology"
        elif any(word in job_description for word in ["media", "publishing", "journalism"]):
            analysis["industry"] = "media"
        elif any(word in job_description for word in ["healthcare", "medical", "health"]):
            analysis["industry"] = "healthcare"

        # Check remote options
        if any(word in job_description for word in ["remote", "work from home", "distributed"]):
            analysis["remote_friendly"] = True
        elif any(word in job_description for word in ["on-site", "office", "in-person"]):
            analysis["remote_friendly"] = False

        # Determine career path
        if "product" in job_title.lower():
            analysis["career_path"] = "product_marketing"
        elif "digital" in job_title.lower():
            analysis["career_path"] = "digital_marketing"
        elif any(word in job_title.lower() for word in ["communication", "content"]):
            analysis["career_path"] = "marketing_communications"
        else:
            analysis["career_path"] = "marketing_general"

        # Calculate priority score (0-1)
        score_factors = {
            "senior_level": 0.8 if analysis["experience_level"] == "senior" else 0.6,
            "remote_friendly": 0.3 if analysis["remote_friendly"] else 0.0,
            "skill_match": len(analysis["required_skills"]) * 0.1,
            "industry_match": 0.2 if analysis["industry"] == "technology" else 0.1,
        }
        analysis["priority_score"] = min(1.0, sum(score_factors.values()))

        # Culture indicators
        if "startup" in job_description:
            analysis["culture_indicators"].append("startup")
        if "fast-paced" in job_description:
            analysis["culture_indicators"].append("fast_paced")
        if "collaborative" in job_description:
            analysis["culture_indicators"].append("collaborative")
        if "innovative" in job_description:
            analysis["culture_indicators"].append("innovative")

        return analysis

    def analyze_and_update_job(self, job_id: str) -> Dict:
        """
        Analyze job and update database with results
        """
        # Get job data
        with self.db_client.get_session() as session:
            result = session.execute(
                """
                SELECT j.*, c.name as company_name, c.industry as company_industry 
                FROM jobs j 
                LEFT JOIN companies c ON j.company_id = c.id 
                WHERE j.id = %s
            """,
                (job_id,),
            ).fetchone()

            if not result:
                raise ValueError(f"Job {job_id} not found")

            job_data = dict(result._mapping)

        # Perform LLM analysis
        analysis = self.simulate_llm_job_analysis(job_data)

        # Update job record with analysis
        with self.db_client.get_session() as session:
            session.execute(
                """
                UPDATE jobs SET 
                    skills_required = %s,
                    industry = %s,
                    career_path = %s,
                    priority_score = %s,
                    analysis_completed = %s
                WHERE id = %s
            """,
                (
                    analysis["required_skills"],
                    analysis["industry"],
                    analysis["career_path"],
                    analysis["priority_score"],
                    True,
                    job_id,
                ),
            )

        logging.info(
            f"Completed LLM analysis for job {job_id}: {analysis['career_path']} role with {len(analysis['required_skills'])} skills"
        )
        return analysis

    def determine_application_method(self, job_data: Dict) -> tuple[str, Optional[str]]:
        """
        Determine how to apply for this job
        Returns (method, contact_info)
        """
        description = job_data.get("job_description", "").lower()

        # Look for email addresses in job description
        import re

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, job_data.get("job_description", ""))

        if emails:
            return "email", emails[0]

        # Check for application instructions
        if any(phrase in description for phrase in ["send resume", "email resume", "contact"]):
            # Try to infer company email
            company_name = (
                job_data.get("company_name", "").lower().replace(" ", "").replace("inc", "").replace("ltd", "")
            )
            if company_name:
                inferred_email = f"careers@{company_name}.com"
                return "email_inferred", inferred_email

        # Check for easy apply
        if "indeed.com" in job_data.get("primary_source_url", ""):
            return "indeed_easy_apply", job_data.get("primary_source_url")

        return "unavailable", None

    def batch_analyze_jobs(self, job_ids: List[str]) -> Dict[str, Dict]:
        """
        Analyze multiple jobs in batch
        """
        results = {}

        for job_id in job_ids:
            try:
                analysis = self.analyze_and_update_job(job_id)
                results[job_id] = analysis
            except Exception as e:
                logging.error(f"Failed to analyze job {job_id}: {e}")
                results[job_id] = {"error": str(e)}

        logging.info(f"Completed batch analysis of {len(job_ids)} jobs")
        return results
