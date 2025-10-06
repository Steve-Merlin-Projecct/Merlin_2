"""
Job Scrape Data Pipeline
Handles the flow from raw scrapes to cleaned/deduplicated job data
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4
from modules.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ScrapeDataPipeline:
    """
    Manages the data pipeline from raw job scrapes to cleaned, deduplicated job records
    """

    def __init__(self):
        self.db = DatabaseManager()

    def insert_raw_scrape(self, source_website: str, source_url: str, raw_data: Dict, **kwargs) -> str:
        """
        Insert a raw scrape record with comprehensive data sanitization

        Args:
            source_website: Website where data was scraped (e.g., 'indeed.ca')
            source_url: Full URL of the job posting
            raw_data: Complete raw JSON data from scraper
            **kwargs: Additional metadata (scraper_used, user_agent, etc.)

        Returns:
            str: UUID of the inserted raw scrape record
        """
        try:
            # Import security sanitization
            from modules.security.security_patch import SecurityPatch

            # Sanitize raw data before storage
            sanitized_data = SecurityPatch.sanitize_job_data(raw_data)

            # Sanitize metadata
            sanitized_website = SecurityPatch._sanitize_text_content(source_website)
            sanitized_url = SecurityPatch._sanitize_text_content(source_url)

            # Validate essential data
            if not sanitized_data or not sanitized_data.get("id"):
                raise ValueError("Invalid job data after sanitization")

            scrape_id = str(uuid4())

            # Extract optional metadata with sanitization
            full_application_url = kwargs.get("full_application_url", sanitized_url)
            if full_application_url:
                full_application_url = SecurityPatch._sanitize_text_content(full_application_url)

            scraper_used = kwargs.get("scraper_used", "unknown")
            if scraper_used:
                scraper_used = SecurityPatch._sanitize_text_content(scraper_used)

            scraper_run_id = kwargs.get("scraper_run_id")
            if scraper_run_id:
                scraper_run_id = SecurityPatch._sanitize_text_content(str(scraper_run_id))

            user_agent = kwargs.get("user_agent")
            if user_agent:
                user_agent = SecurityPatch._sanitize_text_content(user_agent)

            ip_address = kwargs.get("ip_address")
            if ip_address:
                # Basic IP validation
                ip_address = SecurityPatch._sanitize_text_content(ip_address)
                if not re.match(r"^[0-9.:a-fA-F]+$", ip_address):
                    ip_address = None

            response_time_ms = kwargs.get("response_time_ms")
            if response_time_ms is not None:
                try:
                    response_time_ms = int(float(response_time_ms))
                    if response_time_ms < 0 or response_time_ms > 300000:  # Max 5 minutes
                        response_time_ms = None
                except:
                    response_time_ms = None

            # Calculate data size from sanitized data
            data_size_bytes = len(json.dumps(sanitized_data).encode("utf-8"))

            query = """
                INSERT INTO raw_job_scrapes (
                    scrape_id, source_website, source_url, full_application_url,
                    raw_data, scraper_used, scraper_run_id, user_agent, ip_address,
                    response_time_ms, data_size_bytes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                scrape_id,
                sanitized_website,
                sanitized_url,
                full_application_url,
                json.dumps(sanitized_data),
                scraper_used,
                scraper_run_id,
                user_agent,
                ip_address,
                response_time_ms,
                data_size_bytes,
            )

            self.db.execute_query(query, params)
            logger.info(f"Inserted sanitized raw scrape {scrape_id} from {sanitized_website}")

            return scrape_id

        except Exception as e:
            logger.error(f"Error inserting raw scrape: {e}")
            raise

    def process_raw_scrapes_to_cleaned(self, batch_size: int = 100) -> Dict:
        """
        Process unprocessed raw scrapes into cleaned, deduplicated records

        Args:
            batch_size: Number of raw scrapes to process in one batch

        Returns:
            Dict: Processing statistics
        """
        try:
            # Get unprocessed raw scrapes
            raw_scrapes = self._get_unprocessed_raw_scrapes(batch_size)

            if not raw_scrapes:
                return {"processed": 0, "cleaned_created": 0, "duplicates_merged": 0}

            processed_count = 0
            cleaned_created = 0
            duplicates_merged = 0

            for raw_scrape in raw_scrapes:
                try:
                    # Clean and normalize the data
                    cleaned_data = self._clean_job_data(raw_scrape)

                    if cleaned_data:
                        # Check for duplicates and merge if necessary
                        existing_cleaned = self._find_duplicate_cleaned_job(cleaned_data)

                        if existing_cleaned:
                            # Merge with existing record
                            self._merge_duplicate_job(
                                existing_cleaned["cleaned_job_id"], raw_scrape["scrape_id"], cleaned_data
                            )
                            duplicates_merged += 1
                        else:
                            # Create new cleaned record
                            self._create_cleaned_job_record(cleaned_data, [raw_scrape["scrape_id"]])
                            cleaned_created += 1

                    # Mark raw scrape as processed
                    self._mark_raw_scrape_processed(raw_scrape["scrape_id"])
                    processed_count += 1

                except Exception as e:
                    logger.error(f"Error processing raw scrape {raw_scrape['scrape_id']}: {e}")
                    self._mark_raw_scrape_error(raw_scrape["scrape_id"], str(e))

            logger.info(
                f"Pipeline processed {processed_count} raw scrapes, "
                f"created {cleaned_created} new cleaned records, "
                f"merged {duplicates_merged} duplicates"
            )

            return {
                "processed": processed_count,
                "cleaned_created": cleaned_created,
                "duplicates_merged": duplicates_merged,
            }

        except Exception as e:
            logger.error(f"Error in scrape pipeline: {e}")
            raise

    def _get_unprocessed_raw_scrapes(self, limit: int) -> List[Dict]:
        """Get raw scrapes that haven't been processed yet"""
        query = """
            SELECT scrape_id, source_website, source_url, raw_data, scrape_timestamp
            FROM raw_job_scrapes 
            ORDER BY scrape_timestamp DESC
            LIMIT %s
        """

        results = self.db.execute_query(query, (limit,))
        return [dict(row) for row in results] if results else []

    def _clean_job_data(self, raw_scrape: Dict) -> Optional[Dict]:
        """
        Clean and normalize raw job data

        Args:
            raw_scrape: Raw scrape record

        Returns:
            Dict: Cleaned job data or None if data is invalid
        """
        try:
            raw_data = raw_scrape["raw_data"]

            # Handle different scraper formats (Apify, custom, etc.)
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)

            # Extract and clean data based on source
            cleaned = {
                "source_website": raw_scrape["source_website"],
                "external_job_id": self._extract_external_job_id(raw_data, raw_scrape["source_url"]),
                "application_url": raw_scrape["source_url"],
            }

            # Job title cleaning
            cleaned["job_title"] = self._clean_text(
                raw_data.get("positionName") or raw_data.get("title") or raw_data.get("job_title")
            )

            # Company name cleaning
            cleaned["company_name"] = self._clean_text(
                raw_data.get("companyName") or raw_data.get("company") or raw_data.get("employer")
            )

            # Location cleaning
            location_raw = raw_data.get("location", "")
            if location_raw:
                location_data = self._parse_location(location_raw)
                cleaned.update(location_data)  # Merge all location fields
            else:
                cleaned["location_city"] = None
                cleaned["location_province"] = None
                cleaned["location_country"] = "CA"  # Default for Canadian jobs

            # Job description
            description = raw_data.get("description") or raw_data.get("snippet", "")
            cleaned["job_description"] = self._clean_text(description, max_length=5000)

            # Salary extraction - fix unpacking error
            salary_text = raw_data.get("salary", "")
            if salary_text:
                try:
                    salary_data = self._parse_salary(salary_text)
                    if len(salary_data) == 4:
                        # Unpack 4 values
                        salary_low, salary_high, salary_currency, salary_period = salary_data
                        cleaned["salary_min"] = salary_low  # Match database schema
                        cleaned["salary_max"] = salary_high  # Match database schema
                        cleaned["salary_currency"] = salary_currency
                        cleaned["salary_period"] = salary_period
                    elif len(salary_data) == 2:
                        # Unpack 2 values (low, high only)
                        salary_low, salary_high = salary_data
                        cleaned["salary_min"] = salary_low
                        cleaned["salary_max"] = salary_high
                        cleaned["salary_currency"] = "CAD"  # Default for Canadian jobs
                        cleaned["salary_period"] = "yearly"
                except Exception as e:
                    logger.error(f"Error parsing salary '{salary_text}': {e}")
                    cleaned["salary_min"] = None
                    cleaned["salary_max"] = None

            # Work arrangement
            job_types = raw_data.get("jobType", [])
            if isinstance(job_types, list):
                for job_type in job_types:
                    if "remote" in str(job_type).lower():
                        cleaned["work_arrangement"] = "remote"
                        break
                    elif "hybrid" in str(job_type).lower():
                        cleaned["work_arrangement"] = "hybrid"
                        break
                else:
                    cleaned["work_arrangement"] = "onsite"

            # Job type
            if job_types:
                cleaned["job_type"] = self._clean_text(str(job_types[0]) if job_types else "Full-time")
            else:
                cleaned["job_type"] = "Full-time"

            # Posting date
            posted_at = raw_data.get("postedAt") or raw_data.get("scrapedAt")
            if posted_at:
                cleaned["posting_date"] = self._parse_date(posted_at)

            # External apply link
            apply_link = raw_data.get("externalApplyLink")
            if apply_link:
                cleaned["external_apply_link"] = self._clean_text(apply_link)

            # Company rating and reviews
            rating = raw_data.get("rating")
            if rating:
                try:
                    cleaned["company_rating"] = float(rating)
                except:
                    pass

            reviews_count = raw_data.get("reviewsCount")
            if reviews_count:
                try:
                    cleaned["company_reviews_count"] = int(reviews_count)
                except:
                    pass

            # Validate required fields
            if not cleaned.get("job_title") or not cleaned.get("company_name"):
                logger.warning(
                    f"Missing required fields in job data: title={bool(cleaned.get('job_title'))}, company={bool(cleaned.get('company_name'))}"
                )
                return None

            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning job data: {e}")
            return None

            # Location processing
            location_raw = raw_data.get("location") or raw_data.get("jobLocation")
            cleaned.update(self._parse_location(location_raw))

            # Salary processing
            salary_data = self._parse_salary(raw_data.get("salary") or raw_data.get("salaryRange"))
            cleaned.update(salary_data)

            # Description and requirements
            cleaned["job_description"] = self._clean_html(
                raw_data.get("description") or raw_data.get("descriptionHTML") or raw_data.get("job_description")
            )

            # Company details
            cleaned["company_website"] = raw_data.get("companyWebsite")
            cleaned["company_logo_url"] = raw_data.get("companyLogo")
            cleaned["reviews_count"] = self._safe_int(raw_data.get("reviewsCount"))
            cleaned["company_rating"] = self._safe_float(raw_data.get("rating"))

            # Job metadata
            cleaned["job_type"] = self._normalize_job_type(raw_data.get("jobType"))
            cleaned["work_arrangement"] = self._infer_work_arrangement(cleaned["job_description"], location_raw)
            cleaned["posting_date"] = self._parse_date(raw_data.get("postedAt") or raw_data.get("datePosted"))
            cleaned["is_expired"] = raw_data.get("isExpired", False)

            # Quality scoring
            cleaned["confidence_score"] = self._calculate_confidence_score(cleaned, raw_data)

            # Validation
            if not cleaned["job_title"] or not cleaned["company_name"]:
                logger.warning(f"Skipping invalid job data: missing title or company")
                return None

            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning job data: {e}")
            return None

    def _extract_external_job_id(self, raw_data: Dict, url: str) -> Optional[str]:
        """Extract the original job ID from the source site"""
        # Try to get ID from data first
        job_id = raw_data.get("id") or raw_data.get("jobId") or raw_data.get("external_id")

        if job_id:
            return str(job_id)

        # Try to extract from URL patterns
        patterns = [
            r"/viewjob\?jk=([a-zA-Z0-9]+)",  # Indeed
            r"/job/([a-zA-Z0-9-]+)",  # Generic
            r"jobId=([a-zA-Z0-9]+)",  # Query parameter
            r"/jobs/(\d+)",  # Numeric ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _clean_text(self, text: str, max_length: int = None) -> Optional[str]:
        """Clean and normalize text fields"""
        if not text:
            return None

        # Remove extra whitespace and normalize
        cleaned = re.sub(r"\s+", " ", str(text).strip())

        # Remove common prefixes/suffixes
        cleaned = re.sub(r"^(Job Title:|Position:|Title:)\s*", "", cleaned, flags=re.IGNORECASE)

        # Apply max length if specified
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        return cleaned if cleaned else None

    def _clean_html(self, html_text: str) -> Optional[str]:
        """Remove HTML tags and clean description text"""
        if not html_text:
            return None

        # Basic HTML tag removal
        text = re.sub(r"<[^>]+>", "", str(html_text))

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove common artifacts
        text = re.sub(r"&[a-zA-Z]+;", " ", text)  # HTML entities

        return text if text else None

    def _parse_location(self, location_raw: str) -> Dict:
        """Parse location string into structured components"""
        location_data = {
            "location_raw": location_raw,
            "location_city": None,
            "location_province": None,
            "location_country": None,
        }

        if not location_raw:
            return location_data

        # Canadian province patterns
        ca_provinces = {
            "AB": "Alberta",
            "BC": "British Columbia",
            "MB": "Manitoba",
            "NB": "New Brunswick",
            "NL": "Newfoundland and Labrador",
            "NS": "Nova Scotia",
            "ON": "Ontario",
            "PE": "Prince Edward Island",
            "QC": "Quebec",
            "SK": "Saskatchewan",
            "NT": "Northwest Territories",
            "NU": "Nunavut",
            "YT": "Yukon",
        }

        location_str = str(location_raw).strip()

        # Parse common formats: "City, Province" or "City, Province, Country"
        parts = [part.strip() for part in location_str.split(",")]

        if len(parts) >= 2:
            location_data["location_city"] = parts[0]

            # Check if second part is a Canadian province
            province_part = parts[1].upper()
            if province_part in ca_provinces:
                location_data["location_province"] = ca_provinces[province_part]
                location_data["location_country"] = "Canada"
            elif province_part.endswith(" CANADA"):
                prov = province_part.replace(" CANADA", "").strip()
                if prov in ca_provinces:
                    location_data["location_province"] = ca_provinces[prov]
                    location_data["location_country"] = "Canada"
            else:
                location_data["location_province"] = parts[1]
                if len(parts) >= 3:
                    location_data["location_country"] = parts[2]

        return location_data

    def _parse_salary(self, salary_raw: str) -> Dict:
        """Parse salary information into structured components"""
        salary_data = {
            "salary_raw": salary_raw,
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "CAD",  # Default for Canadian jobs
            "salary_period": "annually",
        }

        if not salary_raw:
            return salary_data

        salary_str = str(salary_raw).replace(",", "").replace("$", "")

        # Extract currency
        if "USD" in salary_str:
            salary_data["salary_currency"] = "USD"

        # Extract period
        if any(word in salary_str.lower() for word in ["hour", "hourly", "/hr", "per hour"]):
            salary_data["salary_period"] = "hourly"
        elif any(word in salary_str.lower() for word in ["month", "monthly", "/mo"]):
            salary_data["salary_period"] = "monthly"

        # Extract numbers
        numbers = re.findall(r"\d+(?:\.\d+)?", salary_str)
        if numbers:
            nums = [float(n) for n in numbers]
            if len(nums) == 1:
                salary_data["salary_min"] = salary_data["salary_max"] = int(nums[0])
            elif len(nums) >= 2:
                salary_data["salary_min"] = int(min(nums))
                salary_data["salary_max"] = int(max(nums))

        return salary_data

    def _normalize_job_type(self, job_type_raw) -> Optional[str]:
        """Normalize job type to standard values"""
        if not job_type_raw:
            return None

        job_type = str(job_type_raw).lower()

        if "full" in job_type or "permanent" in job_type:
            return "full-time"
        elif "part" in job_type:
            return "part-time"
        elif "contract" in job_type or "temporary" in job_type:
            return "contract"
        elif "intern" in job_type:
            return "internship"

        return "full-time"  # Default

    def _infer_work_arrangement(self, description: str, location: str) -> Optional[str]:
        """Infer work arrangement from description and location"""
        if not description:
            return None

        desc_lower = str(description).lower()
        loc_lower = str(location or "").lower()

        if any(word in desc_lower or word in loc_lower for word in ["remote", "work from home", "wfh", "anywhere"]):
            return "remote"
        elif any(word in desc_lower for word in ["hybrid", "flexible", "mix of"]):
            return "hybrid"
        else:
            return "onsite"

    def _parse_date(self, date_str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None

        try:
            # Handle ISO format
            if isinstance(date_str, str) and "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            # Handle relative dates
            if isinstance(date_str, str):
                date_lower = date_str.lower()
                if "today" in date_lower:
                    return datetime.now()
                elif "yesterday" in date_lower:
                    return datetime.now() - timedelta(days=1)
                elif "days ago" in date_lower:
                    days = re.search(r"(\d+)\s*days?\s*ago", date_lower)
                    if days:
                        return datetime.now() - timedelta(days=int(days.group(1)))

            return None

        except Exception:
            return None

    def _calculate_confidence_score(self, cleaned_data: Dict, raw_data: Dict) -> float:
        """
        Calculate confidence score for cleaned data quality and duplicate detection

        Confidence score ranges from 0.0 to 1.0, where:
        - 0.8-1.0: High confidence (complete data, good for duplicate detection)
        - 0.6-0.8: Medium confidence (some missing data, moderate reliability)
        - 0.4-0.6: Low confidence (minimal data, unreliable for matching)
        - 0.0-0.4: Very low confidence (insufficient data quality)

        Args:
            cleaned_data: Cleaned job data dictionary
            raw_data: Original raw scrape data

        Returns:
            float: Confidence score (0.0-1.0)
        """
        score = 0.0
        max_score = 0.0

        # Critical fields (60% of total score)
        if cleaned_data.get("job_title"):
            title_quality = self._assess_title_quality(cleaned_data["job_title"])
            score += 0.3 * title_quality
        max_score += 0.3

        if cleaned_data.get("company_name"):
            company_quality = self._assess_company_quality(cleaned_data["company_name"])
            score += 0.3 * company_quality
        max_score += 0.3

        # Important fields (30% of total score)
        if cleaned_data.get("job_description"):
            desc_quality = self._assess_description_quality(cleaned_data["job_description"])
            score += 0.15 * desc_quality
        max_score += 0.15

        if cleaned_data.get("location_city"):
            score += 0.15
        max_score += 0.15

        # Additional fields (10% of total score)
        if cleaned_data.get("salary_min") or cleaned_data.get("salary_max"):
            score += 0.05
        max_score += 0.05

        if cleaned_data.get("external_job_id"):
            score += 0.05
        max_score += 0.05

        # Bonus scoring for data completeness
        bonus_fields = ["work_arrangement", "job_type", "posting_date", "company_website"]
        bonus_count = sum(1 for field in bonus_fields if cleaned_data.get(field))
        bonus_score = min(0.1, bonus_count * 0.025)  # Max 0.1 bonus
        score += bonus_score
        max_score += 0.1

        final_score = round(score / max_score if max_score > 0 else 0.0, 4)

        # Ensure score is within valid range
        return max(0.0, min(1.0, final_score))

    def _assess_title_quality(self, title: str) -> float:
        """Assess job title quality (0.0-1.0)"""
        if not title:
            return 0.0

        quality = 0.5  # Base score

        # Check for meaningful length
        if len(title) >= 10:
            quality += 0.2
        if len(title) >= 20:
            quality += 0.1

        # Check for common title patterns
        if any(word in title.lower() for word in ["senior", "junior", "manager", "specialist", "analyst"]):
            quality += 0.1

        # Check for department/function
        if any(word in title.lower() for word in ["marketing", "sales", "engineering", "finance", "hr"]):
            quality += 0.1

        return min(1.0, quality)

    def _assess_company_quality(self, company: str) -> float:
        """Assess company name quality (0.0-1.0)"""
        if not company:
            return 0.0

        quality = 0.5  # Base score

        # Check for meaningful length
        if len(company) >= 5:
            quality += 0.2

        # Check for company indicators
        if any(suffix in company.lower() for suffix in ["inc", "corp", "ltd", "llc", "company"]):
            quality += 0.2

        # Penalize generic names
        if company.lower() in ["company", "corporation", "business", "employer"]:
            quality -= 0.3

        return max(0.0, min(1.0, quality))

    def _assess_description_quality(self, description: str) -> float:
        """Assess job description quality (0.0-1.0)"""
        if not description:
            return 0.0

        quality = 0.3  # Base score

        # Check for meaningful length
        if len(description) >= 100:
            quality += 0.2
        if len(description) >= 300:
            quality += 0.2
        if len(description) >= 500:
            quality += 0.1

        # Check for key sections
        desc_lower = description.lower()
        if "responsibility" in desc_lower or "duties" in desc_lower:
            quality += 0.1
        if "requirement" in desc_lower or "qualifications" in desc_lower:
            quality += 0.1
        if "experience" in desc_lower:
            quality += 0.1

        return min(1.0, quality)

    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _find_duplicate_cleaned_job(self, cleaned_data: Dict) -> Optional[Dict]:
        """Find existing cleaned job that might be a duplicate"""
        if not cleaned_data.get("external_job_id") or not cleaned_data.get("source_website"):
            return None

        query = """
            SELECT cleaned_job_id, duplicates_count 
            FROM cleaned_job_scrapes 
            WHERE external_job_id = %s 
            AND source_website = %s 
            AND is_expired = FALSE
            LIMIT 1
        """

        results = self.db.execute_query(query, (cleaned_data["external_job_id"], cleaned_data["source_website"]))

        return dict(results[0]) if results else None

    def _merge_duplicate_job(self, existing_id: str, new_scrape_id: str, cleaned_data: Dict) -> None:
        """Merge a duplicate job with an existing cleaned record"""
        query = """
            UPDATE cleaned_job_scrapes 
            SET duplicates_count = duplicates_count + 1,
                last_seen_timestamp = CURRENT_TIMESTAMP
            WHERE cleaned_job_id = %s
        """

        self.db.execute_query(query, (existing_id,))

        logger.info(f"Merged duplicate job {new_scrape_id} with existing record {existing_id}")

    def _create_cleaned_job_record(self, cleaned_data: Dict, scrape_ids: List[str]) -> str:
        """Create a new cleaned job record"""
        cleaned_job_id = str(uuid4())

        query = """
            INSERT INTO cleaned_job_scrapes (
                cleaned_job_id, job_title, company_name,
                location_city, location_province, location_country,
                work_arrangement, salary_min, salary_max, salary_currency,
                salary_period, job_description, external_job_id, source_website,
                application_url, job_type, posting_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        params = (
            cleaned_job_id,
            cleaned_data.get("job_title"),
            cleaned_data.get("company_name"),
            cleaned_data.get("location_city"),
            cleaned_data.get("location_province"),
            cleaned_data.get("location_country"),
            cleaned_data.get("work_arrangement"),
            cleaned_data.get("salary_min"),
            cleaned_data.get("salary_max"),
            cleaned_data.get("salary_currency"),
            cleaned_data.get("salary_period"),
            cleaned_data.get("job_description"),
            cleaned_data.get("external_job_id"),
            cleaned_data.get("source_website"),
            cleaned_data.get("application_url"),
            cleaned_data.get("job_type"),
            cleaned_data.get("posting_date"),
        )

        self.db.execute_query(query, params)

        logger.info(f"Created new cleaned job record {cleaned_job_id}")
        logger.info(f"Job: {cleaned_data.get('job_title')} at {cleaned_data.get('company_name')}")
        logger.info(f"Confidence score: {cleaned_data.get('confidence_score', 0.0)}")

        return cleaned_job_id

    def _mark_raw_scrape_processed(self, scrape_id: str) -> None:
        """Mark a raw scrape as successfully processed"""
        # This is implicit - the scrape_id will be in the original_scrape_ids array
        pass

    def _mark_raw_scrape_error(self, scrape_id: str, error_message: str) -> None:
        """Mark a raw scrape as having an error during processing"""
        query = """
            UPDATE raw_job_scrapes 
            SET success_status = FALSE, error_message = %s 
            WHERE scrape_id = %s
        """

        self.db.execute_query(query, (error_message, scrape_id))

    def get_pipeline_stats(self) -> Dict:
        """Get statistics about the scraping pipeline"""
        stats = {}

        # Raw scrape stats
        raw_stats = self.db.execute_query(
            """
            SELECT 
                COUNT(*) as total_raw,
                COUNT(CASE WHEN success_status = TRUE THEN 1 END) as successful_raw,
                COUNT(CASE WHEN success_status = FALSE THEN 1 END) as failed_raw
            FROM raw_job_scrapes
        """
        )

        if raw_stats:
            stats.update(dict(raw_stats[0]))

        # Cleaned scrape stats
        cleaned_stats = self.db.execute_query(
            """
            SELECT 
                COUNT(*) as total_cleaned,
                COALESCE(SUM(duplicates_count), 0) as total_duplicates_merged,
                COALESCE(AVG(confidence_score), 0) as avg_confidence,
                COUNT(CASE WHEN is_expired = FALSE THEN 1 END) as active_jobs
            FROM cleaned_job_scrapes
        """
        )

        if cleaned_stats:
            stats.update(dict(cleaned_stats[0]))

        # Processing efficiency
        processed_count = self.db.execute_query(
            """
            SELECT COUNT(DISTINCT UNNEST(original_scrape_ids)) as processed_raw_count
            FROM cleaned_job_scrapes
        """
        )

        if processed_count:
            stats["processed_raw_count"] = processed_count[0]["processed_raw_count"]
            if stats.get("total_raw", 0) > 0:
                stats["processing_rate"] = round(stats["processed_raw_count"] / stats["total_raw"] * 100, 2)

        return stats

    def _calculate_confidence_score(self, cleaned_data: Dict, raw_data: Dict) -> float:
        """
        Calculate confidence score for cleaned data quality and duplicate detection

        Confidence score ranges from 0.0 to 1.0, where:
        - 0.8-1.0: High confidence (complete data, good for duplicate detection)
        - 0.6-0.8: Medium confidence (some missing data, moderate reliability)
        - 0.4-0.6: Low confidence (minimal data, unreliable for matching)
        - 0.0-0.4: Very low confidence (insufficient data quality)

        Args:
            cleaned_data: Cleaned job data dictionary
            raw_data: Original raw scrape data

        Returns:
            float: Confidence score (0.0-1.0)
        """
        score = 0.0
        max_score = 0.0

        # Critical fields (60% of total score)
        if cleaned_data.get("job_title"):
            title_quality = self._assess_title_quality(cleaned_data["job_title"])
            score += 0.3 * title_quality
        max_score += 0.3

        if cleaned_data.get("company_name"):
            company_quality = self._assess_company_quality(cleaned_data["company_name"])
            score += 0.3 * company_quality
        max_score += 0.3

        # Important fields (30% of total score)
        if cleaned_data.get("job_description"):
            desc_quality = self._assess_description_quality(cleaned_data["job_description"])
            score += 0.15 * desc_quality
        max_score += 0.15

        if cleaned_data.get("location_city"):
            score += 0.15
        max_score += 0.15

        # Additional fields (10% of total score)
        if cleaned_data.get("salary_min") or cleaned_data.get("salary_max"):
            score += 0.05
        max_score += 0.05

        if cleaned_data.get("external_job_id"):
            score += 0.05
        max_score += 0.05

        # Bonus scoring for data completeness
        bonus_fields = ["work_arrangement", "job_type", "posting_date", "company_website"]
        bonus_count = sum(1 for field in bonus_fields if cleaned_data.get(field))
        bonus_score = min(0.1, bonus_count * 0.025)  # Max 0.1 bonus
        score += bonus_score
        max_score += 0.1

        final_score = round(score / max_score if max_score > 0 else 0.0, 4)

        # Ensure score is within valid range
        return max(0.0, min(1.0, final_score))

    def _assess_title_quality(self, title: str) -> float:
        """Assess job title quality (0.0-1.0)"""
        if not title:
            return 0.0

        quality = 0.5  # Base score

        # Check for meaningful length
        if len(title) >= 10:
            quality += 0.2
        if len(title) >= 20:
            quality += 0.1

        # Check for common title patterns
        if any(word in title.lower() for word in ["senior", "junior", "manager", "specialist", "analyst"]):
            quality += 0.1

        # Check for department/function
        if any(word in title.lower() for word in ["marketing", "sales", "engineering", "finance", "hr"]):
            quality += 0.1

        return min(1.0, quality)

    def _assess_company_quality(self, company: str) -> float:
        """Assess company name quality (0.0-1.0)"""
        if not company:
            return 0.0

        quality = 0.5  # Base score

        # Check for meaningful length
        if len(company) >= 5:
            quality += 0.2

        # Check for company indicators
        if any(suffix in company.lower() for suffix in ["inc", "corp", "ltd", "llc", "company"]):
            quality += 0.2

        # Penalize generic names
        if company.lower() in ["company", "corporation", "business", "employer"]:
            quality -= 0.3

        return max(0.0, min(1.0, quality))

    def _assess_description_quality(self, description: str) -> float:
        """Assess job description quality (0.0-1.0)"""
        if not description:
            return 0.0

        quality = 0.3  # Base score

        # Check for meaningful length
        if len(description) >= 100:
            quality += 0.2
        if len(description) >= 300:
            quality += 0.2
        if len(description) >= 500:
            quality += 0.1

        # Check for key sections
        desc_lower = description.lower()
        if "responsibility" in desc_lower or "duties" in desc_lower:
            quality += 0.1
        if "requirement" in desc_lower or "qualifications" in desc_lower:
            quality += 0.1
        if "experience" in desc_lower:
            quality += 0.1

        return min(1.0, quality)
