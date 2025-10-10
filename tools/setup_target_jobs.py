#!/usr/bin/env python3
"""
Target Job Folder Setup Tool

Reads user's job search preferences from database and creates organized
folder structure for each target job title. Prepares workspace for
professional writing agent to generate job-specific seed sentences.

Author: Automated Job Application System
Version: 1.0.0
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.database.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TargetJobSetup:
    """
    Sets up folder structure for target job positions based on user preferences
    """

    def __init__(self, user_id: str = 'steve_glen'):
        """
        Initialize setup tool

        Args:
            user_id: User identifier (default: steve_glen)
        """
        self.user_id = user_id
        self.db = DatabaseManager()
        self.base_path = Path('user_content/target_jobs')
        self.source_path = Path('user_content/source_materials')

        # Ensure base directories exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.source_path.mkdir(parents=True, exist_ok=True)

    def get_user_target_jobs(self) -> List[Dict]:
        """
        Retrieve user's target job titles from database

        Returns:
            List of target job dictionaries with preferences
        """

        # Query user's job search preferences
        query = """
            SELECT DISTINCT
                jsp.job_title_target,
                jsp.industry_preference,
                jsp.salary_minimum,
                jsp.salary_maximum,
                jsp.work_arrangement_preference,
                jsp.location_preference,
                jsp.package_name,
                jsp.is_active
            FROM user_job_search_preferences jsp
            JOIN users u ON jsp.user_id = u.id
            WHERE u.email = %s
                AND jsp.is_active = TRUE
            ORDER BY jsp.job_title_target
        """

        try:
            results = self.db.execute_query(query, (self.user_id,))

            target_jobs = []
            for row in results:
                target_jobs.append({
                    'job_title': row[0],
                    'industry': row[1],
                    'salary_min': row[2],
                    'salary_max': row[3],
                    'work_arrangement': row[4],
                    'location': row[5],
                    'package_name': row[6],
                    'is_active': row[7]
                })

            logger.info(f"Found {len(target_jobs)} active target jobs for {self.user_id}")
            return target_jobs

        except Exception as e:
            logger.error(f"Error querying target jobs: {str(e)}")
            # Return default target jobs if database query fails
            return self._get_default_target_jobs()

    def _get_default_target_jobs(self) -> List[Dict]:
        """
        Provide default target jobs if database unavailable

        Returns:
            List of default target job configurations
        """

        logger.warning("Using default target jobs")

        return [
            {
                'job_title': 'Marketing Automation Manager',
                'industry': 'Marketing',
                'salary_min': 85000,
                'salary_max': 120000,
                'work_arrangement': 'hybrid',
                'location': 'Alberta, Canada',
                'package_name': 'regional_alberta',
                'is_active': True
            },
            {
                'job_title': 'Marketing Manager',
                'industry': 'Marketing',
                'salary_min': 75000,
                'salary_max': 110000,
                'work_arrangement': 'hybrid',
                'location': 'Edmonton, Alberta',
                'package_name': 'local_edmonton',
                'is_active': True
            },
            {
                'job_title': 'Digital Marketing Manager',
                'industry': 'Digital Marketing',
                'salary_min': 75000,
                'salary_max': 110000,
                'work_arrangement': 'remote',
                'location': 'Canada (Remote)',
                'package_name': 'remote_canada',
                'is_active': True
            }
        ]

    def create_job_folders(self, target_jobs: List[Dict]) -> Dict:
        """
        Create folder structure for each target job

        Args:
            target_jobs: List of target job dictionaries

        Returns:
            Summary of created folders
        """

        created_folders = []
        existing_folders = []

        for job in target_jobs:
            job_title = job['job_title']

            # Sanitize job title for folder name
            folder_name = self._sanitize_folder_name(job_title)
            job_folder = self.base_path / folder_name

            # Create folder structure
            if job_folder.exists():
                logger.info(f"Folder already exists: {folder_name}")
                existing_folders.append(str(job_folder))
            else:
                job_folder.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created folder: {folder_name}")
                created_folders.append(str(job_folder))

            # Create subfolders
            (job_folder / 'seed_sentences').mkdir(exist_ok=True)
            (job_folder / 'generated_variations').mkdir(exist_ok=True)
            (job_folder / 'reframed_context').mkdir(exist_ok=True)

            # Create job configuration file
            self._create_job_config(job_folder, job)

            # Create README
            self._create_readme(job_folder, job)

        return {
            'total_jobs': len(target_jobs),
            'created': len(created_folders),
            'existing': len(existing_folders),
            'created_paths': created_folders,
            'existing_paths': existing_folders
        }

    def _sanitize_folder_name(self, job_title: str) -> str:
        """
        Convert job title to safe folder name

        Args:
            job_title: Raw job title

        Returns:
            Sanitized folder name
        """

        # Convert to lowercase, replace spaces with hyphens
        folder_name = job_title.lower()
        folder_name = folder_name.replace(' ', '-')
        folder_name = folder_name.replace('/', '-')

        # Remove special characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789-_')
        folder_name = ''.join(c for c in folder_name if c in allowed_chars)

        return folder_name

    def _create_job_config(self, job_folder: Path, job: Dict):
        """
        Create job configuration JSON file

        Args:
            job_folder: Path to job folder
            job: Job configuration dictionary
        """

        config_file = job_folder / 'job_config.json'

        config = {
            'job_title': job['job_title'],
            'industry': job['industry'],
            'salary_range': {
                'minimum': job['salary_min'],
                'maximum': job['salary_max']
            },
            'work_arrangement': job['work_arrangement'],
            'location': job['location'],
            'package_name': job['package_name'],
            'is_active': job['is_active'],
            'created_date': str(Path(job_folder).stat().st_ctime) if job_folder.exists() else None
        }

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logger.debug(f"Created config: {config_file}")

    def _create_readme(self, job_folder: Path, job: Dict):
        """
        Create README file for job folder

        Args:
            job_folder: Path to job folder
            job: Job configuration dictionary
        """

        readme_file = job_folder / 'README.md'

        content = f"""# {job['job_title']}

## Job Configuration

- **Industry**: {job['industry']}
- **Salary Range**: ${job['salary_min']:,} - ${job['salary_max']:,}
- **Work Arrangement**: {job['work_arrangement']}
- **Location**: {job['location']}
- **Preference Package**: {job['package_name']}

## Folder Structure

### `seed_sentences/`
Contains original seed sentences generated by the professional writing agent.
These are high-quality, job-specific sentences crafted from user's background materials.

### `generated_variations/`
Contains variations generated from seed sentences using Gemini API.
Each seed produces 5-10 variations with different lengths and styles.

### `reframed_context/`
Contains user's experiences and achievements reframed specifically for this job title.
This context helps the writing agent understand how to position the candidate.

## Workflow

1. **Reframing**: Agent analyzes user source materials and reframes for {job['job_title']}
2. **Seed Generation**: Professional writing agent creates 15-20 seed sentences
3. **Variation**: Gemini generates variations (5-10 per seed)
4. **Evaluation**: 5-stage pipeline evaluates all variations
5. **Selection**: Approved sentences ready for document generation

## Usage

To generate seeds for this job:
```
/generate-seeds {job['job_title']}
```

To generate variations:
```python
python -m modules.content.sentence_variation_generator \\
    --seeds seed_sentences/seeds.json \\
    --output generated_variations/
```
"""

        with open(readme_file, 'w') as f:
            f.write(content)

        logger.debug(f"Created README: {readme_file}")

    def create_source_materials_readme(self):
        """
        Create README for source materials folder
        """

        readme_file = self.source_path / 'README.md'

        content = """# User Source Materials

## Purpose

This folder contains your personal background materials that the professional writing agent uses to generate job-specific seed sentences.

## What to Include

Drop any of these files here:

### Career Documents
- Resume/CV (current version)
- Previous resumes for different roles
- LinkedIn profile export
- Portfolio or work samples descriptions

### Experience Details
- Detailed job descriptions from past roles
- Project summaries and outcomes
- Achievement lists with metrics
- Performance review excerpts (sanitized)

### Credentials
- Certifications and licenses
- Academic transcripts or degree information
- Training completion certificates
- Professional development records

### Skills Documentation
- Technical skills inventory
- Software proficiencies
- Language skills
- Specialized knowledge areas

### Personal Branding
- Personal mission statement
- Career goals and aspirations
- Values and work preferences
- Professional bio or summary

## File Formats

Accepted formats:
- Text files (.txt, .md)
- PDF documents (.pdf)
- Word documents (.docx)
- Plain text formats preferred for best parsing

## Privacy and Security

- These files are LOCAL ONLY
- Never committed to version control (in .gitignore)
- Used only by the writing agent during seed generation
- Not sent to external services (except reframed excerpts to Gemini for variation)

## Organization Tips

Consider organizing by:
- `resume_current.pdf`
- `work_history_odvod.md`
- `achievements_2020-2025.txt`
- `certifications.md`
- `personal_statement.txt`

## How It's Used

1. **Intake**: Writing agent reads ALL files in this folder
2. **Analysis**: Extracts achievements, skills, metrics, unique differentiators
3. **Reframing**: For each target job, reframes experiences appropriately
4. **Generation**: Creates factually accurate, compelling seed sentences
5. **Verification**: All generated content traceable back to source materials

---

**Ready to Start?** Drop your files here and run `/generate-seeds`
"""

        with open(readme_file, 'w') as f:
            f.write(content)

        logger.info(f"Created source materials README: {readme_file}")


def main():
    """
    Main execution function
    """

    print("=" * 60)
    print("TARGET JOB FOLDER SETUP")
    print("=" * 60)
    print()

    setup = TargetJobSetup()

    # Get target jobs from database
    print("Fetching target jobs from database...")
    target_jobs = setup.get_user_target_jobs()

    print(f"\nFound {len(target_jobs)} target job(s):")
    for job in target_jobs:
        print(f"  - {job['job_title']} ({job['package_name']})")

    # Create folder structure
    print("\nCreating folder structure...")
    result = setup.create_job_folders(target_jobs)

    print(f"\n✓ Setup complete!")
    print(f"  - Total jobs: {result['total_jobs']}")
    print(f"  - New folders: {result['created']}")
    print(f"  - Existing folders: {result['existing']}")

    # Create source materials README
    print("\nCreating source materials documentation...")
    setup.create_source_materials_readme()

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. Add your background materials to:")
    print("   user_content/source_materials/")
    print("\n2. Generate seed sentences with:")
    print("   /generate-seeds <job_title>")
    print("\n3. Review folders created at:")
    print("   user_content/target_jobs/")
    print()


if __name__ == "__main__":
    main()
