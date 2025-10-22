#!/usr/bin/env python3
"""
Module: diagnose_docker_network.py
Purpose: Diagnose Docker container networking and Flask accessibility
Created: 2024-09-18
Modified: 2025-10-21
Dependencies: None (standard library only)
Related: .devcontainer/, docker-compose.yml
Description: Identifies network configuration issues in Docker containers,
             checks Flask accessibility, and validates database connectivity.
"""

import os
import socket
import subprocess
import json

print("=" * 80)
print("DOCKER CONTAINER NETWORK DIAGNOSIS")
print("=" * 80)

# 1. Identify the environment
print("\n1. ENVIRONMENT IDENTIFICATION")
print("-" * 40)
print(f"  Hostname: {socket.gethostname()}")
print(f"  In Docker: {os.path.exists('/.dockerenv')}")

# Get container ID if in Docker
try:
    with open('/proc/self/cgroup', 'r') as f:
        for line in f:
            if 'docker' in line:
                container_id = line.split('/')[-1].strip()[:12]
                print(f"  Container ID: {container_id}")
                break
except:
    pass

# 2. Network interfaces and IPs
print("\n2. NETWORK INTERFACES")
print("-" * 40)
result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
print(f"  Container IPs: {result.stdout.strip()}")

result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'default' in line:
        print(f"  Default route: {line}")

# 3. Check what Flask is actually bound to
print("\n3. FLASK BINDING CHECK")
print("-" * 40)
result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True, errors='ignore')
for line in result.stdout.split('\n'):
    if '5000' in line:
        print(f"  Port 5000: {line}")

# If netstat doesn't work, try ss
if '5000' not in result.stdout:
    result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, errors='ignore')
    for line in result.stdout.split('\n'):
        if '5000' in line:
            print(f"  Port 5000: {line}")

# 4. Docker port mapping
print("\n4. DOCKER PORT MAPPING")
print("-" * 40)
print("  Checking if ports are exposed to host...")

# Check Docker environment variables
docker_vars = ['DOCKER_HOST', 'HOSTNAME', 'PORT', 'HOST']
for var in os.environ:
    if 'DOCKER' in var or 'PORT' in var or 'HOST' in var:
        print(f"  {var}: {os.environ[var]}")

# 5. Test Flask accessibility from container
print("\n5. FLASK ACCESSIBILITY TEST")
print("-" * 40)

import urllib.request
import urllib.error

test_urls = [
    'http://localhost:5000/',
    'http://127.0.0.1:5000/',
    'http://0.0.0.0:5000/',
    f'http://{socket.gethostname()}:5000/',
]

# Get container IP
container_ip = result.stdout.strip().split()[0] if result.stdout else None
if container_ip:
    test_urls.append(f'http://{container_ip}:5000/')

for url in test_urls:
    try:
        response = urllib.request.urlopen(url, timeout=2)
        print(f"  ✓ {url}: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"  ✗ {url}: HTTP {e.code}")
    except urllib.error.URLError as e:
        print(f"  ✗ {url}: {str(e.reason)}")
    except Exception as e:
        print(f"  ✗ {url}: {e}")

# 6. Check Flask process and its actual binding
print("\n6. FLASK PROCESS DETAILS")
print("-" * 40)
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'flask' in line.lower() or 'app_modular' in line:
        parts = line.split()
        if len(parts) > 10:
            print(f"  PID {parts[1]}: {' '.join(parts[10:])[:80]}")

# Get the actual listening address from Flask process
result = subprocess.run(['lsof', '-i', ':5000', '-n', '-P'], capture_output=True, text=True, errors='ignore')
if result.stdout:
    print("\n  LSOF Output (actual binding):")
    for line in result.stdout.split('\n')[1:]:  # Skip header
        if line:
            print(f"    {line}")

# 7. Browser access instructions
print("\n7. BROWSER ACCESS FROM HOST")
print("-" * 40)
print("  Since Flask is inside a Docker container, you need to access it")
print("  using the port that Docker exposes to your host machine.")
print("")
print("  IMPORTANT: The URL depends on how Docker is configured:")
print("")
print("  If using Docker Desktop or similar:")
print("    • http://localhost:5000/dashboard (if port is mapped)")
print("")
print("  If ports are NOT mapped, Flask is NOT accessible from host browser!")
print("  Docker containers are isolated unless ports are explicitly exposed.")
print("")

# 8. Check if this is a Codespace or GitHub environment
print("\n8. CODESPACE/GITHUB CHECK")
print("-" * 40)
codespace_vars = ['CODESPACE_NAME', 'GITHUB_CODESPACE_TOKEN', 'CODESPACES']
is_codespace = False
for var in codespace_vars:
    if var in os.environ:
        print(f"  {var}: {os.environ.get(var)[:50]}...")
        is_codespace = True

if is_codespace:
    print("\n  ⚠️  CODESPACE DETECTED!")
    print("  In GitHub Codespaces, you need to:")
    print("  1. Use the Ports tab in VS Code")
    print("  2. Make port 5000 public or add port forwarding")
    print("  3. Use the provided Codespace URL, not localhost")

# 9. Check docker-compose or devcontainer config
print("\n9. DOCKER CONFIGURATION FILES")
print("-" * 40)

config_files = [
    'docker-compose.yml',
    'docker-compose.yaml',
    '.devcontainer/devcontainer.json',
    'Dockerfile',
]

for config_file in config_files:
    if os.path.exists(config_file):
        print(f"\n  Found: {config_file}")
        with open(config_file, 'r') as f:
            content = f.read()
            # Look for port mappings
            for line in content.split('\n'):
                if 'port' in line.lower() or '5000' in line:
                    print(f"    {line.strip()}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)