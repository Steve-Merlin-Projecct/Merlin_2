#!/usr/bin/env python3
"""
Complete Gmail OAuth with authorization code and send test email
"""

import os
import json
import logging
from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager, get_gmail_sender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    auth_code = '4/0AVMBsJhbSEjgUIv3Xe4atyioj2CmrIQlNiYyzDTpF21UdhB2jXYhFXXhcpbvqFmjmfcsgw'
    
    print("🔄 Completing OAuth flow with authorization code...")
    
    try:
        # Setup OAuth manager
        oauth_manager = get_gmail_oauth_manager()
        
        # Setup credentials
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
            print(f"Credentials setup: {setup_result['status']}")
        
        # Complete OAuth flow
        completion_result = oauth_manager.complete_oauth_flow(auth_code)
        print(f"OAuth completion: {completion_result}")
        
        if completion_result['status'] == 'success':
            print("✅ OAuth authentication completed successfully!")
            
            # Send test email
            print("📧 Sending test email to 1234.S.t.e.v.e.Glen@gmail.com...")
            gmail_sender = get_gmail_sender(oauth_manager)
            email_result = gmail_sender.send_test_email('1234.S.t.e.v.e.Glen@gmail.com')
            
            if email_result['status'] == 'success':
                print("✅ Test email sent successfully!")
                print(f"Gmail Message ID: {email_result.get('gmail_message_id')}")
                print("🎉 Your automated job application system Gmail integration is complete!")
                return True
            else:
                print(f"❌ Email sending failed: {email_result['message']}")
                return False
        else:
            print(f"❌ OAuth completion failed: {completion_result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"Error completing OAuth: {e}")
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()