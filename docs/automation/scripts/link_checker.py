#!/usr/bin/env python3
"""
Documentation Link Checker

This script scans all documentation files for links and validates their accessibility.
Supports both internal (relative) and external (HTTP/HTTPS) links.
"""

import os
import re
import sys
import yaml
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Tuple, Set
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class LinkChecker:
    def __init__(self, config_path: str = "docs/automation/config/link_checker_config.yaml"):
        """Initialize the link checker with configuration."""
        self.config = self.load_config(config_path)
        self.docs_root = Path("docs")
        self.broken_links = []
        self.checked_external_links = {}  # Cache for external links
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        default_config = {
            'timeout': 10,
            'max_retries': 2,
            'exclude_patterns': [
                '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg',
                '*.pdf', '*.zip', '*.tar.gz'
            ],
            'exclude_domains': [
                'localhost', '127.0.0.1', 'example.com'
            ],
            'max_workers': 5,
            'check_external': True
        }
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            print(f"Config file {config_path} not found, using defaults")
            return default_config

    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the docs directory."""
        md_files = []
        for root, dirs, files in os.walk(self.docs_root):
            for file in files:
                if file.endswith(('.md', '.markdown')):
                    md_files.append(Path(root) / file)
        return md_files

    def extract_links(self, file_path: Path) -> List[Tuple[str, int]]:
        """Extract all links from a markdown file."""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find markdown links [text](url)
            markdown_links = re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', content)
            for match in markdown_links:
                link_text = match.group(1)
                link_url = match.group(2)
                line_number = content[:match.start()].count('\n') + 1
                links.append((link_url, line_number))
            
            # Find HTML links <a href="url">
            html_links = re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', content)
            for match in html_links:
                link_url = match.group(1)
                line_number = content[:match.start()].count('\n') + 1
                links.append((link_url, line_number))
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return links

    def is_external_link(self, url: str) -> bool:
        """Check if a URL is external (HTTP/HTTPS)."""
        return url.startswith(('http://', 'https://'))

    def is_excluded(self, url: str) -> bool:
        """Check if URL should be excluded from checking."""
        parsed = urlparse(url)
        
        # Check excluded domains
        if parsed.netloc in self.config['exclude_domains']:
            return True
            
        # Check excluded patterns
        for pattern in self.config['exclude_patterns']:
            if pattern.replace('*', '') in url:
                return True
                
        return False

    def check_internal_link(self, url: str, source_file: Path) -> Tuple[bool, str]:
        """Check if an internal link is valid."""
        # Handle anchors
        if url.startswith('#'):
            # For now, assume anchor links are valid (complex to check)
            return True, "Anchor link (not checked)"
        
        # Resolve relative path
        if url.startswith('./') or url.startswith('../'):
            target_path = source_file.parent / url
        else:
            target_path = self.docs_root / url
            
        target_path = target_path.resolve()
        
        if target_path.exists():
            return True, "OK"
        else:
            return False, "File not found"

    def check_external_link(self, url: str) -> Tuple[bool, str]:
        """Check if an external link is accessible."""
        if not self.config['check_external']:
            return True, "External checking disabled"
            
        # Use cache to avoid duplicate requests
        if url in self.checked_external_links:
            return self.checked_external_links[url]
            
        for attempt in range(self.config['max_retries'] + 1):
            try:
                response = requests.head(
                    url, 
                    timeout=self.config['timeout'],
                    allow_redirects=True,
                    headers={'User-Agent': 'Documentation Link Checker'}
                )
                
                if response.status_code < 400:
                    result = (True, f"OK ({response.status_code})")
                else:
                    result = (False, f"HTTP {response.status_code}")
                    
                self.checked_external_links[url] = result
                return result
                
            except requests.exceptions.RequestException as e:
                if attempt == self.config['max_retries']:
                    result = (False, f"Request failed: {str(e)}")
                    self.checked_external_links[url] = result
                    return result
                else:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        return False, "Max retries exceeded"

    def check_links_in_file(self, file_path: Path) -> List[Dict]:
        """Check all links in a single file."""
        file_issues = []
        links = self.extract_links(file_path)
        
        for url, line_number in links:
            if self.is_excluded(url):
                continue
                
            is_valid = True
            error_message = ""
            
            if self.is_external_link(url):
                is_valid, error_message = self.check_external_link(url)
            else:
                is_valid, error_message = self.check_internal_link(url, file_path)
            
            if not is_valid:
                file_issues.append({
                    'file': str(file_path.relative_to(Path.cwd())),
                    'line': line_number,
                    'url': url,
                    'error': error_message
                })
                
        return file_issues

    def run_check(self) -> Dict:
        """Run the complete link checking process."""
        print("Starting documentation link check...")
        
        md_files = self.find_markdown_files()
        print(f"Found {len(md_files)} markdown files to check")
        
        all_issues = []
        
        # Use thread pool for concurrent checking
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            future_to_file = {
                executor.submit(self.check_links_in_file, file_path): file_path 
                for file_path in md_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_issues = future.result()
                    all_issues.extend(file_issues)
                    if file_issues:
                        print(f"Issues found in {file_path.relative_to(Path.cwd())}")
                except Exception as e:
                    print(f"Error checking {file_path}: {e}")
        
        # Generate report
        report = {
            'total_files_checked': len(md_files),
            'total_issues': len(all_issues),
            'issues': all_issues,
            'external_links_checked': len(self.checked_external_links),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return report

    def print_report(self, report: Dict):
        """Print a human-readable report."""
        print(f"\n{'='*60}")
        print("LINK CHECKING REPORT")
        print(f"{'='*60}")
        print(f"Files checked: {report['total_files_checked']}")
        print(f"External links cached: {report['external_links_checked']}")
        print(f"Total issues found: {report['total_issues']}")
        print(f"Timestamp: {report['timestamp']}")
        
        if report['issues']:
            print(f"\n{'BROKEN LINKS':-^60}")
            current_file = None
            for issue in report['issues']:
                if issue['file'] != current_file:
                    current_file = issue['file']
                    print(f"\n📄 {current_file}")
                    
                print(f"  Line {issue['line']:3d}: {issue['url']}")
                print(f"           ❌ {issue['error']}")
        else:
            print(f"\n✅ No broken links found!")

    def save_report(self, report: Dict, output_file: str = "link_check_report.json"):
        """Save report to JSON file."""
        import json
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {output_file}")


def main():
    """Main entry point."""
    checker = LinkChecker()
    report = checker.run_check()
    checker.print_report(report)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--save-report":
        checker.save_report(report)
    
    # Exit with error code if issues found
    sys.exit(1 if report['total_issues'] > 0 else 0)


if __name__ == "__main__":
    main()