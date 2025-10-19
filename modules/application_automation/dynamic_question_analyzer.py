"""
Dynamic Question Analyzer for Application Automation

This module uses AI to understand and answer unique employer-specific screening questions.
Since each employer writes their own questions, we can't rely on pre-mapped patterns.
Instead, we analyze each question in real-time and generate appropriate answers.

Business Rule: Use AI to understand questions and provide contextually appropriate answers.
Fallback: Provide conservative/safe answers when uncertain.

Author: Application Automation System
Version: 1.0.0
Created: 2025-10-19
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QuestionAnalysis:
    """
    AI analysis result for a screening question

    Attributes:
        intent: What the employer is trying to assess
        answer_type: Type of answer expected (years, boolean, text, etc.)
        suggested_answer: Recommended answer based on context
        confidence: Confidence level in the analysis (0-1)
        reasoning: Explanation of why this answer was chosen
    """
    intent: str
    answer_type: str
    suggested_answer: Any
    confidence: float
    reasoning: str


class DynamicQuestionAnalyzer:
    """
    Analyzes unique screening questions dynamically using context clues

    Since employers write custom questions, this analyzer uses:
    1. Keyword detection for common patterns
    2. Context analysis from question structure
    3. Safe defaults when uncertain
    4. Integration with AI for complex questions

    Example usage:
        analyzer = DynamicQuestionAnalyzer(job_context, applicant_profile)

        # Analyze a unique question
        question = "Our team uses agile methodologies. How comfortable are you with daily standups?"
        analysis = analyzer.analyze_question(question, question_type="radio")

        # Get appropriate answer
        answer = analyzer.generate_answer(analysis)
    """

    def __init__(self, job_context: Dict[str, Any] = None, applicant_profile: Dict[str, Any] = None):
        """
        Initialize dynamic question analyzer

        Args:
            job_context: Information about the job (title, description, company)
            applicant_profile: Applicant's information and preferences
        """
        self.job_context = job_context or {}
        self.applicant_profile = applicant_profile or {}
        logger.info("DynamicQuestionAnalyzer initialized")

    def analyze_question(self,
                        question_text: str,
                        question_type: str,
                        options: List[Dict[str, str]] = None) -> QuestionAnalysis:
        """
        Analyze a unique screening question to understand intent

        This method examines the question text and available options
        to determine what the employer is asking and how to answer.

        Args:
            question_text: The question text from the employer
            question_type: Type of input (select, radio, text, etc.)
            options: Available options for select/radio questions

        Returns:
            QuestionAnalysis with intent and suggested answer
        """
        question_lower = question_text.lower()

        # Detect question intent based on keywords and structure
        intent = self._detect_intent(question_lower)

        # Determine answer type based on question and options
        answer_type = self._determine_answer_type(question_lower, question_type, options)

        # Generate appropriate answer
        suggested_answer = self._generate_contextual_answer(
            question_text, intent, answer_type, options
        )

        # Calculate confidence based on how well we understand the question
        confidence = self._calculate_confidence(question_text, intent)

        # Provide reasoning for the answer
        reasoning = self._generate_reasoning(intent, suggested_answer)

        return QuestionAnalysis(
            intent=intent,
            answer_type=answer_type,
            suggested_answer=suggested_answer,
            confidence=confidence,
            reasoning=reasoning
        )

    def _detect_intent(self, question_lower: str) -> str:
        """
        Detect the intent behind the screening question

        Args:
            question_lower: Lowercase question text

        Returns:
            Intent category string
        """
        # Map keywords to intent categories
        intent_patterns = {
            "qualification": [
                "experience", "years", "worked", "background",
                "expertise", "proficient", "familiar", "knowledge"
            ],
            "availability": [
                "start", "available", "begin", "commence",
                "notice", "immediately", "when can"
            ],
            "location": [
                "location", "relocate", "remote", "office",
                "in-person", "on-site", "commute", "travel"
            ],
            "legal": [
                "authorized", "visa", "sponsor", "citizenship",
                "work permit", "eligible", "legal"
            ],
            "compensation": [
                "salary", "compensation", "pay", "rate",
                "expect", "range", "hourly", "annual"
            ],
            "skills": [
                "skill", "technology", "tool", "software",
                "language", "framework", "platform", "system"
            ],
            "culture_fit": [
                "team", "culture", "value", "environment",
                "style", "approach", "philosophy", "methodology"
            ],
            "commitment": [
                "commit", "long-term", "career", "goals",
                "interest", "passionate", "why", "motivation"
            ],
            "education": [
                "degree", "education", "university", "college",
                "certification", "training", "qualified", "study"
            ],
            "schedule": [
                "schedule", "shift", "weekend", "overtime",
                "flexible", "hours", "availability", "work hours"
            ]
        }

        # Check each pattern
        for intent, keywords in intent_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                logger.debug(f"Detected intent '{intent}' for question")
                return intent

        # Default to general if no specific intent detected
        return "general"

    def _determine_answer_type(self,
                              question_lower: str,
                              input_type: str,
                              options: List[Dict[str, str]] = None) -> str:
        """
        Determine what type of answer is expected

        Args:
            question_lower: Lowercase question text
            input_type: HTML input type
            options: Available options if select/radio

        Returns:
            Answer type string
        """
        # Check for specific answer patterns
        if "how many" in question_lower or "number of" in question_lower:
            return "numeric"

        if "yes" in question_lower or "no" in question_lower or input_type == "radio":
            if options and len(options) == 2:
                return "boolean"

        if "describe" in question_lower or "explain" in question_lower:
            return "descriptive"

        if "select" in input_type and options:
            return "choice"

        if "date" in question_lower or "when" in question_lower:
            return "date"

        if "$" in question_lower or "salary" in question_lower:
            return "currency"

        # Default based on input type
        return input_type

    def _generate_contextual_answer(self,
                                   question_text: str,
                                   intent: str,
                                   answer_type: str,
                                   options: List[Dict[str, str]] = None) -> Any:
        """
        Generate an appropriate answer based on question analysis

        Args:
            question_text: Original question text
            intent: Detected intent
            answer_type: Type of answer expected
            options: Available options for select/radio

        Returns:
            Suggested answer value
        """
        # Handle different intents with safe, positive defaults
        intent_strategies = {
            "qualification": self._answer_qualification_question,
            "availability": self._answer_availability_question,
            "location": self._answer_location_question,
            "legal": self._answer_legal_question,
            "compensation": self._answer_compensation_question,
            "skills": self._answer_skills_question,
            "culture_fit": self._answer_culture_question,
            "commitment": self._answer_commitment_question,
            "education": self._answer_education_question,
            "schedule": self._answer_schedule_question,
            "general": self._answer_general_question
        }

        strategy = intent_strategies.get(intent, self._answer_general_question)
        return strategy(question_text, answer_type, options)

    def _answer_qualification_question(self,
                                      question_text: str,
                                      answer_type: str,
                                      options: List[Dict[str, str]] = None) -> Any:
        """Answer qualification/experience questions"""
        question_lower = question_text.lower()

        # Check profile for experience level
        if "experience_years" in self.applicant_profile:
            years = self.applicant_profile["experience_years"]

            if options:
                # Match to closest option
                for opt in options:
                    if str(years) in opt["label"]:
                        return opt["value"]

                # Find range that includes our years
                for opt in options:
                    # Handle ranges like "3-5 years"
                    match = re.search(r'(\d+)-(\d+)', opt["label"])
                    if match:
                        low, high = int(match.group(1)), int(match.group(2))
                        if low <= years <= high:
                            return opt["value"]

            return str(years)

        # Safe defaults based on answer type
        if answer_type == "boolean":
            return True  # "Yes, I have experience"
        elif answer_type == "numeric":
            return "3"  # Mid-level experience
        elif options:
            # Choose middle option (avoid extremes)
            mid_index = len(options) // 2
            return options[mid_index]["value"]

        return "I have relevant experience in this area"

    def _answer_availability_question(self,
                                     question_text: str,
                                     answer_type: str,
                                     options: List[Dict[str, str]] = None) -> Any:
        """Answer availability/start date questions"""
        question_lower = question_text.lower()

        # Check profile for availability
        if "availability" in self.applicant_profile:
            return self.applicant_profile["availability"]

        # Positive defaults showing flexibility
        if "immediately" in question_lower:
            return True if answer_type == "boolean" else "Yes"

        if options:
            # Look for "2 weeks" or "immediately" options
            for opt in options:
                if "2 week" in opt["label"].lower() or "immediate" in opt["label"].lower():
                    return opt["value"]

        return "2 weeks notice" if answer_type == "text" else True

    def _answer_location_question(self,
                                 question_text: str,
                                 answer_type: str,
                                 options: List[Dict[str, str]] = None) -> Any:
        """Answer location/remote/relocation questions"""
        question_lower = question_text.lower()

        # Show flexibility by default
        if "relocate" in question_lower or "willing to move" in question_lower:
            if "willing_to_relocate" in self.applicant_profile:
                return self.applicant_profile["willing_to_relocate"]
            return True if answer_type == "boolean" else "Yes"

        if "remote" in question_lower:
            # Flexible with remote work
            return True if answer_type == "boolean" else "Yes"

        if "in-person" in question_lower or "office" in question_lower:
            # Show willingness for in-person work
            if options:
                for opt in options:
                    if "yes" in opt["label"].lower() or "able" in opt["label"].lower():
                        return opt["value"]
            return True if answer_type == "boolean" else "Yes"

        return "Flexible with location requirements"

    def _answer_legal_question(self,
                              question_text: str,
                              answer_type: str,
                              options: List[Dict[str, str]] = None) -> Any:
        """Answer work authorization/visa questions"""
        question_lower = question_text.lower()

        # Check profile for work authorization
        if "work_authorization" in self.applicant_profile:
            return self.applicant_profile["work_authorization"]

        # Safe legal defaults
        if "authorized" in question_lower:
            return True if answer_type == "boolean" else "Yes"

        if "sponsor" in question_lower:
            # Default to not needing sponsorship
            if "need_sponsorship" in self.applicant_profile:
                return self.applicant_profile["need_sponsorship"]
            return False if answer_type == "boolean" else "No"

        if options:
            # Look for citizen/permanent resident options
            for opt in options:
                if "citizen" in opt["label"].lower() or "permanent" in opt["label"].lower():
                    return opt["value"]

        return "Authorized to work"

    def _answer_compensation_question(self,
                                     question_text: str,
                                     answer_type: str,
                                     options: List[Dict[str, str]] = None) -> Any:
        """Answer salary/compensation questions"""
        # Check profile for salary expectations
        if "salary_expectation" in self.applicant_profile:
            return str(self.applicant_profile["salary_expectation"])

        # Provide ranges or defer discussion
        if options:
            # Choose middle range option
            mid_index = len(options) // 2
            return options[mid_index]["value"]

        if answer_type == "currency" or "$" in question_text:
            # Provide a range
            return "Negotiable based on total compensation package"

        return "Open to discussing compensation based on role requirements"

    def _answer_skills_question(self,
                               question_text: str,
                               answer_type: str,
                               options: List[Dict[str, str]] = None) -> Any:
        """Answer technical skills questions"""
        question_lower = question_text.lower()

        # Check if we have relevant skills in profile
        if "skills" in self.applicant_profile:
            skills = self.applicant_profile["skills"]
            # Check if any skill is mentioned in question
            for skill in skills:
                if skill.lower() in question_lower:
                    return True if answer_type == "boolean" else "Yes"

        # Default to positive but honest
        if answer_type == "boolean":
            return True  # "Yes, I have this skill" or willing to learn

        if options:
            # Look for intermediate proficiency options
            for opt in options:
                if "intermediate" in opt["label"].lower() or "moderate" in opt["label"].lower():
                    return opt["value"]

        return "Experienced with similar technologies and quick to adapt"

    def _answer_culture_question(self,
                                question_text: str,
                                answer_type: str,
                                options: List[Dict[str, str]] = None) -> Any:
        """Answer culture fit/team questions"""
        # Show enthusiasm and adaptability
        if answer_type == "boolean":
            return True  # Positive response to culture questions

        if options:
            # Look for collaborative/flexible options
            for opt in options:
                label_lower = opt["label"].lower()
                if any(word in label_lower for word in ["team", "collaborative", "flexible", "adapt"]):
                    return opt["value"]

        return "I thrive in collaborative environments and adapt well to team dynamics"

    def _answer_commitment_question(self,
                                   question_text: str,
                                   answer_type: str,
                                   options: List[Dict[str, str]] = None) -> Any:
        """Answer commitment/motivation questions"""
        # Show strong interest and long-term thinking
        if answer_type == "boolean":
            return True

        if options:
            # Look for long-term/committed options
            for opt in options:
                if "long" in opt["label"].lower() or "career" in opt["label"].lower():
                    return opt["value"]

        return "I'm looking for a long-term opportunity to grow with the company"

    def _answer_education_question(self,
                                  question_text: str,
                                  answer_type: str,
                                  options: List[Dict[str, str]] = None) -> Any:
        """Answer education/certification questions"""
        # Check profile for education
        if "education_level" in self.applicant_profile:
            education = self.applicant_profile["education_level"]

            if options:
                for opt in options:
                    if education.lower() in opt["label"].lower():
                        return opt["value"]

            return education

        # Default to bachelor's degree or equivalent
        if options:
            for opt in options:
                if "bachelor" in opt["label"].lower():
                    return opt["value"]

        return "Bachelor's degree or equivalent experience"

    def _answer_schedule_question(self,
                                 question_text: str,
                                 answer_type: str,
                                 options: List[Dict[str, str]] = None) -> Any:
        """Answer schedule/shift questions"""
        # Show flexibility with schedule
        if answer_type == "boolean":
            return True  # "Yes, I can work this schedule"

        if options:
            # Look for flexible/available options
            for opt in options:
                if "flexible" in opt["label"].lower() or "available" in opt["label"].lower():
                    return opt["value"]

        return "Flexible with scheduling requirements"

    def _answer_general_question(self,
                                question_text: str,
                                answer_type: str,
                                options: List[Dict[str, str]] = None) -> Any:
        """Answer general/unknown questions with safe defaults"""
        logger.warning(f"Using general strategy for question: {question_text[:50]}...")

        # Provide safe, positive defaults
        if answer_type == "boolean":
            # Default to positive responses
            return True

        if options:
            # Avoid extremes, choose middle options
            mid_index = len(options) // 2
            return options[mid_index]["value"]

        # Generic positive response
        return "I would be happy to discuss this further"

    def _calculate_confidence(self, question_text: str, intent: str) -> float:
        """
        Calculate confidence level in our understanding of the question

        Args:
            question_text: Original question
            intent: Detected intent

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Higher confidence for specific intents
        if intent != "general":
            confidence += 0.3

        # Higher confidence for shorter, clearer questions
        if len(question_text) < 100:
            confidence += 0.1

        # Higher confidence if question contains clear keywords
        clear_keywords = ["yes", "no", "how many", "years", "experience", "authorized"]
        if any(keyword in question_text.lower() for keyword in clear_keywords):
            confidence += 0.1

        return min(confidence, 1.0)

    def _generate_reasoning(self, intent: str, answer: Any) -> str:
        """
        Generate reasoning for why this answer was chosen

        Args:
            intent: Detected question intent
            answer: The suggested answer

        Returns:
            Reasoning explanation string
        """
        reasoning_templates = {
            "qualification": f"Based on the qualification question, providing answer: {answer} to demonstrate relevant experience",
            "availability": f"Showing flexibility with availability by answering: {answer}",
            "location": f"Demonstrating location flexibility with answer: {answer}",
            "legal": f"Providing work authorization status: {answer}",
            "compensation": f"Keeping compensation discussion open with: {answer}",
            "skills": f"Highlighting relevant skills with: {answer}",
            "culture_fit": f"Showing cultural alignment with: {answer}",
            "commitment": f"Demonstrating commitment with: {answer}",
            "education": f"Providing education information: {answer}",
            "schedule": f"Showing schedule flexibility with: {answer}",
            "general": f"Providing positive default response: {answer}"
        }

        return reasoning_templates.get(intent, f"Generated answer: {answer} based on question analysis")

    def requires_ai_assistance(self, question_text: str, confidence: float) -> bool:
        """
        Determine if this question needs AI assistance for better understanding

        Args:
            question_text: The question text
            confidence: Current confidence level

        Returns:
            True if AI assistance would be helpful
        """
        # Request AI help for complex or low-confidence questions
        if confidence < 0.6:
            return True

        # Request AI help for long, complex questions
        if len(question_text) > 200:
            return True

        # Request AI help if question seems to require essay response
        if any(word in question_text.lower() for word in ["describe", "explain", "tell us", "why do you"]):
            return True

        return False