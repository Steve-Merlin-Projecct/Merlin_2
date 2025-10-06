#!/usr/bin/env python3
"""
Gmail OAuth Test Setup
Configures Gmail OAuth and sends test email to therealstevenglen@gmail.com
"""

import os
import json
import logging
from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager, get_gmail_sender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_gmail_credentials():
    """Setup Gmail OAuth credentials from environment or manual input"""
    
    # Try to get credentials from environment variable
    google_creds = os.environ.get('GOOGLE_CREDENTIALS')
    
    if google_creds:
        logger.info("Found GOOGLE_CREDENTIALS environment variable")
        try:
            creds_data = json.loads(google_creds)
            
            # Extract client_id and client_secret
            if 'installed' in creds_data:
                client_id = creds_data['installed']['client_id']
                client_secret = creds_data['installed']['client_secret']
            elif 'client_id' in creds_data:
                client_id = creds_data['client_id']
                client_secret = creds_data['client_secret']
            else:
                logger.error("Invalid credentials format")
                return False
                
            # Setup OAuth manager
            oauth_manager = get_gmail_oauth_manager()
            result = oauth_manager.setup_oauth_credentials(client_id, client_secret)
            
            if result['status'] == 'success':
                logger.info("OAuth credentials configured successfully")
                return True
            else:
                logger.error(f"Failed to setup credentials: {result['message']}")
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in Google_Credentials: {e}")
            return False
    else:
        logger.warning("GOOGLE_CREDENTIALS environment variable not found")
        return False

def send_test_email():
    """Send test email to therealstevenglen@gmail.com"""
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        
        # Check OAuth status
        status = oauth_manager.get_oauth_status()
        logger.info(f"OAuth Status: {status}")
        
        if not status['credentials_configured']:
            logger.error("OAuth credentials not configured")
            return False
        
        if not status['authenticated']:
            logger.info("OAuth authentication required - starting flow")
            
            # Get authorization URL
            auth_result = oauth_manager.get_authorization_url()
            if auth_result['status'] == 'success':
                print(f"\n🔗 Authorization Required!")
                print(f"Visit this URL to authorize Gmail access:")
                print(f"{auth_result['authorization_url']}")
                print("\nAfter authorization, run the OAuth completion flow.")
                return False
            else:
                logger.error(f"Failed to get authorization URL: {auth_result['message']}")
                return False
        
        # Send test email
        gmail_sender = get_gmail_sender(oauth_manager)
        result = gmail_sender.send_test_email("1234.S.t.e.v.e.Glen@gmail.com")
        
        if result['status'] == 'success':
            logger.info(f"✅ Test email sent successfully!")
            logger.info(f"Gmail Message ID: {result.get('gmail_message_id')}")
            return True
        else:
            logger.error(f"❌ Failed to send test email: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return False

def main():
    """Main function to setup and test Gmail integration"""
    
    print("🚀 Setting up Gmail OAuth for test email")
    print("=" * 50)
    
    # Setup credentials
    if setup_gmail_credentials():
        print("✅ OAuth credentials configured")
        
        # Send test email
        if send_test_email():
            print("✅ Test email sent to 1234.S.t.e.v.e.Glen@gmail.com")
        else:
            print("❌ Test email failed - check OAuth authentication")
    else:
        print("❌ Failed to setup OAuth credentials")
        print("Please ensure GOOGLE_CREDENTIALS environment variable is set with valid OAuth JSON")

if __name__ == "__main__":
    main()