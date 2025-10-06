#!/usr/bin/env python3
"""
Manual OAuth Completion for Gmail Integration
Allows manual input of authorization code to complete OAuth flow
"""

import os
import json
import logging
from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager, get_gmail_sender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def complete_oauth_with_code():
    """Complete OAuth flow with manually entered authorization code"""
    
    try:
        # Setup OAuth manager
        oauth_manager = get_gmail_oauth_manager()
        
        # Setup credentials first
        google_creds = os.environ.get('GOOGLE_CREDENTIALS')
        if google_creds:
            creds_data = json.loads(google_creds)
            if 'installed' in creds_data:
                client_id = creds_data['installed']['client_id']
                client_secret = creds_data['installed']['client_secret']
            else:
                client_id = creds_data['client_id']
                client_secret = creds_data['client_secret']
            
            setup_result = oauth_manager.setup_oauth_credentials(client_id, client_secret)
            if setup_result['status'] != 'success':
                print(f"❌ Failed to setup credentials: {setup_result['message']}")
                return False
        
        # Get authorization URL
        auth_result = oauth_manager.get_authorization_url()
        if auth_result['status'] != 'success':
            print(f"❌ Failed to get authorization URL: {auth_result['message']}")
            return False
        
        print("🔗 AUTHORIZATION URL:")
        print(auth_result['authorization_url'])
        print()
        print("📋 INSTRUCTIONS:")
        print("1. Click the authorization URL above")
        print("2. Sign in to 1234.S.t.e.v.e.Glen@gmail.com")
        print("3. Grant Gmail permissions")
        print("4. Copy the authorization code from the callback URL")
        print("5. Enter the code below when prompted")
        print()
        
        # Get authorization code from user
        auth_code = input("Enter the authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return False
        
        # Complete OAuth flow
        completion_result = oauth_manager.exchange_code_for_tokens(auth_code)
        
        if completion_result['status'] == 'success':
            print("✅ OAuth authentication completed successfully!")
            
            # Send test email
            print("📧 Sending test email to 1234.S.t.e.v.e.Glen@gmail.com...")
            gmail_sender = get_gmail_sender(oauth_manager)
            email_result = gmail_sender.send_test_email("1234.S.t.e.v.e.Glen@gmail.com")
            
            if email_result['status'] == 'success':
                print("✅ Test email sent successfully!")
                print(f"Gmail Message ID: {email_result.get('gmail_message_id')}")
                print("🎉 Your automated job application system is ready!")
                return True
            else:
                print(f"❌ Email sending failed: {email_result['message']}")
                return False
        else:
            print(f"❌ OAuth completion failed: {completion_result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"OAuth completion error: {e}")
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Gmail OAuth Manual Completion")
    print("=" * 40)
    complete_oauth_with_code()