#!/bin/bash
##
## Test the hook modules without jq dependency
##

echo "=== Testing Hook Modules ==="
echo ""

# Test 1: Question detection
echo "TEST 1: Question - 'How do we implement authentication?'"
echo '{"userPrompt":"How do we implement authentication?"}' | \
    python3 -c "
import json
import sys
import subprocess

data = json.load(sys.stdin)
prompt = data.get('userPrompt', '')
print(f'User prompt: {prompt}')

# Mock the check
prompt_lower = prompt.lower()
if any(word in prompt_lower for word in ['how', 'what', 'why', 'which']):
    print('✓ Question detected - should trigger ANALYSIS mode')
else:
    print('✗ No question detected')
"
echo ""

# Test 2: Implementation command
echo "TEST 2: Implementation - 'Fix the authentication bug'"
echo '{"userPrompt":"Fix the authentication bug"}' | \
    python3 -c "
import json
import sys

data = json.load(sys.stdin)
prompt = data.get('userPrompt', '')
print(f'User prompt: {prompt}')

# Mock the check
prompt_lower = prompt.lower()
if any(word in prompt_lower for word in ['fix', 'update', 'create', 'implement']):
    print('✓ Implementation command detected')
else:
    print('✗ No implementation detected')
"
echo ""

# Test 3: Complex task
echo "TEST 3: Complex task - 'Implement these features: 1. Login 2. Logout 3. Password reset'"
echo '{"userPrompt":"Implement these features: 1. Login 2. Logout 3. Password reset"}' | \
    python3 -c "
import json
import sys
import re

data = json.load(sys.stdin)
prompt = data.get('userPrompt', '')
print(f'User prompt: {prompt}')

# Check for numbered list
if re.search(r'[0-9]+\.', prompt):
    print('✓ Numbered list detected - should trigger TodoWrite reminder')
else:
    print('✗ No list detected')
"
echo ""

# Test 4: Git operation
echo "TEST 4: Git operation - 'Please commit these changes'"
echo '{"userPrompt":"Please commit these changes"}' | \
    python3 -c "
import json
import sys

data = json.load(sys.stdin)
prompt = data.get('userPrompt', '')
print(f'User prompt: {prompt}')

# Mock the check
prompt_lower = prompt.lower()
if 'commit' in prompt_lower:
    print('✓ Git operation detected - reminder about git-orchestrator')
else:
    print('✗ No git operation detected')
"
echo ""

# Test 5: Compound statement
echo "TEST 5: Compound - 'The system failed. Why?'"
echo '{"userPrompt":"The system failed. Why?"}' | \
    python3 -c "
import json
import sys

data = json.load(sys.stdin)
prompt = data.get('userPrompt', '')
print(f'User prompt: {prompt}')

# Check for question mark or question word
if prompt.endswith('?') or 'why' in prompt.lower():
    print('✓ Question pattern detected - should trigger ANALYSIS mode')
else:
    print('✗ No question detected')
"
echo ""

echo "=== Hook Module Logic Summary ==="
echo ""
echo "communication_guidance.sh triggers on:"
echo "  - Question words (what, how, why, which, should)"
echo "  - Recommendation patterns (recommend, options, best practice)"
echo "  - Compound statements (failed...why, broken...explain)"
echo "  - Prompts ending with ?"
echo ""
echo "implementation_guidance.sh triggers on:"
echo "  - Implementation commands (fix, update, create, implement)"
echo "  - Complex indicators (multiple, several, list of)"
echo "  - Numbered/bulleted lists"
echo "  → Reminds about: explain first, break down, use TodoWrite, add docs"
echo ""
echo "workflow_reminders.sh (optional) triggers on:"
echo "  - Git operations → gentle reminder about git-orchestrator"
echo "  - Schema changes → gentle reminder about database_tools"