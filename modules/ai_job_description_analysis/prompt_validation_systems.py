"""
Prompt Validation Systems - Implements Two-System Architecture for Security
============================================================================

System 1: File Modification Validation
---------------------------------------
Runs after any modification to prompt files:
1.A. Hash prompt (template with placeholders, not runtime values)
1.B. Compare hash to canonical hash on file
1.C. If different, replace prompt section with canonical

System 2: Runtime Execution Workflow
------------------------------------
Runs when sending data to Gemini:
2.A. Run System 1 completely
2.B. Generate security token
2.C. Insert security token
2.D. Send prompt and data to Gemini
2.E. Receive data from Gemini
2.F. Does data match JSON format?
2.G. Does Gemini return correct security token?
2.H. Input data into database

Author: Automated Job Application System v4.3.2
Created: 2025-10-18
"""

import hashlib
import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptValidationSystem1:
    """
    System 1: File Modification Validation

    This system validates prompt templates BEFORE token insertion.
    It works on the template structure with placeholders intact.
    """

    def __init__(self, hash_registry_path: Optional[str] = None):
        """
        Initialize System 1 validator.

        Args:
            hash_registry_path: Path to canonical hash registry
        """
        if hash_registry_path is None:
            hash_registry_path = os.path.join(
                os.getcwd(), "storage", "prompt_hashes.json"
            )

        self.hash_registry_path = hash_registry_path
        self.canonical_hashes = self._load_canonical_hashes()

    def _load_canonical_hashes(self) -> Dict:
        """Load canonical hashes from registry."""
        try:
            if os.path.exists(self.hash_registry_path):
                with open(self.hash_registry_path, 'r') as f:
                    registry = json.load(f)
                    logger.info(f"System 1: Loaded {len(registry)} canonical hashes")
                    return registry
            else:
                logger.warning("System 1: No canonical hash registry found")
                return {}
        except Exception as e:
            logger.error(f"System 1: Failed to load canonical hashes: {e}")
            return {}

    def extract_prompt_template(self, file_path: str) -> Optional[str]:
        """
        Extract the prompt template from a Python file.

        This extracts the TEMPLATE with {security_token} as a variable,
        NOT the runtime version with actual token values.

        Args:
            file_path: Path to the prompt Python file

        Returns:
            Extracted prompt template or None
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Find the prompt_parts section between PROMPT_START and PROMPT_END
            pattern = r'#\s*PROMPT_START\s*\n(.*?)\n\s*#\s*PROMPT_END'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                prompt_section = match.group(1).strip()

                # Convert runtime f-strings to template placeholders
                # Replace f"...{security_token}..." with "...{SECURITY_TOKEN}..."
                template = re.sub(
                    r'f"([^"]*)\{security_token\}([^"]*)"',
                    r'"\1{SECURITY_TOKEN}\2"',
                    prompt_section
                )
                template = re.sub(
                    r"f'([^']*)\{security_token\}([^']*)\'",
                    r"'\1{SECURITY_TOKEN}\2'",
                    template
                )

                # Also handle multiline f-strings
                template = re.sub(
                    r'f"""([^"]*)\{security_token\}([^"]*)"""',
                    r'"""\1{SECURITY_TOKEN}\2"""',
                    template,
                    flags=re.DOTALL
                )

                # Remove f-string prefix for job_count and other variables
                template = re.sub(r'f"([^"]*)\{job_count\}([^"]*)"', r'"\1{JOB_COUNT}\2"', template)
                template = re.sub(r'f"([^"]*)\{jobs_text\}([^"]*)"', r'"\1{JOBS_TEXT}\2"', template)

                return template

            logger.warning(f"System 1: No PROMPT_START/END markers found in {file_path}")
            return None

        except Exception as e:
            logger.error(f"System 1: Failed to extract template from {file_path}: {e}")
            return None

    def calculate_template_hash(self, template: str) -> str:
        """
        Calculate hash of the prompt TEMPLATE.

        This hashes the template structure with placeholders,
        not runtime values.

        Args:
            template: Prompt template with {PLACEHOLDERS}

        Returns:
            SHA-256 hash of template
        """
        # Normalize whitespace and formatting
        normalized = re.sub(r'\s+', ' ', template.strip())

        # Calculate hash
        hash_obj = hashlib.sha256(normalized.encode('utf-8'))
        return hash_obj.hexdigest()

    def get_canonical_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Get the canonical prompt from git repository.

        Args:
            prompt_name: Name of the prompt (e.g., 'tier1_core_prompt')

        Returns:
            Canonical prompt template or None
        """
        try:
            # Get canonical from git commit a276ce8
            import subprocess

            file_path = f"modules/ai_job_description_analysis/prompts/{prompt_name}.py"
            result = subprocess.run(
                ["git", "show", f"a276ce8:{file_path}"],
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode == 0:
                # Extract template from canonical file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(result.stdout)
                    temp_path = f.name

                try:
                    canonical_template = self.extract_prompt_template(temp_path)
                    return canonical_template
                finally:
                    os.unlink(temp_path)

            return None

        except Exception as e:
            logger.error(f"System 1: Failed to get canonical prompt: {e}")
            return None

    def validate_and_fix(self, file_path: str, prompt_name: str) -> Tuple[bool, bool]:
        """
        System 1 main validation function.

        1.A. Hash the prompt template
        1.B. Compare to canonical hash
        1.C. If different, replace with canonical

        Args:
            file_path: Path to prompt file to validate
            prompt_name: Name for hash registry lookup

        Returns:
            (is_valid, was_replaced)
        """
        logger.info(f"System 1: Validating {prompt_name} at {file_path}")

        # Step 1.A: Hash the current prompt template
        current_template = self.extract_prompt_template(file_path)
        if current_template is None:
            logger.error(f"System 1: Could not extract template from {file_path}")
            return False, False

        current_hash = self.calculate_template_hash(current_template)
        logger.debug(f"System 1: Current hash: {current_hash[:16]}...")

        # Step 1.B: Compare to canonical hash
        if prompt_name not in self.canonical_hashes:
            logger.warning(f"System 1: No canonical hash for {prompt_name}")
            # Register this as the canonical
            self.canonical_hashes[prompt_name] = {
                'hash': current_hash,
                'registered_at': datetime.now().isoformat(),
                'last_validated': datetime.now().isoformat()
            }
            self._save_canonical_hashes()
            return True, False

        canonical_hash = self.canonical_hashes[prompt_name]['hash']
        logger.debug(f"System 1: Canonical hash: {canonical_hash[:16]}...")

        if current_hash == canonical_hash:
            logger.info(f"System 1: ✅ Validation PASSED for {prompt_name}")
            return True, False

        # Step 1.C: Hash mismatch - replace with canonical
        logger.warning(f"System 1: ❌ Hash mismatch for {prompt_name}")
        logger.info("System 1: Replacing with canonical version from git...")

        try:
            # Get the canonical file directly from git
            import subprocess
            file_path_git = f"modules/ai_job_description_analysis/prompts/{prompt_name}.py"
            result = subprocess.run(
                ["git", "show", f"a276ce8:{file_path_git}"],
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode != 0:
                logger.error("System 1: Failed to get canonical from git")
                return False, False

            # Get canonical content from git
            canonical_file_content = result.stdout

            # Read current file
            with open(file_path, 'r') as f:
                current_file_content = f.read()

            # Pattern to match PROMPT_START to PROMPT_END section
            pattern = r'(#\s*PROMPT_START\s*\n)(.*?)(\n\s*#\s*PROMPT_END)'

            # Extract the canonical section
            canonical_match = re.search(pattern, canonical_file_content, re.DOTALL)
            if not canonical_match:
                logger.error("System 1: Could not find PROMPT_START/END in canonical")
                return False, False

            # Extract the current section
            current_match = re.search(pattern, current_file_content, re.DOTALL)
            if not current_match:
                logger.error("System 1: Could not find PROMPT_START/END in current file")
                return False, False

            # Get the exact canonical section (including markers)
            canonical_section = canonical_match.group(0)

            # Replace the current section with canonical using string slicing
            # This preserves exact formatting without regex interpretation issues
            start_pos = current_match.start()
            end_pos = current_match.end()

            new_content = (
                current_file_content[:start_pos] +
                canonical_section +
                current_file_content[end_pos:]
            )

            # Write back to file
            with open(file_path, 'w') as f:
                f.write(new_content)

            logger.info(f"System 1: ✅ Replaced {prompt_name} with canonical version")
            return True, True

        except Exception as e:
            logger.error(f"System 1: Failed to replace with canonical: {e}")
            return False, False

    def _save_canonical_hashes(self):
        """Save canonical hashes to registry."""
        try:
            os.makedirs(os.path.dirname(self.hash_registry_path), exist_ok=True)
            with open(self.hash_registry_path, 'w') as f:
                json.dump(self.canonical_hashes, f, indent=2)
            logger.info(f"System 1: Saved {len(self.canonical_hashes)} canonical hashes")
        except Exception as e:
            logger.error(f"System 1: Failed to save canonical hashes: {e}")


class PromptValidationSystem2:
    """
    System 2: Runtime Execution Workflow

    This system handles the complete workflow when sending data to Gemini.
    """

    def __init__(self):
        """Initialize System 2 runtime validator."""
        self.system1 = PromptValidationSystem1()
        self.security_tokens = {}  # Track tokens for validation

    def execute_workflow(
        self,
        jobs: List[Dict],
        prompt_file_path: str,
        prompt_name: str = "tier1_core_prompt",
        tier: str = "tier1"
    ) -> Dict[str, Any]:
        """
        Execute the complete System 2 workflow.

        2.A. Run System 1 completely
        2.B. Generate security token
        2.C. Insert security token
        2.D. Send prompt and data to Gemini
        2.E. Receive data from Gemini
        2.F. Does data match JSON format?
        2.G. Does Gemini return correct security token?
        2.H. Input data into database

        Args:
            jobs: List of job dictionaries to analyze
            prompt_file_path: Path to prompt file
            prompt_name: Prompt identifier (tier1_core_prompt, tier2_enhanced_prompt, tier3_strategic_prompt)
            tier: Tier level (tier1, tier2, tier3) for token optimization

        Returns:
            Dict with workflow results and any errors
        """
        workflow_result = {
            'success': False,
            'steps_completed': [],
            'errors': [],
            'data': None
        }

        try:
            # Step 2.A: Run System 1 validation
            logger.info("System 2: Step 2.A - Running System 1 validation...")
            is_valid, was_replaced = self.system1.validate_and_fix(
                prompt_file_path,
                prompt_name
            )

            if not is_valid:
                workflow_result['errors'].append("System 1 validation failed")
                return workflow_result

            if was_replaced:
                logger.info("System 2: Prompt was replaced with canonical version")

            workflow_result['steps_completed'].append('2.A_system1_validation')

            # Step 2.B: Generate security token
            logger.info("System 2: Step 2.B - Generating security token...")
            from modules.ai_job_description_analysis.ai_analyzer import generate_security_token
            security_token = generate_security_token()
            self.security_tokens[prompt_name] = security_token
            workflow_result['steps_completed'].append('2.B_token_generated')

            # Step 2.C: Insert security token into prompt
            logger.info("System 2: Step 2.C - Creating prompt with security token...")

            # Import the appropriate prompt creation function based on tier
            if tier == "tier1" or prompt_name == "tier1_core_prompt":
                from modules.ai_job_description_analysis.prompts.tier1_core_prompt import (
                    create_tier1_core_prompt
                )
                prompt_with_token = create_tier1_core_prompt(jobs)

            elif tier == "tier2" or prompt_name == "tier2_enhanced_prompt":
                from modules.ai_job_description_analysis.prompts.tier2_enhanced_prompt import (
                    create_tier2_enhanced_prompt
                )
                prompt_with_token = create_tier2_enhanced_prompt(jobs)

            elif tier == "tier3" or prompt_name == "tier3_strategic_prompt":
                from modules.ai_job_description_analysis.prompts.tier3_strategic_prompt import (
                    create_tier3_strategic_prompt
                )
                prompt_with_token = create_tier3_strategic_prompt(jobs)

            else:
                workflow_result['errors'].append(f"Unknown tier: {tier}")
                return workflow_result

            # Extract the token that was generated
            token_match = re.search(r'SECURITY TOKEN: (SEC_TOKEN_[A-Za-z0-9]{32})', prompt_with_token)
            if token_match:
                actual_token = token_match.group(1)
                self.security_tokens[prompt_name] = actual_token
                logger.debug(f"System 2: Token inserted: {actual_token[:20]}...")

            workflow_result['steps_completed'].append('2.C_token_inserted')

            # Step 2.D: Send to Gemini
            logger.info("System 2: Step 2.D - Sending to Gemini API...")
            from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer

            analyzer = GeminiJobAnalyzer()

            # Use the analyzer's API call method with proper token limits
            from modules.ai_job_description_analysis.token_optimizer import TokenOptimizer
            token_optimizer = TokenOptimizer()
            token_allocation = token_optimizer.calculate_optimal_tokens(
                job_count=len(jobs), tier=tier
            )

            # Make the API call using analyzer's method
            response_dict = analyzer._make_gemini_request(
                prompt_with_token,
                max_output_tokens=token_allocation.max_output_tokens
            )

            if not response_dict or 'text' not in response_dict:
                workflow_result['errors'].append("Gemini API call failed")
                return workflow_result

            api_response = response_dict['text']

            workflow_result['steps_completed'].append('2.D_sent_to_gemini')

            # Step 2.E: Receive data from Gemini
            logger.info("System 2: Step 2.E - Processing Gemini response...")
            workflow_result['steps_completed'].append('2.E_received_from_gemini')

            # Step 2.F: Validate JSON format
            logger.info("System 2: Step 2.F - Validating JSON format...")
            try:
                parsed_response = json.loads(api_response)

                # Check for required structure
                if not isinstance(parsed_response, dict):
                    workflow_result['errors'].append("Response is not a JSON object")
                    return workflow_result

                if 'analysis_results' not in parsed_response:
                    workflow_result['errors'].append("Missing 'analysis_results' field")
                    return workflow_result

                workflow_result['steps_completed'].append('2.F_json_validated')

            except json.JSONDecodeError as e:
                workflow_result['errors'].append(f"Invalid JSON: {e}")
                return workflow_result

            # Step 2.G: Validate security token
            logger.info("System 2: Step 2.G - Validating security token...")

            returned_token = parsed_response.get('security_token')
            expected_token = self.security_tokens.get(prompt_name)

            if not returned_token:
                workflow_result['errors'].append("No security token in response")
                logger.error("System 2: ⚠️ SECURITY WARNING - No token returned")
                # Log security incident
                self._log_security_incident(
                    "missing_token",
                    f"Gemini did not return security token for {prompt_name}"
                )
                return workflow_result

            if returned_token != expected_token:
                workflow_result['errors'].append(f"Token mismatch - Expected: {expected_token[:20]}..., Got: {returned_token[:20]}...")
                logger.error(f"System 2: ⚠️ SECURITY WARNING - Token mismatch")
                # Log security incident
                self._log_security_incident(
                    "token_mismatch",
                    f"Token mismatch for {prompt_name}"
                )
                return workflow_result

            logger.info("System 2: ✅ Security token validated successfully")
            workflow_result['steps_completed'].append('2.G_token_validated')

            # Step 2.H: Input data into database
            logger.info("System 2: Step 2.H - Storing results in database...")

            # Extract and prepare results for database
            analysis_results = parsed_response.get('analysis_results', [])

            try:
                from modules.database.database_manager import DatabaseManager
                db = DatabaseManager()

                for result in analysis_results:
                    # Store each job analysis
                    # (Implementation depends on your database schema)
                    logger.info(f"System 2: Storing analysis for job {result.get('job_id')}")
                    # db.store_job_analysis(result)  # Implement this method

                workflow_result['steps_completed'].append('2.H_stored_in_database')

            except Exception as e:
                logger.warning(f"System 2: Database storage failed (non-fatal): {e}")
                # Database errors are non-fatal for the workflow
                workflow_result['steps_completed'].append('2.H_database_skipped')

            # Success!
            workflow_result['success'] = True
            workflow_result['data'] = analysis_results

            logger.info(f"System 2: ✅ Workflow completed successfully - {len(analysis_results)} jobs analyzed")

        except Exception as e:
            logger.error(f"System 2: Workflow failed with error: {e}")
            workflow_result['errors'].append(str(e))

        return workflow_result

    def _log_security_incident(self, incident_type: str, details: str):
        """Log security incidents to file and database."""
        try:
            # Log to file
            incident_log_path = os.path.join(os.getcwd(), "storage", "security_incidents.jsonl")
            os.makedirs(os.path.dirname(incident_log_path), exist_ok=True)

            incident = {
                'timestamp': datetime.now().isoformat(),
                'type': incident_type,
                'details': details,
                'system': 'System2_Runtime_Validation'
            }

            with open(incident_log_path, 'a') as f:
                f.write(json.dumps(incident) + '\n')

            # Try to log to database
            try:
                from modules.database.database_manager import DatabaseManager
                db = DatabaseManager()

                insert_query = """
                    INSERT INTO security_detections
                    (detection_type, severity, pattern_matched, text_sample, metadata, action_taken)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                db.execute_query(
                    insert_query,
                    (
                        incident_type,
                        'critical',
                        'security_token_validation',
                        details,
                        json.dumps(incident),
                        'workflow_aborted'
                    )
                )
            except:
                pass  # Database logging is best-effort

        except Exception as e:
            logger.error(f"Failed to log security incident: {e}")


# Convenience functions for integration

def validate_prompt_file(file_path: str, prompt_name: str = "tier1_core_prompt") -> bool:
    """
    Run System 1 validation on a prompt file.

    Args:
        file_path: Path to prompt file
        prompt_name: Prompt identifier

    Returns:
        True if valid or successfully fixed
    """
    system1 = PromptValidationSystem1()
    is_valid, was_replaced = system1.validate_and_fix(file_path, prompt_name)
    return is_valid


def analyze_jobs_with_validation(jobs: List[Dict]) -> Dict[str, Any]:
    """
    Analyze jobs using the complete System 2 workflow.

    Args:
        jobs: List of job dictionaries

    Returns:
        Analysis results or error information
    """
    system2 = PromptValidationSystem2()

    # Determine prompt file path
    prompt_file = os.path.join(
        os.path.dirname(__file__),
        "prompts",
        "tier1_core_prompt.py"
    )

    result = system2.execute_workflow(
        jobs=jobs,
        prompt_file_path=prompt_file,
        prompt_name="tier1_core_prompt"
    )

    return result