"""
Payment and subscription management with Stripe
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from ..db import get_db
from ..models.user import User, SubscriptionTier
from ..dependencies import get_current_user
from ..config import settings

router = APIRouter()


# Pydantic schemas
class CreateCheckoutSessionRequest(BaseModel):
    tier: str  # solo_agent, pro_agent, team_brokerage
    success_url: str
    cancel_url: str


class SubscriptionResponse(BaseModel):
    tier: str
    status: str
    expires_at: Optional[datetime]
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]


@router.get("/payments/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription info"""
    return SubscriptionResponse(
        tier=current_user.subscription_tier.value,
        status=current_user.subscription_status,
        expires_at=current_user.subscription_expires_at,
        stripe_customer_id=current_user.stripe_customer_id,
        stripe_subscription_id=current_user.stripe_subscription_id
    )


@router.post("/payments/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription.
    
    - **tier**: Subscription tier to purchase
    - **success_url**: URL to redirect on success
    - **cancel_url**: URL to redirect on cancellation
    """
    # Validate tier
    tier_prices = {
        "solo_agent": 2900,  # $29.00 in cents
        "pro_agent": 4900,   # $49.00
        "team_brokerage": 14900  # $149.00
    }
    
    if request.tier not in tier_prices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription tier"
        )
    
    # Create actual Stripe checkout session
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.full_name,
                metadata={"user_id": current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.commit()
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'RealInbox AI - {request.tier.replace("_", " ").title()}',
                    },
                    'unit_amount': tier_prices[request.tier],
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                'user_id': current_user.id,
                'tier': request.tier
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id,
            "tier": request.tier,
            "price": tier_prices[request.tier] / 100
        }
        
    except Exception as e:
        # Fallback to mock if Stripe not configured
        if "API key" in str(e) or not settings.STRIPE_API_KEY:
            return {
                "checkout_url": "https://checkout.stripe.com/mock-session-configure-stripe",
                "session_id": "mock_session_id",
                "tier": request.tier,
                "price": tier_prices[request.tier] / 100,
                "note": "Stripe not configured - add STRIPE_API_KEY to .env"
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/payments/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription"""
    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )
    
    # Cancel Stripe subscription
    try:
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
        
        stripe.Subscription.modify(
            current_user.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update user
        current_user.subscription_status = "cancelled"
    except Exception as e:
        if "API key" not in str(e):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Stripe error: {str(e)}"
            )
        # If Stripe not configured, still update local status
        current_user.subscription_status = "cancelled"
    db.commit()
    
    return {
        "success": True,
        "message": "Subscription will end at current period end"
    }


@router.get("/payments/pricing")
async def get_pricing():
    """Get available pricing tiers"""
    return {
        "tiers": [
            {
                "id": "solo_agent",
                "name": "Solo Agent",
                "price_monthly": 29,
                "features": [
                    "1 email account",
                    "500 AI actions/month",
                    "Core features",
                    "Email support"
                ]
            },
            {
                "id": "pro_agent",
                "name": "Pro Agent",
                "price_monthly": 49,
                "features": [
                    "3 email accounts",
                    "Unlimited AI actions",
                    "Advanced analytics",
                    "Voice mode",
                    "Priority support"
                ],
                "popular": True
            },
            {
                "id": "team_brokerage",
                "name": "Team/Brokerage",
                "price_monthly": 149,
                "features": [
                    "Up to 5 agents",
                    "Unlimited AI actions",
                    "Team collaboration",
                    "Shared inbox",
                    "Team analytics",
                    "Dedicated support"
                ]
            }
        ]
    }

