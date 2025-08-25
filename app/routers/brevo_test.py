from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..brevo_config import send_test_email, send_welcome_email

router = APIRouter(tags=["brevo"])

class TestEmailRequest(BaseModel):
    email: str

class WelcomeEmailRequest(BaseModel):
    user_email: str
    user_name: str
    media_board_name: str
    media_board_slug: str

@router.post("/test-email")
async def test_brevo_integration(request: TestEmailRequest):
    """Test Brevo email integration by sending a test email"""
    try:
        result = send_test_email(request.email)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Test email sent successfully",
                "message_id": result["message_id"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send test email: {result['error']}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing Brevo integration: {str(e)}"
        )

@router.post("/welcome-email")
async def send_welcome_email_endpoint(request: WelcomeEmailRequest):
    """Send welcome email to media board purchaser"""
    try:
        result = send_welcome_email(
            user_email=request.user_email,
            user_name=request.user_name,
            media_board_name=request.media_board_name,
            media_board_slug=request.media_board_slug
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Welcome email sent successfully",
                "message_id": result["message_id"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send welcome email: {result['error']}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending welcome email: {str(e)}"
        )

@router.get("/health")
async def brevo_health_check():
    """Health check for Brevo integration"""
    return {
        "status": "healthy",
        "service": "Brevo Email Integration",
        "message": "Brevo API is configured and ready"
    }
