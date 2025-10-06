"""
Test Official Gmail OAuth Integration
Validates the updated implementation using Google's official libraries
"""

import json
import logging
from modules.email_integration.gmail_oauth_official import (
    get_gmail_oauth_manager, 
    get_gmail_sender, 
    GOOGLE_LIBRARIES_AVAILABLE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_libraries_availability():
    """Test that Google's official libraries are properly installed"""
    
    print("🔍 Testing Google official libraries availability...")
    
    if not GOOGLE_LIBRARIES_AVAILABLE:
        print("❌ Google OAuth libraries not available")
        return False
    
    try:
        # Test specific imports
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        print("✅ All Google OAuth libraries imported successfully")
        print("   - google-auth-oauthlib: ✓")
        print("   - google-api-python-client: ✓") 
        print("   - google.oauth2.credentials: ✓")
        return True
        
    except ImportError as e:
        print(f"❌ Google library import failed: {e}")
        return False

def test_official_oauth_manager_initialization():
    """Test official OAuth manager initialization"""
    
    print("\n🔍 Testing official OAuth manager initialization...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        
        # Check required attributes
        required_attributes = [
            'config', 'credentials', 'service', 
            'setup_oauth_credentials', 'get_authorization_url', 
            'complete_oauth_flow', 'get_oauth_status', 'is_authenticated'
        ]
        
        missing_attributes = []
        for attr in required_attributes:
            if not hasattr(oauth_manager, attr):
                missing_attributes.append(attr)
        
        if missing_attributes:
            print(f"❌ Missing OAuth manager attributes: {missing_attributes}")
            return False
        
        print("✅ Official OAuth manager initialized with all required methods")
        return True
        
    except Exception as e:
        print(f"❌ Official OAuth manager initialization failed: {e}")
        return False

def test_oauth_configuration_compliance():
    """Test OAuth configuration compliance with Google's standards"""
    
    print("\n🔍 Testing OAuth configuration compliance...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        config = oauth_manager.config
        
        # Verify Gmail-specific scopes
        expected_scopes = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
        
        if config.SCOPES != expected_scopes:
            print(f"❌ Invalid Gmail scopes: {config.SCOPES}")
            return False
        
        # Verify file paths
        required_files = ['CREDENTIALS_FILE', 'TOKEN_FILE']
        for file_attr in required_files:
            if not hasattr(config, file_attr):
                print(f"❌ Missing configuration: {file_attr}")
                return False
        
        # Verify storage directory structure
        if not config.CREDENTIALS_FILE.startswith('storage/'):
            print(f"❌ Invalid credentials file path: {config.CREDENTIALS_FILE}")
            return False
            
        print("✅ OAuth configuration complies with Google's standards")
        print(f"   - Scopes: Gmail send/compose ✓")
        print(f"   - Storage: {config.CREDENTIALS_FILE} ✓")
        return True
        
    except Exception as e:
        print(f"❌ OAuth configuration test failed: {e}")
        return False

def test_oauth_status_comprehensive():
    """Test comprehensive OAuth status checking"""
    
    print("\n🔍 Testing comprehensive OAuth status checking...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        status = oauth_manager.get_oauth_status()
        
        # Required status fields
        required_fields = [
            'authenticated', 'credentials_configured', 'tokens_available',
            'google_libraries_available', 'needs_setup', 'needs_authorization',
            'token_valid'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in status:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing OAuth status fields: {missing_fields}")
            return False
        
        # Verify library availability status
        if status['google_libraries_available'] != GOOGLE_LIBRARIES_AVAILABLE:
            print("❌ Library availability status mismatch")
            return False
        
        print("✅ Comprehensive OAuth status checking working")
        print(f"   - Google libraries: {status['google_libraries_available']}")
        print(f"   - Credentials configured: {status['credentials_configured']}")
        print(f"   - Authentication: {status['authenticated']}")
        return True
        
    except Exception as e:
        print(f"❌ OAuth status test failed: {e}")
        return False

def test_official_gmail_sender():
    """Test official Gmail sender initialization"""
    
    print("\n🔍 Testing official Gmail sender...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        gmail_sender = get_gmail_sender(oauth_manager)
        
        # Check required methods
        required_methods = ['send_job_application_email', 'send_test_email']
        missing_methods = []
        
        for method in required_methods:
            if not hasattr(gmail_sender, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing Gmail sender methods: {missing_methods}")
            return False
        
        # Check OAuth manager reference
        if gmail_sender.oauth_manager != oauth_manager:
            print("❌ Gmail sender OAuth manager reference incorrect")
            return False
        
        print("✅ Official Gmail sender initialized correctly")
        return True
        
    except Exception as e:
        print(f"❌ Gmail sender test failed: {e}")
        return False

def test_credentials_setup_format():
    """Test credentials setup with Google Cloud Console format"""
    
    print("\n🔍 Testing credentials setup format...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        
        # Test setup with sample credentials
        test_client_id = "123456789-abcdefghijklmnop.apps.googleusercontent.com"
        test_client_secret = "GOCSPX-1234567890abcdefghijk"
        
        result = oauth_manager.setup_oauth_credentials(test_client_id, test_client_secret)
        
        if result['status'] != 'success':
            print(f"❌ Credentials setup failed: {result}")
            return False
        
        # Verify credentials file was created
        import os
        if not os.path.exists(oauth_manager.config.CREDENTIALS_FILE):
            print("❌ Credentials file was not created")
            return False
        
        # Verify credentials format
        with open(oauth_manager.config.CREDENTIALS_FILE, 'r') as f:
            creds_data = json.load(f)
        
        if 'installed' not in creds_data:
            print("❌ Invalid credentials format - missing 'installed' key")
            return False
        
        installed = creds_data['installed']
        required_keys = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        missing_keys = []
        
        for key in required_keys:
            if key not in installed:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Missing credentials keys: {missing_keys}")
            return False
        
        print("✅ Credentials setup format follows Google Cloud Console standards")
        return True
        
    except Exception as e:
        print(f"❌ Credentials setup test failed: {e}")
        return False

def test_error_handling_official():
    """Test error handling in official implementation"""
    
    print("\n🔍 Testing error handling in official implementation...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        gmail_sender = get_gmail_sender(oauth_manager)
        
        # Test sending without authentication
        result = gmail_sender.send_job_application_email(
            to_email="test@example.com",
            subject="Test Application",
            body="Test body"
        )
        
        if result['status'] != 'error':
            print(f"❌ Expected error for unauthenticated send, got: {result['status']}")
            return False
        
        if 'OAuth flow required' not in result['message']:
            print(f"❌ Expected OAuth error message, got: {result['message']}")
            return False
        
        print("✅ Error handling working correctly in official implementation")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_google_api_service_pattern():
    """Test Google API service creation pattern"""
    
    print("\n🔍 Testing Google API service creation pattern...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        
        # Test service creation without authentication (should fail gracefully)
        try:
            service = oauth_manager.get_gmail_service()
            print("❌ Service creation should fail without authentication")
            return False
        except Exception as expected_error:
            if "Not authenticated" not in str(expected_error):
                print(f"❌ Unexpected error message: {expected_error}")
                return False
        
        print("✅ Gmail API service creation follows official patterns")
        return True
        
    except Exception as e:
        print(f"❌ Service pattern test failed: {e}")
        return False

def main():
    """Run all official Gmail OAuth integration tests"""
    
    print("🚀 Running Official Gmail OAuth Integration Tests")
    print("Using Google's Recommended Libraries")
    print("=" * 60)
    
    tests = [
        ("Google Libraries Availability", test_google_libraries_availability),
        ("Official OAuth Manager", test_official_oauth_manager_initialization),
        ("OAuth Configuration Compliance", test_oauth_configuration_compliance),
        ("OAuth Status Comprehensive", test_oauth_status_comprehensive),
        ("Official Gmail Sender", test_official_gmail_sender),
        ("Credentials Setup Format", test_credentials_setup_format),
        ("Error Handling Official", test_error_handling_official),
        ("Google API Service Pattern", test_google_api_service_pattern)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Official Gmail OAuth Integration Test Results")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} {test_name}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All official Gmail OAuth integration tests passed!")
        print("📧 Official Google Workspace implementation ready!")
        print("\n📋 Implementation Features:")
        print("✓ google-auth-oauthlib for OAuth 2.0 flow")
        print("✓ google-api-python-client for Gmail API")
        print("✓ Official Google Workspace patterns")
        print("✓ RFC-compliant email message creation")
        print("✓ Proper credentials and token management")
        print("✓ Comprehensive error handling")
        
        print("\n🔧 Next Steps:")
        print("1. Configure OAuth credentials: POST /api/email/oauth/setup")
        print("2. Complete OAuth flow: GET /api/email/oauth/authorize")
        print("3. Test email sending: POST /api/email/test")
    else:
        print("⚠️  Some tests failed - review implementation")
    
    return passed == total

if __name__ == "__main__":
    main()