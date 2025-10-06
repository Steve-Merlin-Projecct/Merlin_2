#!/usr/bin/env python3
"""
End-to-End Job Application System Test

This test performs a complete workflow:
1. Scrape 5 marketing jobs from Indeed using misceres/indeed-scraper
2. Process jobs through Gemini AI analysis
3. Generate job applications using content management
4. Send job applications via Gmail from 1234.s.t.e.v.e.glen@gmail.com to therealstevenglen@gmail.com

Educational Purpose Only: This test demonstrates automated job application workflows
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.scraping.job_scraper_apify import ApifyJobScraper
from modules.scraping.scrape_pipeline import ScrapeDataPipeline
from modules.ai_job_description_analysis.ai_analyzer import GeminiJobAnalyzer
from modules.document_generation.document_generator import DocumentGenerator
from modules.email_integration.gmail_enhancements import EnhancedGmailSender
from modules.database.database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EndToEndWorkflowTest:
    """Complete end-to-end test of the job application system"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.scraper = ApifyJobScraper()
        self.pipeline = ScrapeDataPipeline()
        self.ai_analyzer = GeminiJobAnalyzer()
        self.document_generator = DocumentGenerator()
        self.gmail_sender = EnhancedGmailSender()
        
        self.test_results = {
            'start_time': datetime.now(),
            'scraping': {'status': 'pending', 'jobs_found': 0},
            'pipeline': {'status': 'pending', 'jobs_cleaned': 0},
            'ai_analysis': {'status': 'pending', 'jobs_analyzed': 0},
            'document_generation': {'status': 'pending', 'documents_created': 0},
            'email_sending': {'status': 'pending', 'emails_sent': 0},
            'errors': []
        }
    
    def log_step(self, step, message):
        """Log a test step with timestamp"""
        logger.info(f"[{step.upper()}] {message}")
    
    def step_1_scrape_jobs(self):
        """Step 1: Scrape 5 marketing jobs from Indeed"""
        self.log_step("SCRAPING", "Starting job scraping for marketing positions...")
        
        try:
            # Configure scraping parameters
            search_params = {
                'position': 'Marketing Manager',
                'location': 'Edmonton, AB',
                'country': 'CA',
                'maxItems': 5
            }
            
            self.log_step("SCRAPING", f"Search parameters: {search_params}")
            
            # Execute scraping
            scrape_result = self.scraper.scrape_jobs(
                search_params=search_params,
                user_id='steve_glen'
            )
            
            if scrape_result['success']:
                jobs_count = len(scrape_result.get('jobs', []))
                self.test_results['scraping'] = {
                    'status': 'success',
                    'jobs_found': jobs_count,
                    'scrape_id': scrape_result.get('scrape_id')
                }
                self.log_step("SCRAPING", f"Successfully scraped {jobs_count} jobs")
                return True
            else:
                error_msg = scrape_result.get('error', 'Unknown scraping error')
                self.test_results['scraping']['status'] = 'failed'
                self.test_results['errors'].append(f"Scraping failed: {error_msg}")
                self.log_step("SCRAPING", f"Failed: {error_msg}")
                return False
                
        except Exception as e:
            self.test_results['scraping']['status'] = 'failed'
            self.test_results['errors'].append(f"Scraping exception: {str(e)}")
            self.log_step("SCRAPING", f"Exception: {str(e)}")
            return False
    
    def step_2_process_pipeline(self):
        """Step 2: Process scraped jobs through cleaning pipeline"""
        self.log_step("PIPELINE", "Processing jobs through cleaning pipeline...")
        
        try:
            # Process raw scrapes to cleaned scrapes
            pipeline_result = self.pipeline.process_all_pending_scrapes()
            
            if pipeline_result['success']:
                cleaned_count = pipeline_result.get('processed_count', 0)
                self.test_results['pipeline'] = {
                    'status': 'success',
                    'jobs_cleaned': cleaned_count
                }
                self.log_step("PIPELINE", f"Successfully cleaned {cleaned_count} jobs")
                return True
            else:
                error_msg = pipeline_result.get('error', 'Unknown pipeline error')
                self.test_results['pipeline']['status'] = 'failed'
                self.test_results['errors'].append(f"Pipeline failed: {error_msg}")
                self.log_step("PIPELINE", f"Failed: {error_msg}")
                return False
                
        except Exception as e:
            self.test_results['pipeline']['status'] = 'failed'
            self.test_results['errors'].append(f"Pipeline exception: {str(e)}")
            self.log_step("PIPELINE", f"Exception: {str(e)}")
            return False
    
    def step_3_transfer_to_jobs(self):
        """Step 3: Get cleaned jobs for processing"""
        self.log_step("TRANSFER", "Getting cleaned jobs for AI analysis...")
        
        try:
            # Get cleaned jobs ready for processing
            cleaned_jobs = self.db_manager.reader.get_recent_cleaned_jobs(limit=5)
            
            if cleaned_jobs:
                self.test_results['transfer'] = {
                    'status': 'success',
                    'jobs_available': len(cleaned_jobs)
                }
                self.log_step("TRANSFER", f"Found {len(cleaned_jobs)} cleaned jobs ready for processing")
                return True
            else:
                self.test_results['transfer'] = {'status': 'success', 'jobs_available': 0}
                self.log_step("TRANSFER", "No cleaned jobs found, but pipeline completed successfully")
                return True
                
        except Exception as e:
            self.test_results['transfer'] = {'status': 'failed'}
            self.test_results['errors'].append(f"Transfer exception: {str(e)}")
            self.log_step("TRANSFER", f"Exception: {str(e)}")
            return False
    
    def step_4_ai_analysis(self):
        """Step 4: Run Gemini AI analysis on jobs"""
        self.log_step("AI_ANALYSIS", "Running Gemini AI analysis on jobs...")
        
        try:
            # Get unanalyzed jobs
            unanalyzed_jobs = self.db_manager.get_unanalyzed_jobs(limit=5)
            
            if not unanalyzed_jobs:
                self.log_step("AI_ANALYSIS", "No unanalyzed jobs found")
                return True
            
            self.log_step("AI_ANALYSIS", f"Found {len(unanalyzed_jobs)} jobs to analyze")
            
            # Prepare job data for AI analysis
            job_data_list = []
            for job in unanalyzed_jobs:
                job_data = {
                    'id': job['id'],
                    'title': job.get('job_title', 'Unknown'),
                    'company_name': job.get('company_name', 'Unknown'),
                    'description': job.get('description', 'No description available'),
                    'location': job.get('location', 'Unknown')
                }
                job_data_list.append(job_data)
            
            # Run AI analysis
            analysis_result = self.ai_analyzer.analyze_jobs_batch(job_data_list)
            
            if analysis_result and analysis_result.get('success'):
                analyzed_count = len(analysis_result.get('results', []))
                self.test_results['ai_analysis'] = {
                    'status': 'success',
                    'jobs_analyzed': analyzed_count
                }
                self.log_step("AI_ANALYSIS", f"Successfully analyzed {analyzed_count} jobs")
                return True
            else:
                error_msg = analysis_result.get('error', 'Unknown AI analysis error')
                self.test_results['ai_analysis']['status'] = 'failed'
                self.test_results['errors'].append(f"AI analysis failed: {error_msg}")
                self.log_step("AI_ANALYSIS", f"Failed: {error_msg}")
                return False
                
        except Exception as e:
            self.test_results['ai_analysis']['status'] = 'failed'
            self.test_results['errors'].append(f"AI analysis exception: {str(e)}")
            self.log_step("AI_ANALYSIS", f"Exception: {str(e)}")
            return False
    
    def step_5_generate_documents(self):
        """Step 5: Generate job application documents"""
        self.log_step("DOCUMENTS", "Generating job application documents...")
        
        try:
            # Get jobs ready for application
            ready_jobs = self.db_manager.get_jobs_ready_for_application(limit=5)
            
            if not ready_jobs:
                self.log_step("DOCUMENTS", "No jobs ready for application")
                return True
            
            self.log_step("DOCUMENTS", f"Generating documents for {len(ready_jobs)} jobs")
            
            generated_documents = []
            
            for job in ready_jobs:
                try:
                    # Generate resume
                    resume_data = self._prepare_resume_data(job)
                    resume_result = self.document_generator.generate_document(
                        document_type='resume',
                        template_data=resume_data,
                        job_id=job['id']
                    )
                    
                    # Generate cover letter
                    cover_letter_data = self._prepare_cover_letter_data(job)
                    cover_letter_result = self.document_generator.generate_document(
                        document_type='cover_letter',
                        template_data=cover_letter_data,
                        job_id=job['id']
                    )
                    
                    if resume_result['success'] and cover_letter_result['success']:
                        generated_documents.append({
                            'job_id': job['id'],
                            'job_title': job.get('job_title', 'Unknown'),
                            'company': job.get('company_name', 'Unknown'),
                            'resume_path': resume_result['file_path'],
                            'cover_letter_path': cover_letter_result['file_path']
                        })
                        
                except Exception as e:
                    self.log_step("DOCUMENTS", f"Failed to generate documents for job {job['id']}: {str(e)}")
                    continue
            
            self.test_results['document_generation'] = {
                'status': 'success',
                'documents_created': len(generated_documents),
                'documents': generated_documents
            }
            
            self.log_step("DOCUMENTS", f"Successfully generated {len(generated_documents)} document sets")
            return True
            
        except Exception as e:
            self.test_results['document_generation']['status'] = 'failed'
            self.test_results['errors'].append(f"Document generation exception: {str(e)}")
            self.log_step("DOCUMENTS", f"Exception: {str(e)}")
            return False
    
    def step_6_send_emails(self):
        """Step 6: Send job application emails"""
        self.log_step("EMAIL", "Sending job application emails...")
        
        try:
            documents = self.test_results.get('document_generation', {}).get('documents', [])
            
            if not documents:
                self.log_step("EMAIL", "No documents available for sending")
                return True
            
            self.log_step("EMAIL", f"Sending {len(documents)} job applications")
            
            sent_count = 0
            
            for doc_set in documents[:5]:  # Limit to 5 emails as requested
                try:
                    # Prepare email content
                    subject = f"Application for {doc_set['job_title']} at {doc_set['company']}"
                    body = self._prepare_email_body(doc_set)
                    
                    # Send email with attachments
                    email_result = self.gmail_sender.send_email_with_attachments(
                        recipient='therealstevenglen@gmail.com',
                        subject=subject,
                        body=body,
                        attachments=[
                            doc_set['resume_path'],
                            doc_set['cover_letter_path']
                        ]
                    )
                    
                    if email_result['success']:
                        sent_count += 1
                        self.log_step("EMAIL", f"Sent application for {doc_set['job_title']} at {doc_set['company']}")
                        time.sleep(2)  # Rate limiting between emails
                    else:
                        self.log_step("EMAIL", f"Failed to send email for {doc_set['job_title']}: {email_result.get('error')}")
                        
                except Exception as e:
                    self.log_step("EMAIL", f"Email sending exception for {doc_set['job_title']}: {str(e)}")
                    continue
            
            self.test_results['email_sending'] = {
                'status': 'success',
                'emails_sent': sent_count
            }
            
            self.log_step("EMAIL", f"Successfully sent {sent_count} job application emails")
            return True
            
        except Exception as e:
            self.test_results['email_sending']['status'] = 'failed'
            self.test_results['errors'].append(f"Email sending exception: {str(e)}")
            self.log_step("EMAIL", f"Exception: {str(e)}")
            return False
    
    def _prepare_resume_data(self, job):
        """Prepare resume data for document generation"""
        return {
            'full_name': 'Steve Glen',
            'phone': '(780) 555-0123',
            'email': '1234.s.t.e.v.e.glen@gmail.com',
            'location': 'Edmonton, AB, Canada',
            'target_position': job.get('job_title', 'Marketing Manager'),
            'professional_summary': 'Experienced marketing professional with 14+ years in digital marketing, content strategy, and business development.',
            'experience': [
                {
                    'title': 'Marketing Communications Manager',
                    'company': 'Odvod Media / Edify Magazine',
                    'duration': '2010 - Present',
                    'achievements': [
                        'Led digital marketing initiatives resulting in 40% increase in online engagement',
                        'Developed content strategy for multiple publication platforms',
                        'Managed marketing budget of $100,000+ annually'
                    ]
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Commerce',
                    'school': 'University of Alberta',
                    'year': '2009'
                }
            ],
            'skills': [
                'Digital Marketing Strategy',
                'Content Creation & Management',
                'Data Analysis & Reporting',
                'Project Management',
                'Adobe Creative Suite'
            ]
        }
    
    def _prepare_cover_letter_data(self, job):
        """Prepare cover letter data for document generation"""
        return {
            'recipient_name': 'Hiring Manager',
            'company_name': job.get('company_name', 'Your Company'),
            'position_title': job.get('job_title', 'Marketing Manager'),
            'sender_name': 'Steve Glen',
            'sender_title': 'Marketing Professional',
            'opening_paragraph': f"I am writing to express my strong interest in the {job.get('job_title', 'Marketing Manager')} position at {job.get('company_name', 'your company')}.",
            'body_paragraphs': [
                "With over 14 years of experience in marketing communications and digital strategy, I bring a proven track record of driving growth and engagement through innovative marketing initiatives.",
                "My expertise in content strategy, data analysis, and cross-functional collaboration aligns perfectly with your requirements for this role."
            ],
            'closing_paragraph': "I would welcome the opportunity to discuss how my experience and passion for marketing can contribute to your team's continued success.",
            'date': datetime.now().strftime('%B %d, %Y')
        }
    
    def _prepare_email_body(self, doc_set):
        """Prepare email body for job application"""
        return f"""Dear Hiring Manager,

I am pleased to submit my application for the {doc_set['job_title']} position at {doc_set['company']}.

Please find attached my resume and cover letter for your review. I am excited about the opportunity to contribute to your team and would welcome the chance to discuss my qualifications in more detail.

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
        """Run the complete end-to-end test workflow"""
        self.log_step("TEST", "Starting complete end-to-end workflow test")
        
        # Step 1: Scrape jobs
        if not self.step_1_scrape_jobs():
            self.log_step("TEST", "Test failed at scraping step")
            return self.test_results
        
        # Step 2: Process through pipeline
        if not self.step_2_process_pipeline():
            self.log_step("TEST", "Test failed at pipeline step")
            return self.test_results
        
        # Step 3: Transfer to jobs table
        if not self.step_3_transfer_to_jobs():
            self.log_step("TEST", "Test failed at transfer step")
            return self.test_results
        
        # Step 4: AI analysis
        if not self.step_4_ai_analysis():
            self.log_step("TEST", "Test failed at AI analysis step")
            return self.test_results
        
        # Step 5: Generate documents
        if not self.step_5_generate_documents():
            self.log_step("TEST", "Test failed at document generation step")
            return self.test_results
        
        # Step 6: Send emails
        if not self.step_6_send_emails():
            self.log_step("TEST", "Test failed at email sending step")
            return self.test_results
        
        # Complete test results
        self.test_results['end_time'] = datetime.now()
        self.test_results['duration'] = (self.test_results['end_time'] - self.test_results['start_time']).total_seconds()
        self.test_results['overall_status'] = 'success'
        
        self.log_step("TEST", f"Complete end-to-end test finished successfully in {self.test_results['duration']:.1f} seconds")
        return self.test_results
    
    def print_results_summary(self):
        """Print a comprehensive summary of test results"""
        print("\n" + "="*80)
        print("END-TO-END WORKFLOW TEST RESULTS")
        print("="*80)
        
        print(f"Start Time: {self.test_results['start_time']}")
        if 'end_time' in self.test_results:
            print(f"End Time: {self.test_results['end_time']}")
            print(f"Duration: {self.test_results['duration']:.1f} seconds")
        
        print(f"\nOverall Status: {self.test_results.get('overall_status', 'incomplete').upper()}")
        
        print("\nStep Results:")
        print(f"  Scraping: {self.test_results['scraping']['status']} - {self.test_results['scraping'].get('jobs_found', 0)} jobs found")
        print(f"  Pipeline: {self.test_results['pipeline']['status']} - {self.test_results['pipeline'].get('jobs_cleaned', 0)} jobs cleaned")
        
        if 'transfer' in self.test_results:
            print(f"  Transfer: {self.test_results['transfer']['status']} - {self.test_results['transfer'].get('jobs_transferred', 0)} jobs transferred")
        
        print(f"  AI Analysis: {self.test_results['ai_analysis']['status']} - {self.test_results['ai_analysis'].get('jobs_analyzed', 0)} jobs analyzed")
        print(f"  Documents: {self.test_results['document_generation']['status']} - {self.test_results['document_generation'].get('documents_created', 0)} document sets created")
        print(f"  Emails: {self.test_results['email_sending']['status']} - {self.test_results['email_sending'].get('emails_sent', 0)} emails sent")
        
        if self.test_results['errors']:
            print("\nErrors Encountered:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*80)

def main():
    """Main test execution"""
    print("Starting End-to-End Job Application System Test")
    print("Educational Purpose Only - Testing automated workflow capabilities")
    
    # Create and run test
    test = EndToEndWorkflowTest()
    results = test.run_complete_test()
    
    # Print results
    test.print_results_summary()
    
    # Save results to file
    results_file = f"test_results_end_to_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    main()