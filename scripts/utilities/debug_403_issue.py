#!/usr/bin/env python3
"""
Module: debug_403_issue.py
Purpose: Debug 403 Forbidden errors for dashboard access
Created: 2024-10-10
Modified: 2025-10-21
Dependencies: requests
Related: modules/dashboard_api.py, docs/troubleshooting/DASHBOARD_ACCESS_FIXED.md
Description: Comprehensive environment and Flask app diagnostics for debugging
             403 errors. Checks authentication, network config, and permissions.
"""

import os
import sys
import socket
import requests
import subprocess
from datetime import datetime

print("=" * 80)
print("DASHBOARD 403 ERROR DEBUGGING")
print(f"Timestamp: {datetime.now()}")
print("=" * 80)

# 1. Check Environment
print("\n1. ENVIRONMENT CHECK")
print("-" * 40)
print(f"  Current Working Directory: {os.getcwd()}")
print(f"  Python Version: {sys.version}")
print(f"  User: {os.environ.get('USER', 'unknown')}")
print(f"  Home: {os.environ.get('HOME', 'unknown')}")
print(f"  In Docker: {'Yes' if os.path.exists('/.dockerenv') else 'No'}")

# 2. Check Network and Ports
print("\n2. NETWORK & PORT CHECK")
print("-" * 40)

def check_port(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

# Check various ports
ports_to_check = [
    ('localhost', 5000, 'Flask App'),
    ('127.0.0.1', 5000, 'Flask App (IP)'),
    ('0.0.0.0', 5000, 'Flask App (All interfaces)'),
    ('localhost', 5432, 'PostgreSQL'),
    ('host.docker.internal', 5432, 'PostgreSQL (Docker)')
]

for host, port, service in ports_to_check:
    try:
        is_open = check_port(host, port)
        status = "✓ OPEN" if is_open else "✗ CLOSED"
        print(f"  {host}:{port} ({service}): {status}")
    except Exception as e:
        print(f"  {host}:{port} ({service}): ✗ ERROR - {e}")

# 3. Check Running Processes
print("\n3. RUNNING PROCESSES")
print("-" * 40)

try:
    # Use ps command instead of psutil
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    flask_processes = []

    for line in lines:
        if 'python' in line and ('app_modular' in line or 'flask' in line):
            parts = line.split()
            if len(parts) > 1:
                pid = parts[1]
                cmd = ' '.join(parts[10:])[:100]
                flask_processes.append((pid, cmd))

    if flask_processes:
        for pid, cmd in flask_processes:
            print(f"  PID {pid}: {cmd}...")
    else:
        print("  No Flask processes found")
except Exception as e:
    print(f"  Error checking processes: {e}")

# 4. Test HTTP Requests
print("\n4. HTTP REQUEST TESTS")
print("-" * 40)

endpoints = [
    ('http://localhost:5000/', 'Root endpoint'),
    ('http://localhost:5000/health', 'Health check'),
    ('http://localhost:5000/dashboard', 'Dashboard'),
    ('http://127.0.0.1:5000/', 'Root (IP)'),
    ('http://127.0.0.1:5000/dashboard', 'Dashboard (IP)'),
]

for url, description in endpoints:
    try:
        response = requests.get(url, timeout=2, allow_redirects=False)
        print(f"\n  {description}: {url}")
        print(f"    Status: {response.status_code}")
        print(f"    Headers: {dict(response.headers)}")

        # Check for specific error patterns
        if response.status_code == 403:
            print(f"    ✗ 403 FORBIDDEN - Analyzing response...")

            # Check response content
            content = response.text[:500]
            if 'nginx' in content.lower():
                print(f"    → Served by NGINX (proxy issue)")
            elif 'apache' in content.lower():
                print(f"    → Served by Apache (proxy issue)")
            elif 'forbidden' in content.lower():
                print(f"    → Generic forbidden message")
            else:
                print(f"    → Content preview: {content[:200]}")

            # Check for authentication headers
            if 'WWW-Authenticate' in response.headers:
                print(f"    → Authentication required: {response.headers['WWW-Authenticate']}")

        elif response.status_code == 302:
            print(f"    → Redirect to: {response.headers.get('Location', 'unknown')}")

        elif response.status_code == 200:
            print(f"    ✓ Success - Content length: {len(response.text)} bytes")

    except requests.exceptions.ConnectionError:
        print(f"\n  {description}: {url}")
        print(f"    ✗ CONNECTION REFUSED - Flask not running on this address")
    except requests.exceptions.Timeout:
        print(f"\n  {description}: {url}")
        print(f"    ✗ TIMEOUT - No response within 2 seconds")
    except Exception as e:
        print(f"\n  {description}: {url}")
        print(f"    ✗ ERROR: {e}")

# 5. Check Flask App Configuration
print("\n5. FLASK APP ANALYSIS")
print("-" * 40)

# Read app_modular.py to check configuration
try:
    with open('app_modular.py', 'r') as f:
        app_content = f.read()

    # Check for authentication decorators
    if 'require_page_auth' in app_content:
        print("  ✓ Found require_page_auth decorator")

    if '@app.route(\'/dashboard\')' in app_content:
        print("  ✓ Found /dashboard route")

        # Find the dashboard function
        import re
        dashboard_match = re.search(
            r'@app\.route\(\'/dashboard\'\)(.*?)^@app\.route|^def \w+',
            app_content,
            re.MULTILINE | re.DOTALL
        )
        if dashboard_match:
            dashboard_code = dashboard_match.group(1)[:500]
            if 'require_page_auth' in dashboard_code:
                print("  ⚠ Dashboard uses authentication decorator")
            if 'session.get' in dashboard_code:
                print("  ⚠ Dashboard checks session")
            if 'render_template' in dashboard_code:
                print("  ✓ Dashboard renders template")

    # Check debug mode
    if 'debug=True' in app_content or 'DEBUG = True' in app_content:
        print("  ✓ Debug mode enabled in code")
    else:
        print("  ⚠ Debug mode may not be enabled")

except Exception as e:
    print(f"  Error reading app_modular.py: {e}")

# 6. Check for Proxy/Firewall Issues
print("\n6. PROXY/FIREWALL CHECK")
print("-" * 40)

# Check for proxy environment variables
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy']
proxy_found = False
for var in proxy_vars:
    value = os.environ.get(var)
    if value:
        print(f"  {var}: {value}")
        proxy_found = True

if not proxy_found:
    print("  No proxy environment variables set")

# Check iptables (if available)
try:
    result = subprocess.run(['iptables', '-L', '-n'], capture_output=True, text=True, timeout=2)
    if result.returncode == 0:
        if '5000' in result.stdout:
            print("  ⚠ Found iptables rules for port 5000")
        else:
            print("  ✓ No iptables rules blocking port 5000")
except:
    print("  iptables not available or no permissions")

# 7. Check File Permissions
print("\n7. FILE PERMISSIONS CHECK")
print("-" * 40)

files_to_check = [
    'app_modular.py',
    'frontend_templates/dashboard_v2.html',
    'frontend_templates/dashboard_login.html',
]

for filepath in files_to_check:
    try:
        if os.path.exists(filepath):
            stat_info = os.stat(filepath)
            perms = oct(stat_info.st_mode)[-3:]
            print(f"  {filepath}: {perms} (exists)")
        else:
            print(f"  {filepath}: NOT FOUND")
    except Exception as e:
        print(f"  {filepath}: ERROR - {e}")

# 8. Test with curl command
print("\n8. CURL COMMAND TEST")
print("-" * 40)

curl_commands = [
    "curl -I http://localhost:5000/dashboard",
    "curl -I http://127.0.0.1:5000/dashboard",
    "curl -v http://localhost:5000/dashboard 2>&1 | head -20",
]

for cmd in curl_commands:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
        print(f"\n  Command: {cmd}")
        print(f"  Output:\n{result.stdout[:500]}")
        if result.stderr:
            print(f"  Stderr:\n{result.stderr[:200]}")
    except Exception as e:
        print(f"\n  Command: {cmd}")
        print(f"  Error: {e}")

# 9. Check for Container/VM Network Issues
print("\n9. CONTAINER/VM NETWORK CHECK")
print("-" * 40)

# Get network interfaces
try:
    import netifaces
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                print(f"  {iface}: {addr['addr']}")
except ImportError:
    # Fallback to ip command
    try:
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'inet ' in line:
                print(f"  {line.strip()}")
    except:
        print("  Unable to get network interfaces")

# 10. Summary and Recommendations
print("\n" + "=" * 80)
print("DIAGNOSIS SUMMARY")
print("=" * 80)

issues_found = []

# Analyze results
if not check_port('localhost', 5000):
    issues_found.append("Flask app not listening on localhost:5000")

print("\nISSUES FOUND:")
if issues_found:
    for issue in issues_found:
        print(f"  • {issue}")
else:
    print("  • 403 error despite app running - likely a middleware or routing issue")

print("\nRECOMMENDED ACTIONS:")
print("  1. Check if there's a reverse proxy (nginx/apache) intercepting requests")
print("  2. Verify Flask app is bound to correct interface (0.0.0.0 vs localhost)")
print("  3. Check for security middleware blocking requests")
print("  4. Test with: curl -H 'Host: localhost' http://127.0.0.1:5000/dashboard")
print("  5. Check Flask logs for request handling details")

print("\n" + "=" * 80)
print("END OF DIAGNOSTIC REPORT")
print("=" * 80)