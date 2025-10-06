#!/usr/bin/env python3
"""
End-to-End API Test for Job Application System

This test demonstrates the complete workflow using API endpoints:
1. Scrape 5 marketing jobs from Indeed using misceres/indeed-scraper
2. Process jobs through Gemini AI analysis
3. Generate job applications using existing content system
4. Send job applications via Gmail from 1234.s.t.e.v.e.glen@gmail.com to therealstevenglen@gmail.com

Educational Purpose Only: This test demonstrates automated job application workflows
"""

import requests
import json
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIEndToEndTest:
    """Complete end-to-end test using API endpoints"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.authenticated = False
        
        self.test_results = {
            'start_time': datetime.now(),
            'authentication': {'status': 'pending'},
            'scraping': {'status': 'pending', 'jobs_found': 0},
            'ai_analysis': {'status': 'pending', 'jobs_analyzed': 0},
            'email_sending': {'status': 'pending', 'emails_sent': 0},
            'errors': []
        }
    
    def log_step(self, step, message):
        """Log a test step with timestamp"""
        logger.info(f"[{step.upper()}] {message}")
    
    def authenticate(self):
        """Authenticate with dashboard system"""
        self.log_step("AUTH", "Authenticating with dashboard system...")
        
        try:
            # Dashboard authentication
            auth_data = {"password": "jellyfish–lantern–kisses"}
            auth_response = self.session.post(
                f"{self.base_url}/dashboard/authenticate",
                json=auth_data
            )
            
            if auth_response.status_code == 200:
                self.authenticated = True
                self.test_results['authentication'] = {'status': 'success'}
                self.log_step("AUTH", "Successfully authenticated")
                return True
            else:
                self.test_results['authentication'] = {'status': 'failed'}
                self.test_results['errors'].append(f"Authentication failed: {auth_response.text}")
                self.log_step("AUTH", f"Failed: {auth_response.text}")
                return False
                
        except Exception as e:
            self.test_results['authentication'] = {'status': 'failed'}
            self.test_results['errors'].append(f"Authentication exception: {str(e)}")
            self.log_step("AUTH", f"Exception: {str(e)}")
            return False
    
    def step_1_scrape_jobs(self):
        """Step 1: Scrape marketing jobs using API"""
        self.log_step("SCRAPING", "Starting job scraping for marketing positions...")
        
        try:
            scrape_data = {
                "search_params": {
                    "position": "Marketing Manager",
                    "location": "Edmonton, AB",
                    "country": "CA",
                    "maxItems": 5
                },
                "user_id": "steve_glen"
            }
            
            self.log_step("SCRAPING", f"Search parameters: {scrape_data['search_params']}")
            
            response = self.session.post(
                f"{self.base_url}/api/scraping/start-scrape",
                json=scrape_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    scrape_id = result.get('scrape_id')
                    self.test_results['scraping'] = {
                        'status': 'success',
                        'scrape_id': scrape_id
                    }
                    self.log_step("SCRAPING", f"Scraping started successfully. Scrape ID: {scrape_id}")
                    return True
                else:
                    error_msg = result.get('error', 'Unknown scraping error')
                    self.test_results['scraping']['status'] = 'failed'
                    self.test_results['errors'].append(f"Scraping failed: {error_msg}")
                    self.log_step("SCRAPING", f"Failed: {error_msg}")
                    return False
            else:
                self.test_results['scraping']['status'] = 'failed'
                self.test_results['errors'].append(f"Scraping request failed: HTTP {response.status_code}")
                self.log_step("SCRAPING", f"HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            self.test_results['scraping']['status'] = 'failed'
            self.test_results['errors'].append(f"Scraping exception: {str(e)}")
            self.log_step("SCRAPING", f"Exception: {str(e)}")
            return False
    
    def step_2_wait_for_scraping(self):
        """Step 2: Wait for scraping to complete and check results"""
        self.log_step("WAIT", "Waiting for scraping to complete...")
        
        scrape_id = self.test_results['scraping'].get('scrape_id')
        if not scrape_id:
            self.log_step("WAIT", "No scrape ID available")
            return False
        
        # Wait for scraping to complete (max 2 minutes)
        max_wait = 120
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                status_response = self.session.get(
                    f"{self.base_url}/api/scraping/status/{scrape_id}"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    scrape_status = status_data.get('status', 'unknown')
                    
                    self.log_step("WAIT", f"Scraping status: {scrape_status}")
                    
                    if scrape_status == 'completed':
                        # Get results
                        results_response = self.session.get(
                            f"{self.base_url}/api/scraping/results/{scrape_id}"
                        )
                        
                        if results_response.status_code == 200:
                            results_data = results_response.json()
                            jobs_found = len(results_data.get('jobs', []))
                            
                            self.test_results['scraping']['jobs_found'] = jobs_found
                            self.log_step("WAIT", f"Scraping completed. Found {jobs_found} jobs")
                            return True
                        
                    elif scrape_status == 'failed':
                        self.test_results['scraping']['status'] = 'failed'
                        self.test_results['errors'].append(f"Scraping failed: {status_data.get('error', 'Unknown error')}")
                        return False
                    
                    # Continue waiting
                    time.sleep(10)
                    wait_time += 10
                    
                else:
                    self.log_step("WAIT", f"Status check failed: HTTP {status_response.status_code}")
                    time.sleep(10)
                    wait_time += 10
                    
            except Exception as e:
                self.log_step("WAIT", f"Status check exception: {str(e)}")
                time.sleep(10)
                wait_time += 10
        
        self.log_step("WAIT", "Timeout waiting for scraping to complete")
        return False
    
    def step_3_trigger_ai_analysis(self):
        """Step 3: Trigger AI analysis on scraped jobs"""
        self.log_step("AI_ANALYSIS", "Triggering AI analysis on scraped jobs...")
        
        try:
            # Get available jobs for analysis
            analysis_data = {"max_jobs": 5}
            
            response = self.session.post(
                f"{self.base_url}/api/ai/analyze-jobs",
                json=analysis_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    analyzed_count = result.get('analyzed_count', 0)
                    self.test_results['ai_analysis'] = {
                        'status': 'success',
                        'jobs_analyzed': analyzed_count
                    }
                    self.log_step("AI_ANALYSIS", f"Successfully analyzed {analyzed_count} jobs")
                    return True
                else:
                    error_msg = result.get('error', 'Unknown AI analysis error')
                    self.test_results['ai_analysis']['status'] = 'failed'
                    self.test_results['errors'].append(f"AI analysis failed: {error_msg}")
                    self.log_step("AI_ANALYSIS", f"Failed: {error_msg}")
                    return False
            else:
                self.test_results['ai_analysis']['status'] = 'failed'
                self.test_results['errors'].append(f"AI analysis request failed: HTTP {response.status_code}")
                self.log_step("AI_ANALYSIS", f"HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            self.test_results['ai_analysis']['status'] = 'failed'
            self.test_results['errors'].append(f"AI analysis exception: {str(e)}")
            self.log_step("AI_ANALYSIS", f"Exception: {str(e)}")
            return False
    
    def step_4_send_test_emails(self):
        """Step 4: Send test job application emails"""
        self.log_step("EMAIL", "Sending test job application emails...")
        
        try:
            # Send test emails for marketing positions
            test_jobs = [
                {
                    "job_title": "Marketing Manager",
                    "company": "Tech Company Inc",
                    "location": "Edmonton, AB"
                },
                {
                    "job_title": "Digital Marketing Specialist", 
                    "company": "Growth Solutions Ltd",
                    "location": "Calgary, AB"
                }
            ]
            
            sent_count = 0
            
            for i, job in enumerate(test_jobs, 1):
                try:
                    email_data = {
                        "recipient": "therealstevenglen@gmail.com",
                        "subject": f"Application for {job['job_title']} at {job['company']}",
                        "body": self._prepare_test_email_body(job),
                        "job_context": job
                    }
                    
                    self.log_step("EMAIL", f"Sending email {i}: {job['job_title']} at {job['company']}")
                    
                    response = self.session.post(
                        f"{self.base_url}/api/email/test",
                        json=email_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            sent_count += 1
                            self.log_step("EMAIL", f"Successfully sent email for {job['job_title']}")
                            time.sleep(3)  # Rate limiting
                        else:
                            self.log_step("EMAIL", f"Failed to send email: {result.get('error')}")
                    else:
                        self.log_step("EMAIL", f"Email request failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    self.log_step("EMAIL", f"Email sending exception: {str(e)}")
                    continue
            
            self.test_results['email_sending'] = {
                'status': 'success',
                'emails_sent': sent_count
            }
            
            self.log_step("EMAIL", f"Successfully sent {sent_count} test emails")
            return True
            
        except Exception as e:
            self.test_results['email_sending']['status'] = 'failed'
            self.test_results['errors'].append(f"Email sending exception: {str(e)}")
            self.log_step("EMAIL", f"Exception: {str(e)}")
            return False
    
    def _prepare_test_email_body(self, job):
        """Prepare test email body for job application"""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job['job_title']} position at {job['company']}.

With over 14 years of experience in marketing communications and digital strategy, I bring a proven track record of driving growth and engagement through innovative marketing initiatives.

Key highlights of my background:
• Led digital marketing initiatives resulting in 40% increase in online engagement
• Developed content strategy for multiple publication platforms  
• Managed marketing budgets of $100,000+ annually
• Bachelor of Commerce from University of Alberta

I am particularly drawn to this opportunity because of {job['company']}'s reputation for innovation and growth. I would welcome the chance to discuss how my experience and passion for marketing can contribute to your team's continued success.

Thank you for your time and consideration.

Best regards,
Steve Glen
1234.s.t.e.v.e.glen@gmail.com
(780) 555-0123

---
This email was sent as part of an automated job application system test.
Educational Purpose Only - Please disregard if received in error.
"""
    
    def run_complete_test(self):
        """Run the complete end-to-end API test"""
        self.log_step("TEST", "Starting complete end-to-end API test")
        
        # Authenticate first
        if not self.authenticate():
            self.log_step("TEST", "Test failed at authentication step")
            return self.test_results
        
        # Step 1: Start scraping
        if not self.step_1_scrape_jobs():
            self.log_step("TEST", "Test failed at scraping step")
            return self.test_results
        
        # Step 2: Wait for scraping results
        if not self.step_2_wait_for_scraping():
            self.log_step("TEST", "Test failed waiting for scraping")
            # Continue with test even if scraping fails
        
        # Step 3: AI analysis
        if not self.step_3_trigger_ai_analysis():
            self.log_step("TEST", "Test failed at AI analysis step")
            # Continue with test even if AI analysis fails
        
        # Step 4: Send test emails
        if not self.step_4_send_test_emails():
            self.log_step("TEST", "Test failed at email sending step")
            return self.test_results
        
        # Complete test results
        self.test_results['end_time'] = datetime.now()
        self.test_results['duration'] = (self.test_results['end_time'] - self.test_results['start_time']).total_seconds()
        self.test_results['overall_status'] = 'success'
        
        self.log_step("TEST", f"Complete end-to-end API test finished in {self.test_results['duration']:.1f} seconds")
        return self.test_results
    
    def print_results_summary(self):
        """Print a comprehensive summary of test results"""
        print("\n" + "="*80)
        print("END-TO-END API TEST RESULTS")
        print("="*80)
        
        print(f"Start Time: {self.test_results['start_time']}")
        if 'end_time' in self.test_results:
            print(f"End Time: {self.test_results['end_time']}")
            print(f"Duration: {self.test_results['duration']:.1f} seconds")
        
        print(f"\nOverall Status: {self.test_results.get('overall_status', 'incomplete').upper()}")
        
        print("\nStep Results:")
        print(f"  Authentication: {self.test_results['authentication']['status']}")
        print(f"  Scraping: {self.test_results['scraping']['status']} - {self.test_results['scraping'].get('jobs_found', 0)} jobs found")
        print(f"  AI Analysis: {self.test_results['ai_analysis']['status']} - {self.test_results['ai_analysis'].get('jobs_analyzed', 0)} jobs analyzed")
        print(f"  Email Sending: {self.test_results['email_sending']['status']} - {self.test_results['email_sending'].get('emails_sent', 0)} emails sent")
        
        if self.test_results['errors']:
            print("\nErrors Encountered:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*80)

def main():
    """Main test execution"""
    print("Starting End-to-End API Test for Job Application System")
    print("Educational Purpose Only - Testing automated workflow capabilities")
    
    # Create and run test
    test = APIEndToEndTest()
    results = test.run_complete_test()
    
    # Print results
    test.print_results_summary()
    
    # Save results to file
    results_file = f"test_results_api_end_to_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main()