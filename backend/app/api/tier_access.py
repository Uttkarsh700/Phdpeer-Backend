"""Subscription tier-based access helpers and decorators."""
from __future__ import annotations

from enum import IntEnum
from functools import wraps

from fastapi import HTTPException, status

from app.models.user import SubscriptionTier, User


class TierLevel(IntEnum):
    """Ordinal tier levels used for gating checks."""

    FREE = 1
    TEAM = 2
    INSTITUTIONAL = 3


_TIER_TO_LEVEL = {
    SubscriptionTier.FREE: TierLevel.FREE,
    SubscriptionTier.TEAM: TierLevel.TEAM,
    SubscriptionTier.INSTITUTIONAL: TierLevel.INSTITUTIONAL,
}


def has_required_tier(
    user_tier: SubscriptionTier,
    minimum_tier: SubscriptionTier,
) -> bool:
    """Return True when user's tier satisfies minimum required tier."""
    return _TIER_TO_LEVEL[user_tier] >= _TIER_TO_LEVEL[minimum_tier]


def assert_required_tier(user: User, minimum_tier: SubscriptionTier) -> None:
    """Raise 403 if user does not meet minimum required subscription tier."""
    if not has_required_tier(user.subscription_tier, minimum_tier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This endpoint requires '{minimum_tier.value}' tier or above",
        )


def requires_tier(minimum_tier: SubscriptionTier):
    """Decorator for endpoint functions expecting `current_user` keyword arg."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Tier check misconfiguration: current_user dependency missing",
                )
            assert_required_tier(current_user, minimum_tier)
            return await func(*args, **kwargs)

        return async_wrapper

    return decorator
