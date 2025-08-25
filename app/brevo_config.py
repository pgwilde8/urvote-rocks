import os
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail, SendSmtpEmailTo, SendSmtpEmailSender

# Brevo API Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "your-api-key-here")

# Configure Brevo API
configuration = Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY

# Create API client
api_client = ApiClient(configuration)
transactional_api = TransactionalEmailsApi(api_client)

def send_welcome_email(user_email: str, user_name: str, media_board_name: str, media_board_slug: str):
    """Send welcome email to media board purchaser"""
    try:
        # Create email content
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to UrVote.Rocks! 🎉</h2>
            <p>Hi {user_name},</p>
            <p>Thank you for purchasing a Media Board: <strong>{media_board_name}</strong></p>
            <p>Your Media Board is now live at: <a href="https://urvote.rocks/board/{media_board_slug}">https://urvote.rocks/board/{media_board_slug}</a></p>
            <p>Start uploading content and engaging your community!</p>
            <br>
            <p>Best regards,<br>The UrVote.Rocks Team</p>
        </body>
        </html>
        """
        
        # Create email
        send_smtp_email = SendSmtpEmail(
            to=[SendSmtpEmailTo(email=user_email, name=user_name)],
            sender=SendSmtpEmailSender(email="noreply@urvote.rocks", name="UrVote.Rocks"),
            subject=f"Welcome to UrVote.Rocks - {media_board_name}",
            html_content=html_content
        )
        
        # Send email
        api_response = transactional_api.send_transac_email(send_smtp_email)
        
        return {
            "success": True,
            "message_id": api_response.message_id,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }

def send_test_email(test_email: str):
    """Send test email to verify Brevo integration"""
    try:
        # Create email content
        html_content = """
        <html>
        <body>
            <h2>Brevo Integration Test ✅</h2>
            <p>This is a test email from UrVote.Rocks to verify the Brevo integration is working.</p>
            <p>If you receive this, the email system is configured correctly!</p>
            <br>
            <p>Best regards,<br>UrVote.Rocks Team</p>
        </body>
        </html>
        """
        
        # Create email
        send_smtp_email = SendSmtpEmail(
            to=[SendSmtpEmailTo(email=test_email, name="Test User")],
            sender=SendSmtpEmailSender(email="noreply@urvote.rocks", name="UrVote.Rocks"),
            subject="Brevo Integration Test - UrVote.Rocks",
            html_content=html_content
        )
        
        # Send email
        api_response = transactional_api.send_transac_email(send_smtp_email)
        
        return {
            "success": True,
            "message_id": api_response.message_id,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }
