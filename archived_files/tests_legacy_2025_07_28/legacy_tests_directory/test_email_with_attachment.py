#!/usr/bin/env python3
"""
Test sending email with attachment using Gmail OAuth integration
"""

import os
import logging
from modules.email_integration.gmail_oauth_official import get_gmail_oauth_manager, get_gmail_sender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_attachment():
    """Create a simple test document attachment"""
    test_content = """Test Document for Gmail Attachment

This is a test document to verify that the automated job application system 
can successfully send emails with attachments from 1234.S.t.e.v.e.Glen@gmail.com.

System Details:
- Gmail OAuth Integration: OPERATIONAL
- Test Message ID: 1983525fe6f29567
- Sender: 1234.S.t.e.v.e.Glen@gmail.com
- Recipient: therealstevenglen@gmail.com

Date: July 23, 2025
Status: Testing attachment functionality
"""
    
    # Create test file
    test_file_path = "storage/test_attachment.txt"
    os.makedirs("storage", exist_ok=True)
    
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    return test_file_path

def main():
    print("📧 Testing Gmail attachment functionality...")
    
    try:
        # Create test attachment
        attachment_path = create_test_attachment()
        print(f"Created test attachment: {attachment_path}")
        
        # Get Gmail sender
        oauth_manager = get_gmail_oauth_manager()
        gmail_sender = get_gmail_sender(oauth_manager)
        
        # Prepare email data
        email_data = {
            'to_email': 'therealstevenglen@gmail.com',
            'subject': 'Test Email with Attachment - Automated Job Application System',
            'body': """Hello Steve,

This is a test email from your automated job application system to verify attachment functionality.

The system successfully completed Gmail OAuth integration and can now send emails with attachments from your 1234.S.t.e.v.e.Glen@gmail.com account.

Attached is a test document confirming the integration is working properly.

Best regards,
Your Automated Job Application System""",
            'attachment_path': attachment_path,
            'attachment_name': 'Gmail_Integration_Test.txt'
        }
        
        # Send email with attachment
        print("Sending email with attachment...")
        result = gmail_sender.send_email_with_attachment(
            to_email=email_data['to_email'],
            subject=email_data['subject'],
            body=email_data['body'],
            attachment_path=email_data['attachment_path'],
            attachment_name=email_data['attachment_name']
        )
        
        print(f"Email result: {result}")
        
        if result['status'] == 'success':
            print("✅ Email with attachment sent successfully!")
            print(f"Gmail Message ID: {result.get('gmail_message_id')}")
            print(f"From: 1234.S.t.e.v.e.Glen@gmail.com")
            print(f"To: {email_data['to_email']}")
            print(f"Attachment: {email_data['attachment_name']}")
            print("🎉 Attachment functionality verified!")
            return True
        else:
            print(f"❌ Email sending failed: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing attachment functionality: {e}")
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()