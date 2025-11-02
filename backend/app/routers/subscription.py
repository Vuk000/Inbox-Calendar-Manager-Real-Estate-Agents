"""Subscription router - Subscription management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..utils.subscription_utils import get_usage_summary, get_tier_limits

router = APIRouter()


class UsageSummaryResponse(BaseModel):
    """Usage summary response"""
    tier: str
    subscription_tier: str
    limits: dict
    usage: dict


@router.get("/subscription/usage", response_model=UsageSummaryResponse)
async def get_usage_summary_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription usage summary"""
    summary = get_usage_summary(db, current_user.id)
    
    return UsageSummaryResponse(
        tier=summary.get('tier', 'free'),
        subscription_tier=summary.get('subscription_tier', 'free_trial'),
        limits=summary.get('limits', {}),
        usage=summary.get('usage', {})
    )


@router.get("/subscription/limits")
async def get_subscription_limits(
    current_user: User = Depends(get_current_user)
):
    """Get limits for current user's subscription tier"""
    limits = get_tier_limits(current_user.subscription_tier)
    
    return {
        "tier": current_user.get_simple_tier(),
        "subscription_tier": current_user.subscription_tier.value,
        "limits": limits,
        "is_premium": current_user.is_premium_tier()
    }


@router.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """Get current subscription status"""
    return {
        "tier": current_user.get_simple_tier(),
        "subscription_tier": current_user.subscription_tier.value,
        "status": current_user.subscription_status,
        "expires_at": current_user.subscription_expires_at.isoformat() if current_user.subscription_expires_at else None,
        "is_premium": current_user.is_premium_tier()
    }

