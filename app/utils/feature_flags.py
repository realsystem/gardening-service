"""Feature flag service for runtime control of features.

Provides:
- Runtime feature flag checking
- Flag reload without restart
- Fail-safe defaults
- Metrics for flag usage

Feature flags allow disabling features at runtime for:
- Incident response (disable broken features)
- Gradual rollouts
- A/B testing
- Load shedding during high traffic
"""
import os
import logging
from typing import Dict, Optional
from datetime import datetime
from functools import lru_cache

from app.config import get_settings
from app.utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class FeatureFlags:
    """Service for checking feature flags with runtime reload capability.

    Flags can be controlled via:
    1. Environment variables (primary source)
    2. Runtime reload via admin endpoint

    All flags default to True (features enabled) for fail-safe behavior.
    Flags should disable features, not enable them.
    """

    # Cache for loaded flags
    _cached_flags: Optional[Dict[str, bool]] = None
    _last_reload: Optional[datetime] = None

    # Flag definitions with fail-safe defaults
    FLAG_DEFINITIONS = {
        'FEATURE_RULE_ENGINE_ENABLED': {
            'default': True,
            'description': 'Enable automatic task generation via rule engine',
            'fail_safe': True,  # Fail open - rules enabled by default
        },
        'FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED': {
            'default': True,
            'description': 'Enable compliance blocking (403 responses)',
            'fail_safe': True,  # Fail closed - compliance enabled by default
        },
        'FEATURE_OPTIMIZATION_ENGINES_ENABLED': {
            'default': True,
            'description': 'Enable optimization features (nutrient, shading, etc.)',
            'fail_safe': True,  # Fail open - optimizations enabled by default
        },
    }

    @classmethod
    def reload(cls) -> Dict[str, bool]:
        """Reload feature flags from environment/settings.

        Returns:
            Dictionary of current flag states
        """
        settings = get_settings()

        flags = {}
        for flag_name, flag_def in cls.FLAG_DEFINITIONS.items():
            # Get from settings (which reads from env)
            value = getattr(settings, flag_name, flag_def['default'])

            # Convert string to bool if needed (env vars are strings)
            if isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 'on')

            flags[flag_name] = bool(value)

        cls._cached_flags = flags
        cls._last_reload = datetime.utcnow()

        logger.info(
            "Feature flags reloaded",
            extra={
                'flags': flags,
                'reload_time': cls._last_reload.isoformat()
            }
        )

        return flags

    @classmethod
    def get_flags(cls) -> Dict[str, bool]:
        """Get current feature flags (cached).

        Returns:
            Dictionary of flag name -> enabled status
        """
        if cls._cached_flags is None:
            cls.reload()

        return cls._cached_flags.copy()

    @classmethod
    def is_enabled(cls, flag_name: str) -> bool:
        """Check if a feature flag is enabled.

        Args:
            flag_name: Name of the flag to check

        Returns:
            True if flag is enabled, False otherwise

        Note:
            Unknown flags default to their fail-safe value.
        """
        flags = cls.get_flags()

        # If flag not in cache, use fail-safe default
        if flag_name not in flags:
            flag_def = cls.FLAG_DEFINITIONS.get(flag_name, {})
            default_value = flag_def.get('fail_safe', True)

            logger.warning(
                f"Unknown feature flag '{flag_name}', using fail-safe default: {default_value}"
            )

            return default_value

        return flags[flag_name]

    @classmethod
    def get_status(cls) -> Dict[str, any]:
        """Get full status of feature flag system.

        Returns:
            Dictionary with flags, metadata, and reload info
        """
        flags = cls.get_flags()

        return {
            'flags': flags,
            'last_reload': cls._last_reload.isoformat() if cls._last_reload else None,
            'definitions': cls.FLAG_DEFINITIONS,
        }


# Convenience functions for checking specific flags

def is_rule_engine_enabled() -> bool:
    """Check if rule engine is enabled.

    Returns:
        True if rule engine should generate tasks
    """
    return FeatureFlags.is_enabled('FEATURE_RULE_ENGINE_ENABLED')


def is_compliance_enforcement_enabled() -> bool:
    """Check if compliance enforcement is enabled.

    Returns:
        True if compliance violations should block requests (403)
        False if violations should only be logged
    """
    return FeatureFlags.is_enabled('FEATURE_COMPLIANCE_ENFORCEMENT_ENABLED')


def is_optimization_engines_enabled() -> bool:
    """Check if optimization engines are enabled.

    Returns:
        True if optimization features should be available
    """
    return FeatureFlags.is_enabled('FEATURE_OPTIMIZATION_ENGINES_ENABLED')


def reload_feature_flags() -> Dict[str, bool]:
    """Reload feature flags from environment/config.

    Returns:
        Dictionary of reloaded flags
    """
    return FeatureFlags.reload()


def get_feature_flag_status() -> Dict[str, any]:
    """Get complete feature flag status.

    Returns:
        Status dictionary with all flags and metadata
    """
    return FeatureFlags.get_status()
