"""
Text validation and sanitization for incident title and narrative fields.
Provides defense-in-depth protection against XSS and other injection attacks.
"""
import re
import html
import unicodedata
from typing import Tuple, Optional


# Maximum allowed lengths for text fields
MAX_TITLE_LENGTH = 500
MAX_NARRATIVE_LENGTH = 10000


# Control character pattern (C0 and C1 control chars, excluding newline/tab)
# \x00-\x08: C0 controls (NUL to BS)
# \x0b-\x0c: VT and FF
# \x0e-\x1f: SO to US
# \x7f: DEL
# \x80-\x9f: C1 controls
CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\x80-\x9f]')

# HTML/XML tag pattern - matches opening, closing, and self-closing tags
HTML_TAG_PATTERN = re.compile(r'<[^>]+>', re.IGNORECASE)

# HTML comments pattern
HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.IGNORECASE | re.DOTALL)

# CDATA section pattern
CDATA_PATTERN = re.compile(r'<!\[CDATA\[.*?\]\]>', re.IGNORECASE | re.DOTALL)


def validate_text_length(text: str, max_length: int, field_name: str = "text") -> Tuple[bool, Optional[str]]:
    """
    Validate that text does not exceed maximum length.

    Args:
        text: Text to validate
        max_length: Maximum allowed length in characters
        field_name: Name of the field for error messages

    Returns:
        (is_valid, error_message)
        - is_valid: True if text is within length limit
        - error_message: Error description if invalid, None if valid
    """
    if text is None:
        return True, None

    if not isinstance(text, str):
        return False, f"{field_name} must be a string"

    text_length = len(text)
    if text_length > max_length:
        return False, f"{field_name} exceeds maximum length ({text_length} > {max_length} characters)"

    return True, None


def strip_html_tags(text: str) -> str:
    """
    Remove HTML/XML tags, comments, and CDATA sections from text.

    Args:
        text: Text potentially containing HTML/XML markup

    Returns:
        Text with all HTML/XML elements removed
    """
    if not text:
        return text

    # Remove HTML comments first (may contain tags)
    result = HTML_COMMENT_PATTERN.sub('', text)

    # Remove CDATA sections
    result = CDATA_PATTERN.sub('', result)

    # Remove all HTML/XML tags
    result = HTML_TAG_PATTERN.sub('', result)

    # Decode HTML entities to their character equivalents
    # This converts &lt; to <, &amp; to &, etc.
    result = html.unescape(result)

    return result


def remove_control_characters(text: str) -> str:
    """
    Remove control characters from text while preserving newlines and tabs.

    Args:
        text: Text potentially containing control characters

    Returns:
        Text with control characters removed
    """
    if not text:
        return text

    return CONTROL_CHAR_PATTERN.sub('', text)


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode text using NFC (Canonical Decomposition, followed by Canonical Composition).

    This ensures consistent representation of characters that can be represented
    in multiple ways (e.g., é as single char vs e + combining accent).

    Args:
        text: Text to normalize

    Returns:
        Unicode-normalized text
    """
    if not text:
        return text

    return unicodedata.normalize('NFC', text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text:
    - Replace multiple spaces with single space
    - Trim leading/trailing whitespace
    - Preserve single newlines but collapse multiple newlines

    Args:
        text: Text with potentially excessive whitespace

    Returns:
        Text with normalized whitespace
    """
    if not text:
        return text

    # Replace multiple spaces (not newlines) with single space
    result = re.sub(r'[^\S\n]+', ' ', text)

    # Collapse multiple newlines to double newline (paragraph break)
    result = re.sub(r'\n{3,}', '\n\n', result)

    # Strip leading/trailing whitespace
    result = result.strip()

    return result


def sanitize_text(text: str) -> str:
    """
    Apply full sanitization pipeline to text.

    Pipeline:
    1. Unicode normalization (NFC)
    2. Remove control characters
    3. Strip HTML tags and decode entities
    4. Normalize whitespace

    Args:
        text: Raw text to sanitize

    Returns:
        Fully sanitized text
    """
    if not text:
        return text if text is not None else ''

    if not isinstance(text, str):
        text = str(text)

    # Step 1: Unicode normalization
    result = normalize_unicode(text)

    # Step 2: Remove control characters
    result = remove_control_characters(result)

    # Step 3: Strip HTML tags and decode entities
    result = strip_html_tags(result)

    # Step 4: Normalize whitespace
    result = normalize_whitespace(result)

    return result


def detect_xss_patterns(text: str) -> Tuple[bool, Optional[str]]:
    """
    Detect common XSS attack patterns in text.

    This is a basic detection for obvious XSS patterns.
    Full XSS detection is implemented in subtask 1.2.

    Args:
        text: Text to analyze for XSS patterns

    Returns:
        (is_safe, warning_message)
        - is_safe: True if no XSS patterns detected
        - warning_message: Description of detected pattern, None if safe
    """
    if not text:
        return True, None

    text_lower = text.lower()

    # Check for script tags
    if re.search(r'<\s*script', text_lower):
        return False, "Detected <script> tag"

    # Check for common event handlers
    event_handlers = [
        'onclick', 'onerror', 'onload', 'onmouseover', 'onfocus',
        'onblur', 'onchange', 'onsubmit', 'onkeydown', 'onkeyup'
    ]
    for handler in event_handlers:
        if re.search(rf'{handler}\s*=', text_lower):
            return False, f"Detected event handler: {handler}"

    # Check for javascript: URI
    if re.search(r'javascript\s*:', text_lower):
        return False, "Detected javascript: URI scheme"

    # Check for data: URI with executable types
    if re.search(r'data\s*:\s*(text/html|application/javascript|text/javascript)', text_lower):
        return False, "Detected potentially dangerous data: URI"

    # Check for vbscript: (IE legacy)
    if re.search(r'vbscript\s*:', text_lower):
        return False, "Detected vbscript: URI scheme"

    return True, None
