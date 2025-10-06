"""
User Job Preference Packages System
Handles multiple preference packages per user with contextual conditions
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class PreferencePackages:
    """
    Manages multiple job preference packages per user
    Each package has conditions and preferences for different scenarios
    """

    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_preference_package(self, user_id: str, package_data: Dict) -> str:
        """
        Create a new preference package for a user

        Args:
            user_id: User identifier
            package_data: Complete package configuration

        Returns:
            package_id: Unique identifier for the package
        """
        with self.db_manager.get_session() as session:
            try:
                # Insert new preference package
                insert_query = """
                    INSERT INTO user_job_preferences (
                        user_id, package_name, package_description, 
                        conditions, preferences, is_active, created_at
                    ) VALUES (
                        %(user_id)s, %(package_name)s, %(package_description)s,
                        %(conditions)s, %(preferences)s, %(is_active)s, %(created_at)s
                    ) RETURNING package_id
                """

                result = session.execute(
                    insert_query,
                    {
                        "user_id": user_id,
                        "package_name": package_data["package_name"],
                        "package_description": package_data.get("package_description", ""),
                        "conditions": json.dumps(package_data["conditions"]),
                        "preferences": json.dumps(package_data["preferences"]),
                        "is_active": package_data.get("is_active", True),
                        "created_at": datetime.utcnow(),
                    },
                )

                package_id = result.fetchone()[0]
                session.commit()

                logger.info(f"Created preference package {package_id} for user {user_id}")
                return package_id

            except Exception as e:
                session.rollback()
                logger.error(f"Error creating preference package: {e}")
                raise

    def get_matching_package(self, user_id: str, job_context: Dict) -> Optional[Dict]:
        """
        Get the best matching preference package for a job context

        Args:
            user_id: User identifier
            job_context: Job details including location, salary, etc.

        Returns:
            Dict with package details or None if no match
        """
        with self.db_manager.get_session() as session:
            try:
                # Get all active packages for user
                query = """
                    SELECT package_id, package_name, package_description,
                           conditions, preferences, priority_score
                    FROM user_job_preferences 
                    WHERE user_id = %(user_id)s 
                    AND is_active = true
                    ORDER BY priority_score DESC
                """

                result = session.execute(query, {"user_id": user_id})
                packages = result.fetchall()

                if not packages:
                    logger.warning(f"No active preference packages found for user {user_id}")
                    return None

                # Find best matching package
                best_match = None
                best_score = -1

                for package in packages:
                    package_dict = {
                        "package_id": package[0],
                        "package_name": package[1],
                        "package_description": package[2],
                        "conditions": json.loads(package[3]),
                        "preferences": json.loads(package[4]),
                        "priority_score": package[5],
                    }

                    match_score = self._calculate_match_score(package_dict["conditions"], job_context)

                    if match_score > best_score:
                        best_score = match_score
                        best_match = package_dict

                if best_match:
                    logger.info(
                        f"Selected package '{best_match['package_name']}' for job context (score: {best_score})"
                    )

                return best_match

            except Exception as e:
                logger.error(f"Error finding matching package: {e}")
                return None

    def _calculate_match_score(self, conditions: Dict, job_context: Dict) -> float:
        """
        Calculate how well a package's conditions match a job context

        Args:
            conditions: Package conditions
            job_context: Job details

        Returns:
            Float score (0-100, higher is better match)
        """
        score = 0
        total_conditions = 0

        # Location-based matching
        if "location" in conditions and "location" in job_context:
            total_conditions += 1
            job_location = job_context["location"].lower()

            # Check for exact location matches
            if "exact_locations" in conditions["location"]:
                for location in conditions["location"]["exact_locations"]:
                    if location.lower() in job_location:
                        score += 30
                        break

            # Check for proximity-based rules
            if "proximity_rules" in conditions["location"]:
                # This would integrate with a geocoding service
                # For now, simple keyword matching
                if "local_keywords" in conditions["location"]["proximity_rules"]:
                    for keyword in conditions["location"]["proximity_rules"]["local_keywords"]:
                        if keyword.lower() in job_location:
                            score += 25
                            break

                if "remote_keywords" in conditions["location"]["proximity_rules"]:
                    for keyword in conditions["location"]["proximity_rules"]["remote_keywords"]:
                        if keyword.lower() in job_location:
                            score += 15
                            break

        # Salary range matching
        if "salary_context" in conditions and "salary_low" in job_context:
            total_conditions += 1
            job_salary = job_context.get("salary_low", 0)

            salary_ranges = conditions["salary_context"]
            if "preferred_range" in salary_ranges:
                min_salary = salary_ranges["preferred_range"]["min"]
                max_salary = salary_ranges["preferred_range"]["max"]

                if min_salary <= job_salary <= max_salary:
                    score += 20
                elif job_salary >= min_salary:
                    score += 10

        # Work arrangement matching
        if "work_arrangement" in conditions and "remote_work" in job_context:
            total_conditions += 1
            job_remote = job_context.get("remote_work", "").lower()
            preferred_arrangements = conditions["work_arrangement"]["preferred"]

            if job_remote in [arr.lower() for arr in preferred_arrangements]:
                score += 15

        # Company size matching
        if "company_preferences" in conditions and "company_size" in job_context:
            total_conditions += 1
            job_company_size = job_context.get("company_size", "")
            preferred_sizes = conditions["company_preferences"].get("preferred_sizes", [])

            if job_company_size in preferred_sizes:
                score += 10

        # Industry matching
        if "industry_preferences" in conditions and "industry" in job_context:
            total_conditions += 1
            job_industry = job_context.get("industry", "").lower()
            preferred_industries = conditions["industry_preferences"].get("preferred", [])
            excluded_industries = conditions["industry_preferences"].get("excluded", [])

            if job_industry in [ind.lower() for ind in preferred_industries]:
                score += 15
            elif job_industry in [ind.lower() for ind in excluded_industries]:
                score -= 50  # Strong negative for excluded industries

        # Normalize score based on number of conditions checked
        if total_conditions > 0:
            normalized_score = (score / total_conditions) * (total_conditions / 5)  # Adjust based on condition coverage
        else:
            normalized_score = 0

        return max(0, min(100, normalized_score))

    def get_targeted_search_configs(self, user_id: str) -> List[Dict]:
        """
        Generate targeted search configurations based on user's preference packages

        Args:
            user_id: User identifier

        Returns:
            List of search configurations optimized for user preferences
        """
        with self.db_manager.get_session() as session:
            try:
                # Get all active packages for user
                query = """
                    SELECT package_id, package_name, conditions, preferences
                    FROM user_job_preferences 
                    WHERE user_id = %(user_id)s 
                    AND is_active = true
                    ORDER BY priority_score DESC
                """

                result = session.execute(query, {"user_id": user_id})
                packages = result.fetchall()

                search_configs = []

                for package in packages:
                    conditions = json.loads(package[2])
                    preferences = json.loads(package[3])

                    # Extract search parameters from package
                    config = self._extract_search_config(conditions, preferences)
                    config["package_id"] = package[0]
                    config["package_name"] = package[1]

                    search_configs.append(config)

                logger.info(f"Generated {len(search_configs)} targeted search configs for user {user_id}")
                return search_configs

            except Exception as e:
                logger.error(f"Error generating search configs: {e}")
                return []

    def _extract_search_config(self, conditions: Dict, preferences: Dict) -> Dict:
        """
        Extract Apify search configuration from preference package

        Args:
            conditions: Package conditions
            preferences: Package preferences

        Returns:
            Search configuration for Apify scraper
        """
        config = {}

        # Job titles from preferences
        if "job_titles" in preferences:
            config["job_titles"] = preferences["job_titles"]["preferred"]
        else:
            config["job_titles"] = ["Marketing Manager"]  # Default

        # Locations from conditions
        if "location" in conditions:
            locations = []
            if "exact_locations" in conditions["location"]:
                locations.extend(conditions["location"]["exact_locations"])
            if "proximity_rules" in conditions["location"]:
                if "search_locations" in conditions["location"]["proximity_rules"]:
                    locations.extend(conditions["location"]["proximity_rules"]["search_locations"])
            config["locations"] = locations if locations else ["Edmonton, AB"]
        else:
            config["locations"] = ["Edmonton, AB"]

        # Salary filters
        if "salary_context" in conditions:
            salary_range = conditions["salary_context"].get("preferred_range", {})
            config["salary_min"] = salary_range.get("min", 0)
            config["salary_max"] = salary_range.get("max", 150000)

        # Work arrangement
        if "work_arrangement" in conditions:
            config["remote_work"] = conditions["work_arrangement"]["preferred"]

        # Job type preferences
        if "job_type" in preferences:
            config["job_types"] = preferences["job_type"]["preferred"]

        return config


def create_steve_glen_packages():
    """
    Create Steve Glen's preference packages for different scenarios
    """
    pp = PreferencePackages()
    user_id = "steve_glen"

    # Package 1: Local Edmonton jobs (higher acceptance, lower salary requirements)
    local_package = {
        "package_name": "Local Edmonton Jobs",
        "package_description": "Jobs within Edmonton or easy commute distance",
        "conditions": {
            "location": {
                "exact_locations": ["Edmonton, AB", "Edmonton", "Sherwood Park", "St. Albert"],
                "proximity_rules": {
                    "local_keywords": ["edmonton", "sherwood park", "st. albert", "leduc"],
                    "search_locations": ["Edmonton, AB", "Sherwood Park, AB", "St. Albert, AB"],
                },
            },
            "salary_context": {
                "preferred_range": {"min": 65000, "max": 85000},
                "acceptable_range": {"min": 60000, "max": 90000},
            },
            "work_arrangement": {
                "preferred": ["hybrid", "onsite", "remote"],
                "acceptable": ["hybrid", "onsite", "remote"],
            },
        },
        "preferences": {
            "job_titles": {
                "preferred": ["Marketing Manager", "Marketing Coordinator", "Digital Marketing Manager"],
                "acceptable": ["Marketing Specialist", "Communications Manager", "Brand Manager"],
            },
            "job_type": {"preferred": ["Full-time", "Contract"]},
            "industry_preferences": {
                "preferred": ["Marketing", "Technology", "Healthcare", "Professional Services"],
                "excluded": ["Oil & Gas", "Construction"],
            },
        },
        "priority_score": 90,
        "is_active": True,
    }

    # Package 2: Regional Alberta jobs (higher salary required for commute)
    regional_package = {
        "package_name": "Regional Alberta Jobs",
        "package_description": "Jobs requiring commute outside Edmonton area",
        "conditions": {
            "location": {
                "exact_locations": ["Calgary, AB", "Red Deer, AB", "Fort McMurray, AB"],
                "proximity_rules": {
                    "remote_keywords": ["calgary", "red deer", "fort mcmurray", "grande prairie"],
                    "search_locations": ["Calgary, AB", "Red Deer, AB", "Alberta, CA"],
                },
            },
            "salary_context": {
                "preferred_range": {"min": 85000, "max": 120000},
                "acceptable_range": {"min": 80000, "max": 130000},
            },
            "work_arrangement": {"preferred": ["remote", "hybrid"], "acceptable": ["remote", "hybrid"]},
        },
        "preferences": {
            "job_titles": {
                "preferred": ["Marketing Manager", "Senior Marketing Manager", "Marketing Director"],
                "acceptable": ["Digital Marketing Manager", "Brand Manager"],
            },
            "job_type": {"preferred": ["Full-time"]},
            "industry_preferences": {
                "preferred": ["Technology", "Healthcare", "Professional Services", "Finance"],
                "excluded": ["Oil & Gas"],
            },
        },
        "priority_score": 70,
        "is_active": True,
    }

    # Package 3: Remote-first jobs (flexible on location, focused on role quality)
    remote_package = {
        "package_name": "Remote-First Opportunities",
        "package_description": "High-quality remote positions across Canada",
        "conditions": {
            "location": {
                "exact_locations": ["Remote", "Canada"],
                "proximity_rules": {
                    "remote_keywords": ["remote", "work from home", "distributed"],
                    "search_locations": ["Canada", "Toronto, ON", "Vancouver, BC", "Montreal, QC"],
                },
            },
            "salary_context": {
                "preferred_range": {"min": 75000, "max": 110000},
                "acceptable_range": {"min": 70000, "max": 120000},
            },
            "work_arrangement": {"preferred": ["remote"], "acceptable": ["remote", "hybrid"]},
        },
        "preferences": {
            "job_titles": {
                "preferred": ["Marketing Manager", "Digital Marketing Manager", "Content Marketing Manager"],
                "acceptable": ["Marketing Specialist", "Growth Marketing Manager"],
            },
            "job_type": {"preferred": ["Full-time", "Contract"]},
            "industry_preferences": {
                "preferred": ["Technology", "SaaS", "E-commerce", "Healthcare"],
                "excluded": ["Oil & Gas", "Construction", "Manufacturing"],
            },
        },
        "priority_score": 80,
        "is_active": True,
    }

    # Create packages
    try:
        local_id = pp.create_preference_package(user_id, local_package)
        regional_id = pp.create_preference_package(user_id, regional_package)
        remote_id = pp.create_preference_package(user_id, remote_package)

        logger.info(f"Created preference packages: Local ({local_id}), Regional ({regional_id}), Remote ({remote_id})")

        return {"local": local_id, "regional": regional_id, "remote": remote_id}

    except Exception as e:
        logger.error(f"Error creating Steve Glen packages: {e}")
        raise


if __name__ == "__main__":
    # Test the system
    logging.basicConfig(level=logging.INFO)

    # Create Steve Glen's packages
    package_ids = create_steve_glen_packages()

    # Test targeted search generation
    pp = PreferencePackages()
    search_configs = pp.get_targeted_search_configs("steve_glen")

    print(f"Generated {len(search_configs)} search configurations:")
    for config in search_configs:
        print(f"- {config['package_name']}: {config['locations']}")
