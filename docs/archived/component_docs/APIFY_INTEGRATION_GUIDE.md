# Apify Indeed Scraper Integration Guide

## Overview

This guide walks you through integrating the **misceres/indeed-scraper** from Apify into your automated job application system. This integration enables real job data collection from Indeed.com to feed your LLM analysis and application generation pipeline.

## Prerequisites

### 1. Apify Account Setup

**Step 1**: Create Apify Account
- Go to [apify.com](https://apify.com)
- Sign up for a free account
- Verify your email address

**Step 2**: Get API Token
- Log into Apify Console
- Go to Settings → Integrations
- Copy your API token (starts with `apify_api_...`)

**Step 3**: Add Token to Environment
```bash
# In your Replit project, add this secret:
APIFY_TOKEN=your_api_token_here
```

### 2. Install Dependencies

The required packages are already installed in your project:
- `requests` - For API calls to Apify
- `python-docx` - For document generation (already installed)

## Integration Steps

### Step 1: Environment Setup

Add your Apify token to Replit Secrets:
1. Click the lock icon in the left sidebar
2. Add new secret: `APIFY_TOKEN`
3. Paste your API token value

### Step 2: Test the Integration

Create a test script to verify the connection:

```python
# test_apify_integration.py
from modules.job_scraper_apify import ApifyJobScraper

def test_apify_connection():
    """Test Apify API connection"""
    try:
        scraper = ApifyJobScraper()
        print("✓ Apify connection successful")
        
        # Test scraping a few jobs
        search_configs = [{
            'job_title': 'Marketing Manager',
            'location': 'Edmonton, AB',
            'country': 'CA'
        }]
        
        jobs = scraper.scrape_jobs(search_configs)
        print(f"✓ Successfully scraped {len(jobs)} jobs")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_apify_connection()
```

### Step 3: Add Scraper Endpoint

Add a new endpoint to trigger job scraping:

```python
# In app_modular.py, add this route:

@app.route('/api/scrape-jobs', methods=['POST'])
def scrape_jobs_endpoint():
    """
    Endpoint to trigger job scraping
    """
    try:
        data = request.get_json()
        job_title = data.get('job_title', 'Marketing Manager')
        location = data.get('location', 'Edmonton, AB')
        max_jobs = data.get('max_jobs', 50)
        
        from modules.job_scraper_apify import scrape_indeed_jobs
        
        jobs = scrape_indeed_jobs(job_title, location)
        
        return jsonify({
            'success': True,
            'jobs_scraped': len(jobs),
            'message': f'Successfully scraped {len(jobs)} jobs'
        })
        
    except Exception as e:
        logger.error(f"Error scraping jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### Step 4: Update Dashboard

The dashboard now includes monthly job counts and notifications. When you reach 3000 jobs in a month, you'll see an alert suggesting the memo23 scraper for better value.

## Usage Examples

### Basic Job Scraping

```python
from modules.job_scraper_apify import ApifyJobScraper

# Initialize scraper
scraper = ApifyJobScraper()

# Define search criteria
search_configs = [
    {
        'job_title': 'Marketing Manager',
        'location': 'Edmonton, AB',
        'country': 'CA'
    },
    {
        'job_title': 'Digital Marketing Specialist',
        'location': 'Calgary, AB',
        'country': 'CA'
    }
]

# Scrape jobs
jobs = scraper.scrape_jobs(search_configs)

# Save to database
saved_count = scraper.save_jobs_to_database(jobs)
print(f"Saved {saved_count} new jobs to database")
```

### Automated Workflow Integration

```python
# Example: Daily job scraping workflow
from modules.job_scraper_apify import ApifyJobScraper
from modules.job_application_system import JobApplicationSystem

def daily_job_processing():
    """Complete daily job processing workflow"""
    
    # 1. Scrape new jobs
    scraper = ApifyJobScraper()
    search_configs = [
        {'job_title': 'Marketing Manager', 'location': 'Edmonton, AB'},
        {'job_title': 'Marketing Coordinator', 'location': 'Edmonton, AB'},
        {'job_title': 'Digital Marketing', 'location': 'Alberta, CA'}
    ]
    
    jobs = scraper.scrape_jobs(search_configs)
    scraper.save_jobs_to_database(jobs)
    
    # 2. Process with AI system
    app_system = JobApplicationSystem()
    
    for job in jobs:
        # Check eligibility
        if app_system.check_job_eligibility(job['job_id']):
            # Generate application
            app_system.generate_application_package(job['job_id'])
```

## Data Flow

1. **Search Configuration**: Define job titles and locations
2. **Apify API Call**: Send request to misceres/indeed-scraper
3. **Data Processing**: Transform raw Indeed data to your database format
4. **Database Storage**: Save jobs with status tracking
5. **AI Analysis**: Feed jobs to LLM for eligibility checking
6. **Application Generation**: Create personalized resumes/cover letters

## Cost Management

### Current Pricing (misceres/indeed-scraper)
- **Cost**: $5 per 1,000 results
- **No monthly fee**: Pay only for what you use
- **Includes proxies**: No additional proxy costs

### Monthly Usage Tracking
The system tracks your monthly usage and shows notifications:
- **Under 3,000 jobs/month**: Continue with misceres (most cost-effective)
- **Over 3,000 jobs/month**: Consider upgrading to memo23 for better value

### Optimization Tips
1. **Targeted Searches**: Use specific job titles and locations
2. **Duplicate Prevention**: The scraper automatically prevents duplicate jobs
3. **Batch Processing**: Process multiple searches in single API calls
4. **Rate Limiting**: Apify handles rate limiting automatically

## Troubleshooting

### Common Issues

**Error: "APIFY_TOKEN environment variable is required"**
- Solution: Add your Apify API token to Replit Secrets

**Error: "Failed to start scraping run"**
- Check your API token is valid
- Verify your Apify account has sufficient credits
- Check the search URL format

**No jobs returned**
- Verify the job title and location exist on Indeed
- Try broader search terms
- Check Indeed.ca directly for comparison

**Timeout errors**
- Increase `max_wait_minutes` parameter
- Split large searches into smaller batches
- Check Apify status page for service issues

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support Resources

1. **Apify Documentation**: [docs.apify.com](https://docs.apify.com)
2. **Misceres Scraper**: [apify.com/misceres/indeed-scraper](https://apify.com/misceres/indeed-scraper)
3. **API Reference**: Built into the scraper code
4. **Community Support**: Apify Discord/Forums

## Next Steps

After successful integration:

1. **Test with Sample Data**: Run a few test scrapes
2. **Set Up Automation**: Create scheduled workflows
3. **Monitor Usage**: Watch monthly costs via dashboard
4. **Scale Gradually**: Start with targeted searches, expand as needed
5. **Optimize Searches**: Refine job titles and locations based on results

## Security Notes

- Never commit API tokens to version control
- Use Replit Secrets for all sensitive credentials
- Monitor API usage to prevent unexpected charges
- Set up billing alerts in your Apify account

## Sample Output

The scraper returns jobs in this format:
```json
{
  "job_id": "unique_indeed_id",
  "title": "Marketing Manager",
  "company": "Company Name",
  "location": "Edmonton, AB",
  "description": "Full job description...",
  "salary_low": 65000,
  "salary_high": 85000,
  "job_type": "Full-time",
  "posted_date": "2025-07-04",
  "apply_url": "https://indeed.com/apply/...",
  "company_rating": 4.2,
  "remote_work": "hybrid",
  "source": "indeed",
  "raw_data": "{...}"
}
```

This data feeds directly into your LLM analysis and eligibility checking system.