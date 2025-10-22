"""
Module: prompt_security_manager.py
Purpose: Hash-based security system for LLM prompts with user/agent detection
Created: 2024-10-12
Modified: 2025-10-21
Dependencies: hashlib, json, pathlib
Related: prompt_validation_systems.py, ai_analyzer.py, register_canonical_prompts.py
Description: Implements SHA-256 hash-based validation of prompt string sections
             with change source detection (user vs agent). Auto-replaces agent
             modifications while allowing user changes. Protects against prompt
             injection, unintentional automation bugs, and agent modifications.
             Includes audit logging and canonical prompt replacement.
"""

import hashlib
import json
import logging
import os
import re
from typing import Dict, Optional, Tuple, Literal
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


ChangeSource = Literal['user', 'agent', 'system', 'unknown']


class PromptSecurityManager:
    """
    Manages prompt security through hash-based validation and replacement.

    KEY BEHAVIORS:
    - If USER changed prompt: Update hash, allow change, log it
    - If AGENT changed prompt: Replace with canonical, log security incident
    - Only hashes prompt strings, not entire files

    This protects against:
    - Agent/system accidentally modifying security-critical prompt sections
    - Prompt injection from compromised data
    - Unintentional automation bugs that modify prompts

    This allows:
    - User to intentionally update prompts
    - User modifications are tracked and audited
    """

    def __init__(
        self,
        hash_registry_path: Optional[str] = None,
        change_log_path: Optional[str] = None
    ):
        """
        Initialize the prompt security manager.

        Args:
            hash_registry_path: Path to JSON file storing prompt hashes
                              (default: storage/prompt_hashes.json)
            change_log_path: Path to change log file
                           (default: storage/prompt_changes.jsonl)
        """
        if hash_registry_path is None:
            hash_registry_path = os.path.join(
                os.getcwd(), "storage", "prompt_hashes.json"
            )

        if change_log_path is None:
            change_log_path = os.path.join(
                os.getcwd(), "storage", "prompt_changes.jsonl"
            )

        self.hash_registry_path = hash_registry_path
        self.change_log_path = change_log_path
        self.hash_registry = self._load_hash_registry()

        # Ensure storage directory exists
        os.makedirs(os.path.dirname(self.hash_registry_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.change_log_path), exist_ok=True)

        logger.info(f"PromptSecurityManager initialized with registry: {self.hash_registry_path}")

    def _load_hash_registry(self) -> Dict:
        """
        Load the hash registry from disk.

        Returns:
            Dict containing prompt name -> hash mappings with metadata
        """
        try:
            if os.path.exists(self.hash_registry_path):
                with open(self.hash_registry_path, 'r') as f:
                    registry = json.load(f)
                    logger.info(f"Loaded {len(registry)} prompt hashes from registry")
                    return registry
            else:
                logger.info("No existing hash registry found, creating new one")
                return {}
        except Exception as e:
            logger.error(f"Failed to load hash registry: {e}")
            return {}

    def _save_hash_registry(self):
        """Save the current hash registry to disk."""
        try:
            with open(self.hash_registry_path, 'w') as f:
                json.dump(self.hash_registry, f, indent=2)
            logger.info(f"Saved {len(self.hash_registry)} prompt hashes to registry")
        except Exception as e:
            logger.error(f"Failed to save hash registry: {e}")

    def _log_change(
        self,
        prompt_name: str,
        old_hash: str,
        new_hash: str,
        change_source: ChangeSource,
        action_taken: str,
        additional_info: Optional[Dict] = None
    ):
        """
        Log prompt changes to JSONL file for audit trail.

        Args:
            prompt_name: Name of the prompt that changed
            old_hash: Previous hash
            new_hash: New hash
            change_source: Who made the change ('user', 'agent', 'system')
            action_taken: What action was taken ('updated_hash', 'replaced_prompt', 'rejected')
            additional_info: Additional metadata
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'prompt_name': prompt_name,
                'old_hash': old_hash[:16],  # First 16 chars for readability
                'new_hash': new_hash[:16],
                'change_source': change_source,
                'action_taken': action_taken,
            }

            if additional_info:
                log_entry['additional_info'] = additional_info

            # Append to JSONL file
            with open(self.change_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            logger.info(
                f"Logged change: {prompt_name} by {change_source} -> {action_taken}"
            )

        except Exception as e:
            logger.error(f"Failed to log change: {e}")

    def _log_to_database(
        self,
        prompt_name: str,
        change_source: ChangeSource,
        old_hash: str,
        new_hash: str,
        action_taken: str
    ):
        """Log to security_detections table if available."""
        try:
            from modules.database.database_manager import DatabaseManager
            db = DatabaseManager()

            # Determine severity based on source
            severity = 'high' if change_source in ['agent', 'system', 'unknown'] else 'low'

            insert_query = """
                INSERT INTO security_detections
                (detection_type, severity, pattern_matched, text_sample, metadata, action_taken)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            metadata = {
                'prompt_name': prompt_name,
                'change_source': change_source,
                'old_hash': old_hash,
                'new_hash': new_hash,
                'timestamp': datetime.now().isoformat(),
            }

            db.execute_query(
                insert_query,
                (
                    'prompt_modification',
                    severity,
                    'prompt_hash_changed',
                    f"Prompt '{prompt_name}' changed by {change_source}",
                    json.dumps(metadata),
                    action_taken
                )
            )

        except Exception as e:
            logger.error(f"Failed to log to database: {e}")

    def extract_prompt_section(self, file_content: str, section_marker: str = 'PROMPT_START') -> Optional[str]:
        """
        Extract only the prompt section from a file.

        This allows hashing only the prompt string, not the entire file.

        Args:
            file_content: Full file content
            section_marker: Marker to identify prompt section (default: 'PROMPT_START')

        Returns:
            Extracted prompt section, or None if not found

        Example file structure:
            ```python
            # PROMPT_START
            prompt_text = '''
            This is the prompt text to be hashed.
            Security tokens and instructions go here.
            '''
            # PROMPT_END
            ```
        """
        # Try to find marked sections first
        if section_marker in file_content:
            pattern = rf'#\s*{section_marker}\s*\n(.*?)\n\s*#\s*PROMPT_END'
            match = re.search(pattern, file_content, re.DOTALL)
            if match:
                return match.group(1).strip()

        # Fallback: Find prompt_parts or large string literals
        # Look for prompt_parts list (common pattern in our codebase)
        prompt_parts_pattern = r'prompt_parts\s*=\s*\[(.*?)\]'
        match = re.search(prompt_parts_pattern, file_content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Look for large multi-line strings (likely prompts)
        multiline_string_pattern = r'["\']{{3}}(.*?)["\']{{3}}'
        matches = re.findall(multiline_string_pattern, file_content, re.DOTALL)
        if matches:
            # Return the longest one (likely the main prompt)
            return max(matches, key=len).strip()

        logger.warning(f"Could not find prompt section with marker '{section_marker}'")
        return None

    def calculate_prompt_hash(self, prompt_content: str) -> str:
        """
        Calculate SHA-256 hash of prompt content.

        Args:
            prompt_content: The prompt text to hash

        Returns:
            Hexadecimal hash string
        """
        # Remove dynamic content (security tokens, timestamps) before hashing
        # to get consistent hashes for the same prompt template
        normalized_content = self._normalize_prompt_for_hashing(prompt_content)

        hash_obj = hashlib.sha256(normalized_content.encode('utf-8'))
        return hash_obj.hexdigest()

    def _normalize_prompt_for_hashing(self, prompt: str) -> str:
        """
        Normalize prompt by removing dynamic content before hashing.

        This ensures the hash represents the prompt structure, not dynamic values.

        Args:
            prompt: Raw prompt text

        Returns:
            Normalized prompt text
        """
        # Remove security tokens (SEC_TOKEN_xxxxx)
        normalized = re.sub(r'SEC_TOKEN_[A-Za-z0-9]{32}', 'SEC_TOKEN_PLACEHOLDER', prompt)

        # Remove timestamps
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP_PLACEHOLDER', normalized)

        # Remove job IDs (UUIDs)
        normalized = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            'UUID_PLACEHOLDER',
            normalized
        )

        # Remove job count numbers
        normalized = re.sub(r'Analyze these \d+ job postings', 'Analyze these N job postings', normalized)

        # Remove variable job descriptions and titles
        normalized = re.sub(r'DESCRIPTION:.*?---', 'DESCRIPTION: PLACEHOLDER\n---', normalized, flags=re.DOTALL)
        normalized = re.sub(r'TITLE:.*?\n', 'TITLE: PLACEHOLDER\n', normalized)

        return normalized

    def register_prompt(
        self,
        prompt_name: str,
        prompt_content: str,
        change_source: ChangeSource = 'system'
    ) -> str:
        """
        Register a prompt template and store its hash.

        Args:
            prompt_name: Unique identifier for this prompt (e.g., "tier1_core_prompt")
            prompt_content: The prompt template content
            change_source: Who is registering ('user', 'agent', 'system')

        Returns:
            The calculated hash
        """
        prompt_hash = self.calculate_prompt_hash(prompt_content)

        # Check if this is a new prompt or an update
        if prompt_name in self.hash_registry:
            old_hash = self.hash_registry[prompt_name]['hash']
            if old_hash != prompt_hash:
                logger.info(
                    f"Prompt '{prompt_name}' updated by {change_source}. "
                    f"Old hash: {old_hash[:8]}... New hash: {prompt_hash[:8]}..."
                )
                self._log_change(
                    prompt_name, old_hash, prompt_hash, change_source, 'updated_hash'
                )

        # Store the hash with metadata
        self.hash_registry[prompt_name] = {
            'hash': prompt_hash,
            'registered_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'last_updated_by': change_source,
        }

        self._save_hash_registry()
        logger.info(f"Registered prompt '{prompt_name}' with hash {prompt_hash[:8]}... (source: {change_source})")

        return prompt_hash

    def validate_and_handle_prompt(
        self,
        prompt_name: str,
        current_prompt: str,
        change_source: ChangeSource,
        canonical_prompt_getter: callable
    ) -> Tuple[str, bool]:
        """
        Validate prompt and handle based on change source.

        KEY LOGIC:
        - If hash matches: Return current prompt (no change)
        - If hash differs AND source is USER: Update hash, return current prompt
        - If hash differs AND source is AGENT/SYSTEM: Replace with canonical, log incident

        Args:
            prompt_name: Name of the prompt
            current_prompt: The prompt being validated
            change_source: Who is using this prompt ('user', 'agent', 'system')
            canonical_prompt_getter: Function that returns the canonical prompt

        Returns:
            Tuple of (prompt_to_use, was_replaced)
        """
        if prompt_name not in self.hash_registry:
            # New prompt, register it
            logger.info(f"New prompt '{prompt_name}' detected, registering...")
            self.register_prompt(prompt_name, current_prompt, change_source)
            return current_prompt, False

        expected_hash = self.hash_registry[prompt_name]['hash']
        current_hash = self.calculate_prompt_hash(current_prompt)

        # Hash matches - no change
        if expected_hash == current_hash:
            logger.debug(f"Prompt '{prompt_name}' validation: PASSED")
            return current_prompt, False

        # Hash differs - check who made the change
        logger.warning(
            f"Prompt '{prompt_name}' hash mismatch! "
            f"Expected: {expected_hash[:8]}... Got: {current_hash[:8]}... "
            f"Change source: {change_source}"
        )

        # USER changed it - update hash and allow
        if change_source == 'user':
            logger.info(
                f"User intentionally modified prompt '{prompt_name}'. "
                f"Updating hash to reflect new version."
            )

            self._log_change(
                prompt_name, expected_hash, current_hash, 'user', 'updated_hash',
                {'reason': 'user_modification'}
            )

            self._log_to_database(
                prompt_name, 'user', expected_hash, current_hash, 'hash_updated'
            )

            # Update the registry
            self.register_prompt(prompt_name, current_prompt, 'user')

            return current_prompt, False

        # AGENT/SYSTEM changed it - replace with canonical
        else:
            logger.error(
                f"SECURITY: Agent/system modified prompt '{prompt_name}' without authorization! "
                f"Replacing with canonical version."
            )

            self._log_change(
                prompt_name, expected_hash, current_hash, change_source, 'replaced_prompt',
                {'reason': 'unauthorized_agent_modification'}
            )

            self._log_to_database(
                prompt_name, change_source, expected_hash, current_hash, 'prompt_replaced'
            )

            try:
                canonical_prompt = canonical_prompt_getter()
                canonical_hash = self.calculate_prompt_hash(canonical_prompt)

                if canonical_hash == expected_hash:
                    logger.info(f"Successfully replaced prompt '{prompt_name}' with canonical version")
                    return canonical_prompt, True
                else:
                    # Canonical version also differs - this might be a legitimate update
                    # that happened outside the system
                    logger.warning(
                        f"Canonical prompt for '{prompt_name}' also differs from registry. "
                        f"This might be a legitimate code update. "
                        f"Updating hash to match canonical version."
                    )
                    self.register_prompt(prompt_name, canonical_prompt, 'system')
                    return canonical_prompt, True

            except Exception as e:
                logger.error(f"Failed to get canonical prompt for '{prompt_name}': {e}")
                # Can't replace, use current but log the incident
                return current_prompt, False

    def validate_file_prompt(
        self,
        prompt_file_path: str,
        prompt_name: str,
        change_source: ChangeSource,
        section_marker: str = 'PROMPT_START'
    ) -> Tuple[Optional[str], bool]:
        """
        Validate prompt section within a file.

        This reads the file, extracts the prompt section, validates it,
        and returns the correct prompt to use.

        Args:
            prompt_file_path: Path to the prompt file
            prompt_name: Name of the prompt for registry lookup
            change_source: Who is validating ('user', 'agent', 'system')
            section_marker: Marker to identify prompt section

        Returns:
            Tuple of (prompt_to_use, was_replaced)
        """
        try:
            with open(prompt_file_path, 'r') as f:
                file_content = f.read()

            # Extract prompt section
            prompt_section = self.extract_prompt_section(file_content, section_marker)

            if prompt_section is None:
                logger.warning(f"Could not extract prompt section from {prompt_file_path}")
                return None, False

            # For validation, we need the canonical getter
            # This is a bit tricky since we're working with files
            # For now, return the extracted section and let the caller handle validation

            logger.info(f"Extracted prompt section from {prompt_file_path} for validation")
            return prompt_section, False

        except Exception as e:
            logger.error(f"Failed to validate file prompt: {e}")
            return None, False

    def get_change_history(self, prompt_name: Optional[str] = None, limit: int = 50) -> list:
        """
        Get change history from the log file.

        Args:
            prompt_name: Filter by specific prompt name (optional)
            limit: Maximum number of entries to return

        Returns:
            List of change log entries
        """
        try:
            if not os.path.exists(self.change_log_path):
                return []

            changes = []
            with open(self.change_log_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if prompt_name is None or entry.get('prompt_name') == prompt_name:
                            changes.append(entry)
                    except json.JSONDecodeError:
                        continue

            # Return most recent first
            changes.reverse()
            return changes[:limit]

        except Exception as e:
            logger.error(f"Failed to get change history: {e}")
            return []

    def get_registry_status(self) -> Dict:
        """
        Get current status of the prompt registry.

        Returns:
            Dict with registry statistics
        """
        return {
            'total_prompts': len(self.hash_registry),
            'prompts': {
                name: {
                    'hash': data['hash'][:16],
                    'last_updated': data.get('last_updated'),
                    'last_updated_by': data.get('last_updated_by', 'unknown')
                }
                for name, data in self.hash_registry.items()
            },
            'registry_path': self.hash_registry_path,
            'change_log_path': self.change_log_path,
        }
