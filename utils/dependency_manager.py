#!/usr/bin/env python3
"""
Smart dependency manager for on-demand package installation
Only installs packages when specific functionality is actually used
"""

import sys
import subprocess
import importlib
import logging
from typing import Dict, List, Optional

class DependencyManager:
    """
    Manages on-demand installation of Python packages
    """
    
    def __init__(self):
        self.installed_packages = set()
        self.installation_cache = {}
    
    def ensure_package(self, package_name: str, import_name: Optional[str] = None, 
                      install_cmd: Optional[List[str]] = None) -> bool:
        """
        Ensure a package is available, install if needed
        
        Args:
            package_name: Name of package to install (e.g., 'python-docx')
            import_name: Name to use for import (e.g., 'docx'), defaults to package_name
            install_cmd: Custom installation command, defaults to ['uv', 'add', package_name]
        
        Returns:
            bool: True if package is available, False if installation failed
        """
        if import_name is None:
            import_name = package_name
        
        # Check cache first
        if package_name in self.installation_cache:
            return self.installation_cache[package_name]
        
        # Try to import the package
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} already available")
            self.installation_cache[package_name] = True
            return True
        except ImportError:
            pass
        
        # Install the package
        print(f"📦 {package_name} not found, installing...")
        
        if install_cmd is None:
            install_cmd = ['uv', 'add', package_name]
        
        success = self._install_package(package_name, install_cmd)
        self.installation_cache[package_name] = success
        return success
    
    def _install_package(self, package_name: str, install_cmd: List[str]) -> bool:
        """Install a package using the specified command"""
        try:
            print(f"Installing {package_name}...")
            result = subprocess.run(install_cmd, 
                                  check=True, capture_output=True, text=True)
            print(f"✅ {package_name} installed successfully")
            self.installed_packages.add(package_name)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package_name}: {e}")
            # Try fallback to pip
            try:
                print(f"Trying pip fallback for {package_name}...")
                pip_cmd = [sys.executable, '-m', 'pip', 'install', package_name]
                subprocess.run(pip_cmd, check=True, capture_output=True, text=True)
                print(f"✅ {package_name} installed successfully with pip")
                self.installed_packages.add(package_name)
                return True
            except subprocess.CalledProcessError as pip_error:
                print(f"❌ Pip fallback failed for {package_name}: {pip_error}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error installing {package_name}: {e}")
            return False
    
    def get_import_or_install(self, package_name: str, import_name: Optional[str] = None):
        """
        Get the imported module, installing if necessary
        
        Args:
            package_name: Name of package to install
            import_name: Name to use for import, defaults to package_name
        
        Returns:
            The imported module
        
        Raises:
            ImportError: If package cannot be installed or imported
        """
        if import_name is None:
            import_name = package_name
        
        if self.ensure_package(package_name, import_name):
            try:
                return importlib.import_module(import_name)
            except ImportError as e:
                raise ImportError(f"Failed to import {import_name} after installation: {e}")
        else:
            raise ImportError(f"Could not install {package_name}")

# Global dependency manager instance
dependency_manager = DependencyManager()

def ensure_docx() -> bool:
    """
    Ensure python-docx is available for document generation
    
    Used by: DocumentGenerator, TemplateEngine
    Purpose: Word document creation and manipulation
    Install timing: Only when document generation is requested
    
    Returns:
        bool: True if available, False if installation failed
    """
    return dependency_manager.ensure_package('python-docx', 'docx')

def ensure_numpy() -> bool:
    """
    Ensure numpy is available for data processing
    
    Used by: ToneAnalyzer for mathematical calculations
    Purpose: Numerical computations for tone coherence scoring
    Install timing: Only when tone analysis is performed
    
    Returns:
        bool: True if available, False if installation failed
    """
    return dependency_manager.ensure_package('numpy')

def ensure_bleach() -> bool:
    """
    Ensure bleach is available for HTML sanitization
    
    Used by: SecurityManager for input sanitization
    Purpose: HTML content cleaning and XSS prevention
    Install timing: Only when security sanitization is needed
    
    Returns:
        bool: True if available, False if installation failed
    """
    return dependency_manager.ensure_package('bleach')

def ensure_trafilatura() -> bool:
    """
    Ensure trafilatura is available for web scraping
    
    Used by: Web scraping modules for content extraction
    Purpose: Extracting clean text from HTML web pages
    Install timing: Only when web scraping functionality is used
    
    Returns:
        bool: True if available, False if installation failed
    """
    return dependency_manager.ensure_package('trafilatura')

def ensure_google_genai() -> bool:
    """
    Ensure google-genai is available for AI analysis
    
    Used by: AI job analysis modules
    Purpose: Google Gemini API integration for job analysis
    Install timing: Only when AI analysis is performed
    
    Returns:
        bool: True if available, False if installation failed
    """
    return dependency_manager.ensure_package('google-genai', 'google.genai')

def ensure_requests() -> bool:
    """
    Ensure requests is available for HTTP operations
    
    Used by: Multiple modules for API calls and web requests
    Purpose: HTTP requests to external services
    Install timing: Only when external API calls are made
    
    Returns:
        bool: True if available, False if installation failed
    """
    return dependency_manager.ensure_package('requests')

def get_docx_module():
    """
    Get the docx module, installing if necessary
    
    Returns:
        module: The docx module for document generation
    
    Raises:
        ImportError: If python-docx cannot be installed or imported
    """
    return dependency_manager.get_import_or_install('python-docx', 'docx')

def get_numpy_module():
    """
    Get the numpy module, installing if necessary
    
    Returns:
        module: The numpy module for numerical computations
    
    Raises:
        ImportError: If numpy cannot be installed or imported
    """
    return dependency_manager.get_import_or_install('numpy')

def get_bleach_module():
    """
    Get the bleach module, installing if necessary
    
    Returns:
        module: The bleach module for HTML sanitization
    
    Raises:
        ImportError: If bleach cannot be installed or imported
    """
    return dependency_manager.get_import_or_install('bleach')

def get_trafilatura_module():
    """
    Get the trafilatura module, installing if necessary
    
    Returns:
        module: The trafilatura module for web scraping
    
    Raises:
        ImportError: If trafilatura cannot be installed or imported
    """
    return dependency_manager.get_import_or_install('trafilatura')

def get_google_genai_module():
    """
    Get the google-genai module, installing if necessary
    
    Returns:
        module: The google.genai module for AI analysis
    
    Raises:
        ImportError: If google-genai cannot be installed or imported
    """
    return dependency_manager.get_import_or_install('google-genai', 'google.genai')

def get_requests_module():
    """
    Get the requests module, installing if necessary
    
    Returns:
        module: The requests module for HTTP operations
    
    Raises:
        ImportError: If requests cannot be installed or imported
    """
    return dependency_manager.get_import_or_install('requests')

if __name__ == "__main__":
    # Test the dependency manager
    print("Testing dependency manager...")
    
    # Test docx installation
    try:
        docx = get_docx_module()
        print(f"✅ python-docx version: {docx.__version__}")
        print("✅ Document generation ready")
    except ImportError as e:
        print(f"❌ Failed to setup python-docx: {e}")
    
    print("\nDependency manager test complete")