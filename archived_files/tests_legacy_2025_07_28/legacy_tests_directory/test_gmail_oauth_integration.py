"""
Test Gmail OAuth Integration
Validates the complete Gmail OAuth workflow and email sending functionality
"""

import json
import logging
from modules.email_integration.gmail_oauth import get_gmail_oauth_manager, get_gmail_sender
from modules.email_integration.gmail_setup_guide import get_setup_guide

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_oauth_manager_initialization():
    """Test Gmail OAuth manager initialization"""
    
    print("🔍 Testing Gmail OAuth manager initialization...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        
        # Check if manager has required attributes
        required_attributes = ['config', 'setup_oauth_credentials', 'get_oauth_status', 'is_authenticated']
        missing_attributes = []
        
        for attr in required_attributes:
            if not hasattr(oauth_manager, attr):
                missing_attributes.append(attr)
        
        if missing_attributes:
            print(f"❌ Missing OAuth manager attributes: {missing_attributes}")
            return False
        else:
            print("✅ Gmail OAuth manager initialized with all required methods")
            return True
            
    except Exception as e:
        print(f"❌ OAuth manager initialization failed: {e}")
        return False

def test_oauth_configuration_structure():
    """Test OAuth configuration structure"""
    
    print("\n🔍 Testing OAuth configuration structure...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        
        # Check configuration attributes
        config = oauth_manager.config
        required_config = ['SCOPES', 'CREDENTIALS_FILE', 'TOKEN_FILE', 'OAUTH_ENDPOINT', 'TOKEN_ENDPOINT', 'REDIRECT_URI']
        missing_config = []
        
        for attr in required_config:
            if not hasattr(config, attr):
                missing_config.append(attr)
        
        if missing_config:
            print(f"❌ Missing OAuth configuration: {missing_config}")
            return False
        
        # Validate scope configuration
        expected_scopes = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.compose']
        if config.SCOPES != expected_scopes:
            print(f"❌ Invalid OAuth scopes: {config.SCOPES}")
            return False
        
        print("✅ OAuth configuration structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ OAuth configuration test failed: {e}")
        return False

def test_gmail_sender_initialization():
    """Test Gmail sender initialization"""
    
    print("\n🔍 Testing Gmail sender initialization...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        gmail_sender = get_gmail_sender(oauth_manager)
        
        # Check if sender has required methods
        required_methods = ['send_job_application_email', 'send_test_email', '_create_email_message', '_send_via_gmail_api']
        missing_methods = []
        
        for method in required_methods:
            if not hasattr(gmail_sender, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing Gmail sender methods: {missing_methods}")
            return False
        
        # Check Gmail API URL configuration
        expected_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        if gmail_sender.gmail_api_url != expected_url:
            print(f"❌ Invalid Gmail API URL: {gmail_sender.gmail_api_url}")
            return False
        
        print("✅ Gmail sender initialized with all required methods")
        return True
        
    except Exception as e:
        print(f"❌ Gmail sender initialization failed: {e}")
        return False

def test_email_message_creation():
    """Test email message creation functionality"""
    
    print("\n🔍 Testing email message creation...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        gmail_sender = get_gmail_sender(oauth_manager)
        
        # Test basic email creation
        test_email = "test@example.com"
        test_subject = "Test Application"
        test_body = "This is a test job application email."
        
        # Create email message (without attachments)
        email_message = gmail_sender._create_email_message(test_email, test_subject, test_body)
        
        if not email_message:
            print("❌ Email message creation returned None")
            return False
        
        if not isinstance(email_message, str):
            print(f"❌ Email message should be string, got: {type(email_message)}")
            return False
        
        # Check if message is base64 encoded
        try:
            import base64
            decoded = base64.urlsafe_b64decode(email_message + '==')  # Add padding
            if b'To: test@example.com' not in decoded:
                print("❌ Email message doesn't contain recipient")
                return False
        except Exception as decode_error:
            print(f"❌ Email message is not valid base64: {decode_error}")
            return False
        
        print("✅ Email message creation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Email message creation test failed: {e}")
        return False

def test_oauth_status_checking():
    """Test OAuth status checking functionality"""
    
    print("\n🔍 Testing OAuth status checking...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        status = oauth_manager.get_oauth_status()
        
        # Check status structure
        required_status_fields = ['authenticated', 'credentials_configured', 'tokens_available', 'needs_setup', 'needs_authorization']
        missing_fields = []
        
        for field in required_status_fields:
            if field not in status:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing OAuth status fields: {missing_fields}")
            return False
        
        # Check status logic
        if not status['credentials_configured'] and not status['needs_setup']:
            print("❌ OAuth status logic error: needs_setup should be True when credentials not configured")
            return False
        
        print("✅ OAuth status checking working correctly")
        print(f"   - Credentials configured: {status['credentials_configured']}")
        print(f"   - Tokens available: {status['tokens_available']}")
        print(f"   - Authenticated: {status['authenticated']}")
        return True
        
    except Exception as e:
        print(f"❌ OAuth status checking test failed: {e}")
        return False

def test_setup_guide_completeness():
    """Test setup guide completeness"""
    
    print("\n🔍 Testing Gmail setup guide completeness...")
    
    try:
        setup_guide = get_setup_guide()
        guide_data = setup_guide.get_setup_steps()
        api_endpoints = setup_guide.get_api_endpoints()
        
        # Check guide structure
        required_guide_fields = ['title', 'overview', 'requirements', 'estimated_time', 'steps', 'troubleshooting', 'security_notes', 'next_steps']
        missing_guide_fields = []
        
        for field in required_guide_fields:
            if field not in guide_data:
                missing_guide_fields.append(field)
        
        if missing_guide_fields:
            print(f"❌ Missing setup guide fields: {missing_guide_fields}")
            return False
        
        # Check if all 7 setup steps are present
        if len(guide_data['steps']) != 7:
            print(f"❌ Expected 7 setup steps, found: {len(guide_data['steps'])}")
            return False
        
        # Check API endpoints structure
        if 'oauth_endpoints' not in api_endpoints or 'email_endpoints' not in api_endpoints:
            print("❌ Missing OAuth or email endpoints in API reference")
            return False
        
        print("✅ Gmail setup guide is complete")
        print(f"   - Setup steps: {len(guide_data['steps'])}")
        print(f"   - OAuth endpoints: {len(api_endpoints['oauth_endpoints'])}")
        print(f"   - Email endpoints: {len(api_endpoints['email_endpoints'])}")
        return True
        
    except Exception as e:
        print(f"❌ Setup guide completeness test failed: {e}")
        return False

def test_error_handling():
    """Test error handling in Gmail integration"""
    
    print("\n🔍 Testing error handling...")
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        gmail_sender = get_gmail_sender(oauth_manager)
        
        # Test sending without authentication
        result = gmail_sender.send_job_application_email(
            to_email="test@example.com",
            subject="Test",
            body="Test body"
        )
        
        if result['status'] != 'error':
            print(f"❌ Expected error status for unauthenticated send, got: {result['status']}")
            return False
        
        if 'OAuth authentication required' not in result['message']:
            print(f"❌ Expected OAuth authentication error message, got: {result['message']}")
            return False
        
        print("✅ Error handling working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all Gmail OAuth integration tests"""
    
    print("🚀 Running Gmail OAuth Integration Tests")
    print("=" * 55)
    
    tests = [
        ("OAuth Manager Initialization", test_oauth_manager_initialization),
        ("OAuth Configuration Structure", test_oauth_configuration_structure),
        ("Gmail Sender Initialization", test_gmail_sender_initialization),
        ("Email Message Creation", test_email_message_creation),
        ("OAuth Status Checking", test_oauth_status_checking),
        ("Setup Guide Completeness", test_setup_guide_completeness),
        ("Error Handling", test_error_handling)
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
    print("\n" + "=" * 55)
    print("📊 Gmail OAuth Integration Test Results")
    print("=" * 55)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} {test_name}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All Gmail OAuth integration tests passed!")
        print("📧 Gmail OAuth scaffolding is complete and ready for use")
        print("\n📋 Next Steps:")
        print("1. Follow setup guide at: GET /api/email/setup-guide")
        print("2. Configure OAuth credentials: POST /api/email/oauth/setup")
        print("3. Complete OAuth flow: GET /api/email/oauth/authorize")
        print("4. Test email sending: POST /api/email/test")
    else:
        print("⚠️  Some tests failed - review implementation")
    
    return passed == total

if __name__ == "__main__":
    main()