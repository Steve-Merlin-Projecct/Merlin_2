"""
Content Library Management System
Handles sentence banks, content selection, and application package generation
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import text
from ..database.database_client import DatabaseClient
from .tone_analyzer import ToneAnalyzer


class ContentManager:
    """
    Manages content libraries and generates application packages
    """

    def __init__(self):
        self.db_client = DatabaseClient()
        self.tone_analyzer = ToneAnalyzer()
        self.logger = logging.getLogger(__name__)

    def seed_content_library(self):
        """
        Seed the content library with initial approved sentences
        """
        # Resume content based on Steve Glen's background
        resume_content = [
            {
                "text": "Led comprehensive rebranding initiative for 14-year-old media company, modernizing visual identity and messaging strategy",
                "category": "Leadership",
                "tone": "Confident",
                "tone_strength": 0.9,
                "tags": ["leadership", "branding", "strategy", "media"],
                "matches_job_attributes": ["Brand Management", "Strategic Planning", "Team Leadership"],
                "length": "Long",
                "stage": "Approved",
                "position_label": "Marketing Manager",
                "sentence_strength": 9,
                "intended_document": "resume",
            },
            {
                "text": "Managed editorial calendar and content distribution across multiple digital platforms, increasing engagement 35%",
                "category": "Achievement",
                "tone": "Analytical",
                "tone_strength": 0.8,
                "tags": ["content", "digital", "analytics", "engagement"],
                "matches_job_attributes": ["Content Marketing", "Digital Marketing", "Analytics"],
                "length": "Medium",
                "stage": "Approved",
                "position_label": "Marketing Manager",
                "sentence_strength": 8,
                "intended_document": "resume",
            },
            {
                "text": "Developed data-driven marketing strategies using Google Analytics and custom reporting tools",
                "category": "Technical",
                "tone": "Analytical",
                "tone_strength": 0.85,
                "tags": ["analytics", "data-driven", "google analytics", "reporting"],
                "matches_job_skill": "Analytics",
                "length": "Medium",
                "stage": "Approved",
                "position_label": "Marketing Manager",
                "sentence_strength": 8,
                "intended_document": "resume",
            },
            {
                "text": "Collaborated with cross-functional teams including sales, design, and editorial to align marketing initiatives",
                "category": "Collaboration",
                "tone": "Warm",
                "tone_strength": 0.7,
                "tags": ["collaboration", "cross-functional", "teamwork"],
                "matches_job_skill": "Team Collaboration",
                "length": "Medium",
                "stage": "Approved",
                "position_label": "Marketing Manager",
                "sentence_strength": 7,
                "intended_document": "resume",
            },
        ]

        # Cover letter content
        cover_letter_content = [
            {
                "text": "Your company's innovative approach to digital transformation immediately caught my attention",
                "category": "Opening",
                "tone": "Curious",
                "tone_strength": 0.8,
                "tags": ["company_research", "digital", "innovation"],
                "matches_job_skill": "Digital Marketing",
                "length": "Medium",
                "stage": "Approved",
                "position_label": "All",
                "sentence_strength": 8,
                "intended_document": "cover_letter",
            },
            {
                "text": "I bring 14+ years of experience building marketing strategies that bridge creativity and data analysis",
                "category": "Alignment",
                "tone": "Confident",
                "tone_strength": 0.9,
                "tags": ["experience", "strategy", "creativity", "analytics"],
                "matches_job_skill": "Marketing Strategy",
                "length": "Medium",
                "stage": "Approved",
                "position_label": "Marketing Manager",
                "sentence_strength": 9,
                "intended_document": "cover_letter",
            },
            {
                "text": "At Odvod Media, I transformed our content marketing approach, resulting in a 40% increase in qualified leads",
                "category": "Achievement",
                "tone": "Analytical",
                "tone_strength": 0.85,
                "tags": ["content marketing", "transformation", "lead generation", "metrics"],
                "matches_job_skill": "Content Marketing",
                "length": "Long",
                "stage": "Approved",
                "position_label": "Marketing Manager",
                "sentence_strength": 9,
                "intended_document": "cover_letter",
            },
            {
                "text": "I'm excited about the opportunity to contribute to your team's continued success",
                "category": "Closing",
                "tone": "Warm",
                "tone_strength": 0.7,
                "tags": ["enthusiasm", "team", "contribution"],
                "matches_job_skill": "All",
                "length": "Short",
                "stage": "Approved",
                "position_label": "All",
                "sentence_strength": 7,
                "intended_document": "cover_letter",
            },
        ]

        # Store resume content
        with self.db_client.get_session() as session:
            for content in resume_content:
                session.execute(
                    text(
                        """
                    INSERT INTO sentence_bank_resume (
                        text, category, tone, tone_strength, 
                        length, stage, position_label, sentence_strength, matches_job_skill
                    ) VALUES (:text, :category, :tone, :tone_strength, 
                             :length, :stage, :position_label, :sentence_strength, :matches_job_skill)
                    """
                    ),
                    {
                        "text": content["text"],
                        "category": content["category"],
                        "tone": content["tone"],
                        "tone_strength": content["tone_strength"],
                        "length": content["length"],
                        "stage": content["stage"],
                        "position_label": content["position_label"],
                        "sentence_strength": content["sentence_strength"],
                        "matches_job_skill": content.get("matches_job_skill"),
                    },
                )

            # Store cover letter content
            for content in cover_letter_content:
                session.execute(
                    text(
                        """
                    INSERT INTO sentence_bank_cover_letter (
                        text, category, tone, tone_strength, tags,
                        length, stage, position_label, sentence_strength
                    ) VALUES (:text, :category, :tone, :tone_strength, :tags,
                             :length, :stage, :position_label, :sentence_strength)
                    """
                    ),
                    {
                        "text": content["text"],
                        "category": content["category"],
                        "tone": content["tone"],
                        "tone_strength": content["tone_strength"],
                        "tags": content.get("tags", []),
                        "length": content["length"],
                        "stage": content["stage"],
                        "position_label": content["position_label"],
                        "sentence_strength": content["sentence_strength"],
                    },
                )

        logging.info("Content library seeded with approved sentences")

    def select_content_for_job(self, job_data: Dict) -> Dict:
        """
        Select optimal content for a specific job using AI-analyzed skills and ATS keywords
        """
        job_id = job_data.get("id") or job_data.get("job_id")
        if not job_id:
            raise ValueError("Job ID is required for content selection")

        # Get AI-analyzed skills and keywords from database
        job_skills = self._get_job_skills(job_id)
        job_keywords = self._get_job_ats_keywords(job_id)

        # Get matching resume content
        resume_content = self._select_resume_content(job_skills, job_keywords)

        # Get matching cover letter content
        job_data_with_analysis = {**job_data, "skills_required": job_skills, "keywords": job_keywords}
        cover_letter_content = self._select_cover_letter_content(job_data_with_analysis)

        return {"resume": resume_content, "cover_letter": cover_letter_content}

    def _select_resume_content(self, job_skills: List[str], job_keywords: Optional[List[str]] = None) -> List[Dict]:
        """
        Select resume sentences based on job requirements using skill matching and keyword matching
        """
        if job_keywords is None:
            job_keywords = []

        with self.db_client.get_session() as session:
            # Get all approved resume content
            result = session.execute(
                text(
                    """
                SELECT * FROM sentence_bank_resume 
                WHERE stage = 'Approved'
                """
                )
            ).fetchall()

            sentences = [dict(row._mapping) for row in result]

        # Score and select sentences using new algorithm
        scored_sentences = []
        for sentence in sentences:
            score = self._calculate_composite_score(sentence, job_skills, job_keywords)
            scored_sentences.append((sentence, score))

        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        selected = [sentence for sentence, score in scored_sentences[:6]]  # Top 6 for resume

        return selected

    def _select_cover_letter_content(self, job_data: Dict) -> List[Dict]:
        """
        Select cover letter sentences based on job and company using skill and keyword matching
        Prevents duplicate variable usage: max 1 {job_title} and max 1 {company_name} in final output
        """
        job_skills = job_data.get("skills_required", [])
        job_keywords = job_data.get("keywords", [])

        with self.db_client.get_session() as session:
            result = session.execute(
                text(
                    """
                SELECT * FROM sentence_bank_cover_letter 
                WHERE stage = 'Approved'
                """
                )
            ).fetchall()

            sentences = [dict(row._mapping) for row in result]

        # Select sentences by category to ensure complete cover letter
        categories_needed = ["Opening", "Alignment", "Achievement", "Closing"]
        selected_sentences = []
        
        # Track variable usage to prevent duplicates
        variables_used = {
            "job_title": False,
            "company_name": False
        }

        for category in categories_needed:
            category_sentences = [s for s in sentences if s["category"] == category]
            if category_sentences:
                # Find best sentence that doesn't violate variable repetition rules
                best_sentence = self._select_best_sentence_with_variable_constraints(
                    category_sentences, job_skills, job_keywords, variables_used
                )
                if best_sentence:
                    selected_sentences.append(best_sentence)
                    
                    # Update variable usage tracking
                    sentence_text = best_sentence.get("text", "")
                    if "{job_title}" in sentence_text:
                        variables_used["job_title"] = True
                    if "{company_name}" in sentence_text:
                        variables_used["company_name"] = True

        return selected_sentences

    def _calculate_composite_score(self, sentence: Dict, job_skills: List[str], job_keywords: List[str]) -> float:
        """
        Calculate composite score based on skill matching and keyword matching
        Algorithm based on Natural Language Algorithm for Resume and Cover Letter Content Optimization
        """
        # Configuration weights (can be moved to config file later)
        skill_weight = 0.7
        keyword_weight = 0.3

        # Calculate skill matching score
        skill_score = self._calculate_skill_match_score(sentence, job_skills)

        # Calculate keyword matching score
        keyword_score = self._calculate_keyword_match_score(sentence, job_keywords)

        # Normalize scores to 0-1 scale
        normalized_skill_score = min(skill_score, 1.0)
        normalized_keyword_score = min(keyword_score, 1.0)

        # Calculate composite score
        composite_score = (normalized_skill_score * skill_weight) + (normalized_keyword_score * keyword_weight)

        return composite_score

    def _calculate_skill_match_score(self, sentence: Dict, job_skills: List[str]) -> float:
        """
        Calculate skill matching score based on sentence tags and job skills
        """
        if not job_skills:
            return 0.0

        sentence_tags = sentence.get("tags", [])
        if not sentence_tags:
            return 0.0

        # Convert to lowercase for case-insensitive matching
        job_skills_lower = [skill.lower() for skill in job_skills]
        sentence_tags_lower = [tag.lower() for tag in sentence_tags]

        # Count exact matches
        skill_matches = len(set(job_skills_lower).intersection(set(sentence_tags_lower)))

        # Calculate score as ratio of matches to total job skills
        skill_score = skill_matches / len(job_skills)

        return skill_score

    def _calculate_keyword_match_score(self, sentence: Dict, job_keywords: List[str]) -> float:
        """
        Calculate keyword matching score based on sentence text and job keywords
        Ignores variable placeholders during keyword matching for accurate scoring
        """
        if not job_keywords:
            return 0.0

        sentence_text = sentence.get("text", "").lower()
        if not sentence_text:
            return 0.0

        # Remove variable placeholders from text for more accurate keyword matching
        # This prevents variables like {job_title} from interfering with keyword matching
        processed_text = self._strip_variables_for_keyword_matching(sentence_text)

        # Count keyword occurrences in processed sentence text
        keyword_matches = 0
        for keyword in job_keywords:
            if keyword.lower() in processed_text:
                keyword_matches += 1

        # Calculate score as ratio of matched keywords to total keywords
        keyword_score = keyword_matches / len(job_keywords)

        return keyword_score

    def _strip_variables_for_keyword_matching(self, text: str) -> str:
        """
        Remove variable placeholders from text for keyword matching
        
        Args:
            text: Text that may contain variable placeholders
            
        Returns:
            Text with variable placeholders removed for accurate keyword matching
        """
        import re
        
        # Remove {job_title} and {company_name} placeholders 
        # This prevents literal variable text from interfering with keyword matching
        variable_pattern = re.compile(r'\{(job_title|company_name)\}')
        processed_text = variable_pattern.sub('', text)
        
        # Clean up extra spaces that might result from variable removal
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        return processed_text

    def _select_best_sentence_with_variable_constraints(self, category_sentences: List[Dict], 
                                                       job_skills: List[str], job_keywords: List[str], 
                                                       variables_used: Dict[str, bool]) -> Optional[Dict]:
        """
        Select best sentence from category that doesn't violate variable repetition constraints
        
        Args:
            category_sentences: Sentences in the current category
            job_skills: Job skills for scoring
            job_keywords: Job keywords for scoring  
            variables_used: Dictionary tracking which variables have been used
            
        Returns:
            Best valid sentence or None if no valid sentences available
        """
        # Score all sentences and sort by composite score
        scored_sentences = []
        for sentence in category_sentences:
            score = self._calculate_composite_score(sentence, job_skills, job_keywords)
            scored_sentences.append((sentence, score))
        
        # Sort by score (highest first)
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Find first sentence that doesn't violate variable constraints
        for sentence, score in scored_sentences:
            sentence_text = sentence.get("text", "")
            
            # Check if this sentence would violate variable repetition rules
            violates_constraints = False
            
            if "{job_title}" in sentence_text and variables_used["job_title"]:
                violates_constraints = True
            if "{company_name}" in sentence_text and variables_used["company_name"]:
                violates_constraints = True
                
            # If no violations, this is our best valid sentence
            if not violates_constraints:
                return sentence
        
        # If no valid sentences found, return the highest scoring one anyway
        # (This ensures we always have content for each category)
        if scored_sentences:
            self.logger.warning(f"No sentences available without variable constraint violations. Using highest scoring sentence.")
            return scored_sentences[0][0]
            
        return None

    def _get_job_skills(self, job_id: str) -> List[str]:
        """
        Retrieve AI-analyzed skills from job_skills table
        """
        with self.db_client.get_session() as session:
            result = session.execute(
                text(
                    """
                SELECT skill_name, importance_rating, is_required
                FROM job_skills 
                WHERE job_id = :job_id
                ORDER BY importance_rating DESC NULLS LAST, is_required DESC
            """
                ),
                {"job_id": job_id},
            ).fetchall()

            skills = [row[0] for row in result]  # Extract skill names
            self.logger.debug(f"Retrieved {len(skills)} skills for job {job_id}")
            return skills

    def _get_job_ats_keywords(self, job_id: str) -> List[str]:
        """
        Retrieve AI-analyzed ATS keywords from job_ats_keywords table
        Includes primary_keywords, industry_keywords, and must_have_phrases
        """
        with self.db_client.get_session() as session:
            result = session.execute(
                text(
                    """
                SELECT keyword, keyword_category, frequency_in_posting
                FROM job_ats_keywords 
                WHERE job_id = :job_id
                ORDER BY 
                    CASE keyword_category 
                        WHEN 'primary_keywords' THEN 1
                        WHEN 'must_have_phrases' THEN 2  
                        WHEN 'industry_keywords' THEN 3
                        ELSE 4
                    END,
                    frequency_in_posting DESC NULLS LAST
            """
                ),
                {"job_id": job_id},
            ).fetchall()

            keywords = [row[0] for row in result]  # Extract keyword text
            self.logger.debug(f"Retrieved {len(keywords)} ATS keywords for job {job_id}")
            return keywords

    def generate_application_package(self, job_id: str) -> Dict:
        """
        Generate complete application package for a job
        """
        # Get job data
        with self.db_client.get_session() as session:
            result = session.execute(
                text(
                    """
                SELECT j.*, c.name as company_name 
                FROM jobs j 
                LEFT JOIN companies c ON j.company_id = c.id 
                WHERE j.id = :job_id
                """
                ),
                {"job_id": job_id},
            ).fetchone()

            if not result:
                raise ValueError(f"Job {job_id} not found")

            job_data = dict(result._mapping)

        # Select content
        selected_content = self.select_content_for_job(job_data)

        # Generate documents with tone analysis
        resume_sentences = selected_content["resume"]
        cover_letter_sentences = selected_content["cover_letter"]

        # Analyze tone coherence
        resume_analysis = self.tone_analyzer.analyze_document_tone(resume_sentences)
        cover_letter_analysis = self.tone_analyzer.analyze_document_tone(cover_letter_sentences)

        # Generate email content
        email_content = self._generate_email_content(job_data)

        # Create application record
        application_id = self._create_application_record(job_id, resume_analysis, cover_letter_analysis)

        return {
            "job_id": job_id,
            "application_id": application_id,
            "job_data": job_data,
            "resume": {"sentences": resume_sentences, "tone_analysis": resume_analysis},
            "cover_letter": {"sentences": cover_letter_sentences, "tone_analysis": cover_letter_analysis},
            "email": email_content,
        }

    def _generate_email_content(self, job_data: Dict) -> Dict:
        """
        Generate email subject and body for application
        """
        company_name = job_data.get("company_name", "Company")
        job_title = job_data.get("job_title", "Position")

        subject = f"Application for {job_title} Position"

        body = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With over 14 years of experience in marketing and communications, I am confident that my skills and background make me an ideal candidate for this role.

Please find my resume and cover letter attached for your review. I would welcome the opportunity to discuss how my experience can contribute to your team's success.

Thank you for your consideration. I look forward to hearing from you.

Best regards,
Steve Glen

Contact Information:
Email: therealstevenglen@gmail.com
Phone: 780-884-7038
LinkedIn: https://linkedin.com/in/steveglen
Portfolio: https://steveglen.com
"""

        return {"subject": subject, "body": body, "to_email": self._extract_email_from_job(job_data)}

    def _extract_email_from_job(self, job_data: Dict) -> str:
        """
        Extract or infer email address for application
        """
        # In a real system, this would use the LLM analysis
        company_name = job_data.get("company_name", "").lower().replace(" ", "").replace("inc", "").replace("ltd", "")
        return f"careers@{company_name}.com"

    def _create_application_record(self, job_id: str, resume_analysis: Dict, cover_letter_analysis: Dict) -> str:
        """
        Create application record in database
        """
        import uuid

        application_id = str(uuid.uuid4())

        with self.db_client.get_session() as session:
            session.execute(
                text(
                    """
                INSERT INTO job_applications (
                    id, job_id, application_method, application_status,
                    tone_jump_score, tone_coherence_score, total_tone_travel
                ) VALUES (:id, :job_id, :application_method, :application_status,
                         :tone_jump_score, :tone_coherence_score, :total_tone_travel)
                """
                ),
                {
                    "id": application_id,
                    "job_id": job_id,
                    "application_method": "email",
                    "application_status": "prepared",
                    "tone_jump_score": (
                        resume_analysis["average_tone_jump"] + cover_letter_analysis["average_tone_jump"]
                    )
                    / 2,
                    "tone_coherence_score": (
                        resume_analysis["tone_coherence_score"] + cover_letter_analysis["tone_coherence_score"]
                    )
                    / 2,
                    "total_tone_travel": resume_analysis["total_tone_travel"]
                    + cover_letter_analysis["total_tone_travel"],
                },
            )

        return application_id
