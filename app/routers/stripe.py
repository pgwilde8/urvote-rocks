import stripe
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.models import User
from app.auth import get_current_user  # Adjust import as needed
from app.config import settings  # Adjust as needed

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY  # Set your secret key

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": settings.STRIPE_PRICE_ID,  # Your Stripe Price ID for the membership
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://yourdomain.com/cancel",
            metadata={"user_id": current_user.id}
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))