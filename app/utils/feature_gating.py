"""Feature gating utilities for progressive disclosure based on user groups"""
from functools import wraps
from typing import List, Callable
from fastapi import HTTPException, status
from app.models.user import UserGroup


def require_user_group(allowed_groups: List[UserGroup]) -> Callable:
    """
    Decorator to restrict API endpoints based on user group.

    Progressive feature disclosure: Different user groups see different features.
    - Amateur users: Simple interface, core features only
    - Farmers: Intermediate features
    - Researchers: Full access to all features

    Usage:
        @router.post("/hydroponic-gardens")
        @require_user_group([UserGroup.SCIENTIFIC_RESEARCHER])
        def create_hydroponic_garden(...):
            pass

    Args:
        allowed_groups: List of user groups that can access this endpoint

    Raises:
        HTTPException 403: If user's group is not in allowed_groups

    Example:
        # Only researchers can create hydroponic gardens
        @require_user_group([UserGroup.SCIENTIFIC_RESEARCHER])

        # Farmers and researchers can view soil samples
        @require_user_group([UserGroup.FARMER, UserGroup.SCIENTIFIC_RESEARCHER])
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs (injected by get_current_user dependency)
            current_user = kwargs.get('current_user')

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # Check if user's group is allowed
            if current_user.user_group not in allowed_groups:
                # Build helpful error message
                allowed_names = [group.value.replace('_', ' ').title() for group in allowed_groups]

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Feature not available for your account type",
                        "message": f"This feature requires: {', '.join(allowed_names)}",
                        "your_account_type": current_user.user_group.value.replace('_', ' ').title(),
                        "upgrade_info": "Change your account type in Settings to access advanced features"
                    }
                )

            # User is authorized, proceed with endpoint
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def get_feature_flags(user) -> dict:
    """
    Generate feature flags for frontend based on user group.

    Returns a dict of feature availability for the current user.
    Frontend can use this to hide/show features without making failed API calls.

    Args:
        user: User model instance

    Returns:
        Dict of feature_name -> enabled (bool)

    Example:
        {
            "hydroponics": False,          # Amateur: hidden
            "soil_samples_detailed": False, # Amateur: hidden
            "tree_shadows": False,          # Amateur: hidden (unless toggled)
            "companion_analysis": False,    # Amateur: info only
            "ec_ph_monitoring": False,      # Amateur: hidden
            "nutrient_optimization": False, # Amateur: hidden
        }
    """
    is_amateur = user.user_group == UserGroup.AMATEUR_GARDENER
    is_farmer = user.user_group == UserGroup.FARMER
    is_researcher = user.user_group == UserGroup.SCIENTIFIC_RESEARCHER

    return {
        # Core features (everyone)
        "gardens": True,
        "plants": True,
        "planting_dates": True,
        "days_to_harvest": True,
        "layout_visual": True,

        # Intermediate features (farmer+)
        "soil_samples": not is_amateur,
        "soil_samples_detailed": is_researcher,

        # Advanced features (researcher only)
        "hydroponics": is_researcher,
        "ec_ph_monitoring": is_researcher,
        "nutrient_optimization": is_researcher,
        "sensor_integration": is_researcher,
        "rule_engine_config": is_researcher,

        # Toggleable features (user preference)
        "tree_shadows": user.show_trees if is_amateur else True,
        "alerts_enabled": user.enable_alerts,

        # Feature transformations
        "companion_planting": True,  # Everyone sees it
        "companion_planting_mode": "info_only" if is_amateur else "analysis",
    }


def is_feature_enabled(user, feature_name: str) -> bool:
    """
    Check if a specific feature is enabled for the user.

    Args:
        user: User model instance
        feature_name: Feature identifier string

    Returns:
        True if feature is enabled for this user

    Example:
        if is_feature_enabled(user, "hydroponics"):
            # Show hydroponic options
    """
    flags = get_feature_flags(user)
    return flags.get(feature_name, False)
