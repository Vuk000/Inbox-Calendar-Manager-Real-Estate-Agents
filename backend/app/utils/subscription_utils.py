"""Subscription utilities for tier limit checking and usage tracking"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from ..models.user import User, SubscriptionTier
from ..models.vision_scan import VisionScan
from ..models.neighborhood_report import NeighborhoodReport
from ..config import settings
from ..shared.exceptions import SubscriptionLimitException

logger = logging.getLogger(__name__)


def get_tier_limits(tier: SubscriptionTier) -> Dict[str, int]:
    """
    Get usage limits for a subscription tier.
    
    Args:
        tier: Subscription tier enum
        
    Returns:
        Dict with 'vision_scans' and 'neighborhood_searches' limits
    """
    if tier == SubscriptionTier.FREE_TRIAL:
        return {
            'vision_scans': settings.FREE_TIER_VISION_SCANS,
            'neighborhood_searches': settings.FREE_TIER_NEIGHBORHOOD_SEARCHES
        }
    elif tier == SubscriptionTier.SOLO_AGENT:
        return {
            'vision_scans': settings.SOLO_TIER_VISION_SCANS,
            'neighborhood_searches': settings.SOLO_TIER_NEIGHBORHOOD_SEARCHES
        }
    elif tier == SubscriptionTier.PRO_AGENT:
        return {
            'vision_scans': settings.PRO_TIER_VISION_SCANS,
            'neighborhood_searches': settings.PRO_TIER_NEIGHBORHOOD_SEARCHES
        }
    elif tier in [SubscriptionTier.TEAM_BROKERAGE, SubscriptionTier.ENTERPRISE]:
        # Unlimited for team/enterprise
        return {
            'vision_scans': 999999,  # Effectively unlimited
            'neighborhood_searches': 999999
        }
    else:
        # Default to free tier limits
        return {
            'vision_scans': settings.FREE_TIER_VISION_SCANS,
            'neighborhood_searches': settings.FREE_TIER_NEIGHBORHOOD_SEARCHES
        }


def get_monthly_usage(
    db: Session,
    user_id: int,
    feature: str  # 'vision_scans' or 'neighborhood_searches'
) -> int:
    """
    Get user's monthly usage count for a feature.
    
    Args:
        db: Database session
        user_id: User ID
        feature: Feature name ('vision_scans' or 'neighborhood_searches')
        
    Returns:
        Count of usage this month
    """
    # Get start of current month
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    if feature == 'vision_scans':
        count = db.query(func.count(VisionScan.id)).filter(
            and_(
                VisionScan.user_id == user_id,
                VisionScan.created_at >= month_start
            )
        ).scalar()
        return count or 0
    
    elif feature == 'neighborhood_searches':
        count = db.query(func.count(NeighborhoodReport.id)).filter(
            and_(
                NeighborhoodReport.user_id == user_id,
                NeighborhoodReport.created_at >= month_start
            )
        ).scalar()
        return count or 0
    
    return 0


def check_tier_limit(
    db: Session,
    user: User,
    feature: str,
    raise_exception: bool = True
) -> bool:
    """
    Check if user has reached their tier limit for a feature.
    
    Args:
        db: Database session
        user: User object
        feature: Feature name ('vision_scans' or 'neighborhood_searches')
        raise_exception: Whether to raise exception if limit reached
        
    Returns:
        True if within limit, False if limit reached
        
    Raises:
        SubscriptionLimitException: If limit reached and raise_exception=True
    """
    limits = get_tier_limits(user.subscription_tier)
    limit = limits.get(feature, 0)
    
    # Unlimited for team/enterprise
    if limit >= 999999:
        return True
    
    usage = get_monthly_usage(db, user.id, feature)
    
    if usage >= limit:
        if raise_exception:
            raise SubscriptionLimitException(
                message=f"{feature.replace('_', ' ').title()} limit reached for {user.subscription_tier.value} tier",
                feature=feature,
                limit=limit,
                current_usage=usage
            )
        return False
    
    return True


def can_access_feature(
    db: Session,
    user: User,
    feature: str,
    required_tier: Optional[str] = None  # 'pro' or 'team' for premium features
) -> bool:
    """
    Check if user can access a feature based on tier and limits.
    
    Args:
        db: Database session
        user: User object
        feature: Feature name
        required_tier: Optional minimum tier required ('pro' or 'team')
        
    Returns:
        True if user can access feature
    """
    # Check tier requirement
    if required_tier:
        simple_tier = user.get_simple_tier()
        tier_hierarchy = {'free': 1, 'solo': 2, 'pro': 3, 'team': 4}
        
        if tier_hierarchy.get(simple_tier, 0) < tier_hierarchy.get(required_tier, 0):
            return False
    
    # Check usage limits
    try:
        return check_tier_limit(db, user, feature, raise_exception=False)
    except SubscriptionLimitException:
        return False


def get_usage_summary(
    db: Session,
    user_id: int
) -> Dict[str, Any]:
    """
    Get comprehensive usage summary for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dict with usage stats and limits
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}
    
    limits = get_tier_limits(user.subscription_tier)
    
    vision_usage = get_monthly_usage(db, user_id, 'vision_scans')
    neighborhood_usage = get_monthly_usage(db, user_id, 'neighborhood_searches')
    
    return {
        'tier': user.get_simple_tier(),
        'subscription_tier': user.subscription_tier.value,
        'limits': limits,
        'usage': {
            'vision_scans': {
                'used': vision_usage,
                'limit': limits['vision_scans'],
                'remaining': max(0, limits['vision_scans'] - vision_usage) if limits['vision_scans'] < 999999 else -1
            },
            'neighborhood_searches': {
                'used': neighborhood_usage,
                'limit': limits['neighborhood_searches'],
                'remaining': max(0, limits['neighborhood_searches'] - neighborhood_usage) if limits['neighborhood_searches'] < 999999 else -1
            }
        }
    }

