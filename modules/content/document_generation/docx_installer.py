#!/usr/bin/env python3
"""
Dynamic python-docx installer for document generation
Only installs python-docx when document generation is actually needed
"""

import sys
import subprocess
import importlib
import logging


def install_python_docx():
    """Install python-docx using uv package manager"""
    try:
        print("Installing python-docx...")
        result = subprocess.run(["uv", "add", "python-docx"], check=True, capture_output=True, text=True)
        print("✅ python-docx installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install python-docx with uv: {e}")
        print("Trying with pip...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "python-docx"], check=True, capture_output=True, text=True
            )
            print("✅ python-docx installed successfully with pip")
            return True
        except subprocess.CalledProcessError as pip_error:
            print(f"❌ Failed to install python-docx with pip: {pip_error}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error installing python-docx: {e}")
        return False


def ensure_docx_available():
    """
    Ensure python-docx is available, install if needed
    Returns True if available, False if installation failed
    """
    try:
        # Try to import docx
        import docx

        print("✅ python-docx already available")
        return True
    except ImportError:
        print("📦 python-docx not found, installing...")
        return install_python_docx()


def get_docx_module():
    """
    Get the docx module, installing if necessary
    Returns the docx module or raises ImportError if unavailable
    """
    if ensure_docx_available():
        try:
            import docx

            return docx
        except ImportError as e:
            raise ImportError(f"Failed to import python-docx after installation: {e}")
    else:
        raise ImportError("Could not install python-docx")


if __name__ == "__main__":
    # Test the installer
    try:
        docx = get_docx_module()
        print(f"✅ python-docx version: {docx.__version__}")
        print("✅ Document generation ready")
    except ImportError as e:
        print(f"❌ Failed to setup python-docx: {e}")
        sys.exit(1)
