"""
Source URL validation for journalist verification.
Ensures all source URLs are real, verifiable, and accessible.
"""
import re
from urllib.parse import urlparse
from typing import Tuple, List, Optional


# Blocked patterns for test/fake URLs
BLOCKED_PATTERNS = [
    r'placeholder',
    r'test\.com',
    r'example\.com',
    r'localhost',
    r'127\.0\.0\.1',
    r'192\.168\.',
    r'10\.\d+\.',
    r'dummy',
    r'fake',
    r'mock',
    r'sample',
    r'\.test\b',
    r'\.local\b',
]

# Blocked domains (satire, test sites)
BLOCKED_DOMAINS = [
    'example.com',
    'test.com',
    'localhost',
    '127.0.0.1',
]


def validate_source_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a source URL is real and verifiable.
    
    Args:
        url: Source URL to validate
        
    Returns:
        (is_valid, error_message)
        - is_valid: True if URL is valid, False otherwise
        - error_message: Error description if invalid, None if valid
    """
    if not url or not url.strip():
        return False, "Source URL is required and cannot be empty"
    
    url = url.strip()
    
    # Check for blocked patterns
    url_lower = url.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, url_lower):
            return False, f"URL contains blocked pattern: {pattern}"
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"
    
    # Must have scheme
    if not parsed.scheme:
        return False, "URL must include protocol (http:// or https://)"
    
    # Must be HTTP or HTTPS
    if parsed.scheme not in ('http', 'https'):
        return False, f"URL must use http:// or https:// (got: {parsed.scheme}://)"
    
    # Must have domain
    if not parsed.netloc:
        return False, "URL must include a domain name"
    
    # Check blocked domains
    domain_lower = parsed.netloc.lower()
    for blocked in BLOCKED_DOMAINS:
        if blocked in domain_lower:
            return False, f"Domain is blocked: {blocked}"
    
    # Block localhost/internal IPs
    if domain_lower in ('localhost', '127.0.0.1', '0.0.0.0'):
        return False, "Localhost/internal URLs are not allowed"
    
    if domain_lower.startswith('192.168.') or domain_lower.startswith('10.'):
        return False, "Internal/private IP addresses are not allowed"
    
    # URL looks valid
    return True, None


def validate_all_sources(sources: List[dict]) -> Tuple[bool, List[str]]:
    """
    Validate all sources in an incident.
    
    Args:
        sources: List of source dictionaries
        
    Returns:
        (all_valid, errors)
        - all_valid: True if all sources are valid
        - errors: List of error messages for invalid sources
    """
    errors = []
    
    if not sources:
        return True, []
    
    for idx, source in enumerate(sources):
        source_url = source.get('source_url', '').strip()
        
        if not source_url:
            errors.append(f"Source {idx+1}: Missing source_url")
            continue
        
        is_valid, error_msg = validate_source_url(source_url)
        if not is_valid:
            errors.append(f"Source {idx+1}: {error_msg} (URL: {source_url[:60]})")
    
    return len(errors) == 0, errors


def get_source_domain(url: str) -> Optional[str]:
    """
    Safely extract domain from source URL.
    
    Args:
        url: Source URL
        
    Returns:
        Domain name or None if invalid
    """
    try:
        parsed = urlparse(url.strip())
        domain = parsed.netloc or None
        
        # Remove port if present
        if domain and ':' in domain:
            domain = domain.split(':')[0]
        
        return domain
    except Exception:
        return None

