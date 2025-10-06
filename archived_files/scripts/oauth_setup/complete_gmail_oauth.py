#!/usr/bin/env python3
"""
Complete Gmail OAuth Flow and Send Test Email
Automates the OAuth completion using local server flow
"""

import os
import json
import logging
from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager, get_gmail_sender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def complete_oauth_and_send_email():
    """Complete OAuth flow using local server and send test email"""
    
    try:
        oauth_manager = get_gmail_oauth_manager()
        
        # Check current status
        status = oauth_manager.get_oauth_status()
        logger.info(f"Current OAuth status: {status}")
        
        if not status['credentials_configured']:
            logger.error("OAuth credentials not configured")
            return False
        
        if not status['authenticated']:
            logger.info("Starting OAuth flow with local server...")
            
            # Complete OAuth flow using local server
            # This will open a browser and handle the callback automatically
            result = oauth_manager.complete_oauth_flow()
            
            if result['status'] == 'success':
                logger.info("✅ OAuth flow completed successfully!")
            else:
                logger.error(f"❌ OAuth flow failed: {result['message']}")
                return False
        
        # Verify authentication
        final_status = oauth_manager.get_oauth_status()
        if not final_status['authenticated']:
            logger.error("Authentication failed after OAuth flow")
            return False
        
        logger.info("✅ Gmail OAuth authentication successful!")
        
        # Send test email
        logger.info("Sending test email to therealstevenglen@gmail.com...")
        gmail_sender = get_gmail_sender(oauth_manager)
        
        result = gmail_sender.send_test_email("therealstevenglen@gmail.com")
        
        if result['status'] == 'success':
            logger.info("✅ Test email sent successfully!")
            logger.info(f"Gmail Message ID: {result.get('gmail_message_id')}")
            logger.info(f"Thread ID: {result.get('thread_id')}")
            return True
        else:
            logger.error(f"❌ Failed to send test email: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"Error in OAuth completion and email sending: {e}")
        return False

def main():
    """Main function to complete OAuth and send test email"""
    
    print("🚀 Completing Gmail OAuth and Sending Test Email")
    print("=" * 55)
    
    if complete_oauth_and_send_email():
        print("\n🎉 SUCCESS!")
        print("✅ Gmail OAuth authentication completed")
        print("✅ Test email sent to therealstevenglen@gmail.com")
        print("\n📧 Your automated job application system is ready!")
    else:
        print("\n❌ FAILED!")
        print("Please check the logs for error details")

if __name__ == "__main__":
    main()