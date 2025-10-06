#!/bin/bash

# Pure Gemini API Test Runner
# This script runs the pure Gemini API test without any Replit Agent involvement

echo "🔬 PURE GEMINI API TEST RUNNER"
echo "================================"
echo ""
echo "This script will test Google Gemini API directly to determine"
echo "what JSON structure comes from Gemini vs. our application layer."
echo ""

# Check if script exists
if [ ! -f "test_pure_gemini_api.py" ]; then
    echo "❌ ERROR: test_pure_gemini_api.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found"
    echo "Please install Python 3"
    exit 1
fi

# Create tests directory if it doesn't exist
mkdir -p tests

echo "🚀 Starting pure Gemini API test..."
echo ""

# Run the test script
python3 test_pure_gemini_api.py

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ Test completed successfully!"
    echo ""
    echo "📁 Generated files in tests/ folder:"
    ls -la tests/pure_gemini_* 2>/dev/null || echo "   No pure_gemini_* files found"
    echo ""
    echo "🔍 Compare these files with your system output to determine"
    echo "   what data comes from Gemini vs. your application layer."
else
    echo "❌ Test failed with exit code $exit_code"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check that GEMINI_API_KEY environment variable is set"
    echo "   2. Verify google-genai package is installed"
    echo "   3. Check network connectivity to Google APIs"
fi

echo ""
echo "Script completed."