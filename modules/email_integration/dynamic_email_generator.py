"""
Dynamic Email Content Generator
Generates unique, contextual email content based on actual system data and test results
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class DynamicEmailGenerator:
    """
    Generates dynamic, contextual email content based on system state and test results
    """

    def __init__(self):
        self.test_contexts = [
            "end-to-end workflow validation",
            "document generation system testing",
            "APIFY integration verification",
            "email automation functionality check",
            "complete pipeline validation",
            "system integration testing",
            "production readiness assessment",
        ]

        self.technical_achievements = [
            "Successfully authenticated with dashboard security",
            "Validated template-based document generation",
            "Confirmed APIFY job scraping operational",
            "Verified Gmail OAuth integration working",
            "Tested complete automation workflow",
            "Validated database connectivity and queries",
            "Confirmed API endpoint functionality",
        ]

        self.business_benefits = [
            "Automated job application processing saves 2+ hours per application",
            "AI-powered job matching improves application success rate by 40%",
            "Professional document generation ensures consistent quality",
            "Real-time job scraping provides competitive advantage",
            "Integrated email automation streamlines communication",
            "Complete workflow tracking enables performance optimization",
        ]

    def generate_test_summary_email(self, test_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate dynamic email content based on actual test results

        Args:
            test_results: Dictionary containing test results and system data

        Returns:
            Dictionary with subject and body content
        """

        # Extract actual data from test results
        timestamp = datetime.now()
        test_id = f"TEST_{timestamp.strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}"

        # Determine overall status
        total_tests = len(test_results.get("tests", {}))
        passed_tests = sum(1 for result in test_results.get("tests", {}).values() if result.get("status") == "passed")
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Generate dynamic subject
        subjects = [
            f"System Test {test_id} - {passed_tests}/{total_tests} Components Validated",
            f"Automation Update: {success_rate:.0f}% Success Rate - {timestamp.strftime('%B %d, %Y')}",
            f"Job Application System Status - {passed_tests} Features Operational",
            f"Production Test Results: {test_results.get('primary_focus', 'System Integration')} Complete",
        ]

        subject = random.choice(subjects)

        # Generate dynamic body content
        body = self._generate_dynamic_body(test_results, test_id, timestamp, passed_tests, total_tests)

        return {"subject": subject, "body": body}

    def _generate_dynamic_body(
        self, test_results: Dict, test_id: str, timestamp: datetime, passed_tests: int, total_tests: int
    ) -> str:
        """Generate dynamic email body content"""

        # Dynamic greeting and context
        greetings = [
            "System status update from your automated job application platform:",
            "Latest test results from the job automation system:",
            "Production validation completed for your job application workflow:",
            "Comprehensive system check results are now available:",
        ]

        greeting = random.choice(greetings)

        # Generate test results section
        test_section = self._generate_test_results_section(test_results, passed_tests, total_tests)

        # Generate technical details section
        technical_section = self._generate_technical_details_section(test_results)

        # Generate findings and recommendations
        findings_section = self._generate_findings_section(test_results)

        # Generate next steps
        next_steps_section = self._generate_next_steps_section(test_results)

        # Assemble complete email
        body = f"""{greeting}

TEST EXECUTION SUMMARY
Test ID: {test_id}
Execution Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}
Duration: {test_results.get('duration', '45')} seconds
Environment: {test_results.get('environment', 'Production')}

{test_section}

{technical_section}

{findings_section}

{next_steps_section}

SYSTEM STATUS: {'OPERATIONAL' if passed_tests >= total_tests * 0.8 else 'NEEDS ATTENTION'}

---
Automated Job Application System v{test_results.get('version', '2.15')}
Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Educational Purpose Only"""

        return body

    def _generate_test_results_section(self, test_results: Dict, passed_tests: int, total_tests: int) -> str:
        """Generate dynamic test results section"""

        results_lines = ["COMPONENT VALIDATION RESULTS:"]

        # Add actual test results if available
        if "tests" in test_results:
            for component, result in test_results["tests"].items():
                status_symbol = "✓" if result.get("status") == "passed" else "✗"
                details = result.get("details", "")
                results_lines.append(
                    f"{status_symbol} {component.replace('_', ' ').title()}: {result.get('message', 'Completed')} {details}"
                )

        # Add performance metrics if available
        if "performance" in test_results:
            perf = test_results["performance"]
            results_lines.append(f"\nPERFORMANCE METRICS:")
            for metric, value in perf.items():
                results_lines.append(f"  {metric.replace('_', ' ').title()}: {value}")

        return "\n".join(results_lines)

    def _generate_technical_details_section(self, test_results: Dict) -> str:
        """Generate technical details section"""

        details = ["TECHNICAL IMPLEMENTATION DETAILS:"]

        # Add authentication status
        if test_results.get("authentication"):
            details.append(
                f"Authentication: {test_results['authentication'].get('method', 'Dashboard OAuth')} - {test_results['authentication'].get('status', 'Verified')}"
            )

        # Add API endpoints tested
        if test_results.get("endpoints_tested"):
            endpoints = test_results["endpoints_tested"]
            details.append(f"API Endpoints Validated: {len(endpoints)} endpoints")
            for endpoint in endpoints[:3]:  # Show first 3
                details.append(f"  • {endpoint}")

        # Add data processing results
        if test_results.get("data_processing"):
            processing = test_results["data_processing"]
            details.append(
                f"Data Processing: {processing.get('records_processed', 0)} records in {processing.get('time', 'N/A')}"
            )

        # Add integration status
        if test_results.get("integrations"):
            integrations = test_results["integrations"]
            details.append("External Integrations:")
            for service, status in integrations.items():
                details.append(f"  • {service}: {status}")

        return "\n".join(details)

    def _generate_findings_section(self, test_results: Dict) -> str:
        """Generate key findings section"""

        findings = ["KEY FINDINGS & INSIGHTS:"]

        # Add performance insights
        if test_results.get("performance_insights"):
            for insight in test_results["performance_insights"]:
                findings.append(f"• {insight}")

        # Add system capabilities
        capabilities = test_results.get("capabilities_demonstrated", [])
        if capabilities:
            findings.append("Demonstrated Capabilities:")
            for capability in capabilities:
                findings.append(f"  ✓ {capability}")

        # Add any issues or improvements
        if test_results.get("issues_identified"):
            findings.append("Areas for Improvement:")
            for issue in test_results["issues_identified"]:
                findings.append(f"  ! {issue}")

        return "\n".join(findings)

    def _generate_next_steps_section(self, test_results: Dict) -> str:
        """Generate next steps section"""

        next_steps = ["RECOMMENDED NEXT STEPS:"]

        # Add specific recommendations based on test results
        if test_results.get("recommendations"):
            for i, rec in enumerate(test_results["recommendations"], 1):
                next_steps.append(f"{i}. {rec}")
        else:
            # Default recommendations based on system state
            default_steps = [
                "Continue monitoring system performance and reliability",
                "Schedule regular validation tests to ensure continued operation",
                "Review and optimize any components showing degraded performance",
                "Prepare for increased automation workflow volume",
            ]

            for i, step in enumerate(default_steps, 1):
                next_steps.append(f"{i}. {step}")

        return "\n".join(next_steps)

    def generate_job_application_email(self, job_data: Dict[str, Any], documents: List[Dict]) -> Dict[str, str]:
        """
        Generate dynamic job application email content

        Args:
            job_data: Information about the job being applied to
            documents: List of generated documents

        Returns:
            Dictionary with subject and body content
        """

        position = job_data.get("position", "Position")
        company = job_data.get("company", "Company")
        timestamp = datetime.now()

        # Dynamic subject variations
        subjects = [
            f"Application for {position} - Steve Glen",
            f"{position} Application - Steve Glen (Automated Submission)",
            f"Steve Glen - Application for {position} at {company}",
            f"Job Application: {position} - Professional Marketing Executive",
        ]

        subject = random.choice(subjects)

        # Generate application body
        body = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company}.

PROFESSIONAL BACKGROUND:
• 14+ years of marketing communications experience
• Marketing Communications Manager at Odvod Media/Edify Magazine
• Proven track record of driving 40% increases in digital engagement
• Expert in budget management (\$100,000+ with 300%+ ROI)
• Bachelor of Commerce (Marketing Focus) - University of Alberta

CORE COMPETENCIES:
• Digital Marketing Strategy & Implementation
• Google Analytics & Performance Measurement
• Adobe Creative Suite & Design Management
• Content Strategy & Brand Development
• Project Management & Team Leadership

{self._generate_job_specific_content(job_data)}

DOCUMENT ATTACHMENTS:
{self._generate_document_list(documents)}

I am particularly drawn to this opportunity because it aligns perfectly with my experience in marketing communications and strategic campaign development. My proven ability to deliver measurable results in digital marketing initiatives would be valuable to {company}'s continued growth.

I would welcome the opportunity to discuss how my experience and passion for marketing excellence can contribute to your team's success.

Thank you for your consideration.

Best regards,
Steve Glen
1234.s.t.e.v.e.glen@gmail.com
(780) 555-0123
LinkedIn: linkedin.com/in/steveglen

---
Application submitted: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Automated Job Application System v2.15"""

        return {"subject": subject, "body": body}

    def _generate_job_specific_content(self, job_data: Dict) -> str:
        """Generate content specific to the job being applied for"""

        # Analyze job requirements and generate targeted content
        requirements = job_data.get("requirements", [])
        company_info = job_data.get("company_info", {})

        content_lines = []

        if "digital marketing" in str(requirements).lower():
            content_lines.append("DIGITAL MARKETING EXPERTISE:")
            content_lines.append("• Led comprehensive digital marketing campaigns resulting in 300%+ ROI")
            content_lines.append("• Advanced proficiency in Google Analytics, Google Ads, and social media platforms")

        if "content" in str(requirements).lower():
            content_lines.append("CONTENT DEVELOPMENT:")
            content_lines.append("• Created and managed content strategies for B2B and B2C audiences")
            content_lines.append("• Developed multimedia content across web, print, and social channels")

        if company_info.get("industry"):
            content_lines.append(f"INDUSTRY ALIGNMENT:")
            content_lines.append(f"• Strong understanding of {company_info['industry']} market dynamics")

        return "\n".join(content_lines) if content_lines else ""

    def _generate_document_list(self, documents: List[Dict]) -> str:
        """Generate list of attached documents"""

        if not documents:
            return "• Professional resume and cover letter (generated via automated system)"

        doc_lines = []
        for doc in documents:
            doc_type = doc.get("type", "document").title()
            filename = doc.get("filename", "document.docx")
            doc_lines.append(f"• {doc_type}: {filename}")

        return "\n".join(doc_lines)
