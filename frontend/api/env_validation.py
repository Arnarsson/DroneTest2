"""
Environment variable validation for API endpoints.
Validates required environment variables at startup with clear error messages.
"""
import os
import sys
import logging

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = {
    'DATABASE_URL': {
        'description': 'Supabase PostgreSQL connection string',
        'format_hint': 'postgresql://user:password@host:port/database',
        'validate': lambda v: v.startswith(('postgresql://', 'postgres://')),
    },
    'INGEST_TOKEN': {
        'description': 'Bearer token for scraper authentication',
        'format_hint': 'Secret token string',
        'validate': lambda v: len(v) >= 16,  # Minimum security requirement
    },
}

OPTIONAL_ENV_VARS = {
    'OPENROUTER_API_KEY': {
        'description': 'OpenRouter API key for AI verification',
        'format_hint': 'sk-or-v1-...',
    },
    'OPENROUTER_MODEL': {
        'description': 'OpenRouter model to use',
        'default': 'openai/gpt-3.5-turbo',
    },
}


def validate_environment():
    """
    Validate all required environment variables.
    Raises ValueError with clear error message if validation fails.
    """
    errors = []
    warnings = []
    
    # Check required variables
    for var_name, config in REQUIRED_ENV_VARS.items():
        value = os.getenv(var_name)
        
        if not value:
            errors.append(
                f"❌ {var_name}: Missing (required)\n"
                f"   Description: {config['description']}\n"
                f"   Format: {config.get('format_hint', 'N/A')}\n"
                f"   Set in Vercel: Settings → Environment Variables"
            )
        elif 'validate' in config:
            try:
                if not config['validate'](value):
                    errors.append(
                        f"❌ {var_name}: Invalid format\n"
                        f"   Expected: {config.get('format_hint', 'N/A')}\n"
                        f"   Got: {value[:20]}..."
                    )
            except Exception as e:
                errors.append(
                    f"❌ {var_name}: Validation error: {str(e)}"
                )
        else:
            logger.debug(f"✅ {var_name}: Configured")
    
    # Check optional variables
    for var_name, config in OPTIONAL_ENV_VARS.items():
        value = os.getenv(var_name)
        if not value and 'default' not in config:
            warnings.append(
                f"⚠️  {var_name}: Not set (optional)\n"
                f"   Description: {config['description']}\n"
                f"   Default: {config.get('default', 'None')}"
            )
    
    # Report errors
    if errors:
        error_message = (
            "\n" + "=" * 70 + "\n"
            "ENVIRONMENT VALIDATION FAILED\n"
            "=" * 70 + "\n\n"
            + "\n\n".join(errors) + "\n\n"
            + "=" * 70 + "\n"
            "Fix these errors before deploying to production.\n"
            "=" * 70 + "\n"
        )
        logger.error(error_message)
        raise ValueError(error_message)
    
    # Report warnings (non-blocking)
    if warnings:
        warning_message = (
            "\n" + "=" * 70 + "\n"
            "ENVIRONMENT WARNINGS\n"
            "=" * 70 + "\n\n"
            + "\n\n".join(warnings) + "\n\n"
            + "=" * 70 + "\n"
        )
        logger.warning(warning_message)
    
    logger.info("✅ Environment validation passed")


def get_env_or_fail(var_name: str, description: str = None) -> str:
    """
    Get environment variable or raise clear error.
    
    Args:
        var_name: Environment variable name
        description: Optional description for error message
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        desc = f" ({description})" if description else ""
        raise ValueError(
            f"{var_name} environment variable not set{desc}. "
            f"Set it in Vercel: Settings → Environment Variables"
        )
    return value

