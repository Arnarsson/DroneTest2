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


# ============================================================================
# XSS Detection Patterns
# ============================================================================

# All known event handler attributes (comprehensive list)
EVENT_HANDLERS = [
    # Mouse events
    'onclick', 'ondblclick', 'onmousedown', 'onmouseup', 'onmouseover',
    'onmousemove', 'onmouseout', 'onmouseenter', 'onmouseleave', 'onwheel',
    'oncontextmenu',
    # Keyboard events
    'onkeydown', 'onkeyup', 'onkeypress',
    # Form events
    'onfocus', 'onblur', 'onchange', 'oninput', 'onsubmit', 'onreset',
    'oninvalid', 'onselect', 'onsearch',
    # Window/Document events
    'onload', 'onunload', 'onbeforeunload', 'onresize', 'onscroll',
    'onhashchange', 'onpopstate', 'onpageshow', 'onpagehide', 'onbeforeprint',
    'onafterprint', 'ononline', 'onoffline', 'onmessage', 'onstorage',
    # Media events
    'onplay', 'onpause', 'onplaying', 'onended', 'onvolumechange',
    'onseeking', 'onseeked', 'ontimeupdate', 'ondurationchange',
    'onratechange', 'onloadstart', 'onprogress', 'onsuspend', 'onemptied',
    'onstalled', 'onwaiting', 'oncanplay', 'oncanplaythrough', 'onloadeddata',
    'onloadedmetadata', 'onabort',
    # Drag events
    'ondrag', 'ondragstart', 'ondragend', 'ondragenter', 'ondragleave',
    'ondragover', 'ondrop',
    # Clipboard events
    'oncopy', 'oncut', 'onpaste',
    # Touch events
    'ontouchstart', 'ontouchmove', 'ontouchend', 'ontouchcancel',
    # Animation/Transition events
    'onanimationstart', 'onanimationend', 'onanimationiteration',
    'ontransitionend', 'ontransitionstart', 'ontransitioncancel', 'ontransitionrun',
    # Error events
    'onerror',
    # Pointer events
    'onpointerdown', 'onpointerup', 'onpointermove', 'onpointerenter',
    'onpointerleave', 'onpointerover', 'onpointerout', 'onpointercancel',
    'ongotpointercapture', 'onlostpointercapture',
    # Print events
    'onbeforeprint', 'onafterprint',
    # Toggle events
    'ontoggle',
    # Security-related
    'onsecuritypolicyviolation',
    # Fullscreen
    'onfullscreenchange', 'onfullscreenerror',
    # WebSocket
    'onopen', 'onclose',
]

# Dangerous HTML tags that can execute JavaScript
DANGEROUS_TAGS = [
    'script', 'iframe', 'frame', 'frameset', 'object', 'embed', 'applet',
    'form', 'input', 'button', 'select', 'textarea', 'isindex', 'keygen',
    'svg', 'math', 'video', 'audio', 'source', 'img', 'body', 'link',
    'style', 'base', 'meta', 'marquee', 'bgsound', 'xml', 'xss', 'template',
]

# Dangerous URI schemes
DANGEROUS_URI_SCHEMES = [
    'javascript',
    'vbscript',
    'livescript',
    'mocha',
    'data',
    'mhtml',
]

# CSS dangerous expressions/properties
CSS_DANGEROUS_PATTERNS = [
    r'expression\s*\(',  # IE CSS expression
    r'url\s*\(\s*["\']?\s*javascript:',  # CSS url() with javascript
    r'behavior\s*:',  # IE behavior
    r'-moz-binding\s*:',  # Firefox XBL
    r'@import',  # CSS import
]


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


def _decode_url_encoded(text: str) -> str:
    """
    Decode URL-encoded strings (percent encoding).

    Handles both single and double encoding attempts.

    Args:
        text: Text potentially containing URL-encoded characters

    Returns:
        Decoded text
    """
    import urllib.parse

    result = text
    # Attempt up to 3 levels of decoding for nested encoding attacks
    for _ in range(3):
        try:
            decoded = urllib.parse.unquote(result)
            if decoded == result:
                break
            result = decoded
        except Exception:
            break
    return result


def _decode_html_entities(text: str) -> str:
    """
    Decode HTML entities including numeric and named entities.

    Handles decimal (&#60;), hex (&#x3c;), and named (&lt;) entities.

    Args:
        text: Text potentially containing HTML entities

    Returns:
        Decoded text
    """
    result = text

    # Decode hex entities: &#x3c; or &#X3C;
    def decode_hex(match):
        try:
            return chr(int(match.group(1), 16))
        except (ValueError, OverflowError):
            return match.group(0)

    result = re.sub(r'&#[xX]([0-9a-fA-F]+);?', decode_hex, result)

    # Decode decimal entities: &#60;
    def decode_decimal(match):
        try:
            return chr(int(match.group(1)))
        except (ValueError, OverflowError):
            return match.group(0)

    result = re.sub(r'&#(\d+);?', decode_decimal, result)

    # Named entities using html.unescape
    result = html.unescape(result)

    return result


def _normalize_for_detection(text: str) -> Tuple[str, str]:
    """
    Normalize text for XSS pattern detection.

    Applies multiple decodings and normalizations to catch obfuscated attacks.

    Args:
        text: Text to normalize

    Returns:
        Tuple of (normalized_text, normalized_text_no_space) both lowercase
    """
    if not text:
        return "", ""

    # Remove null bytes and other common obfuscation chars
    result = re.sub(r'[\x00\x0d]', '', text)

    # Remove backslashes used for obfuscation
    result = result.replace('\\', '')

    # Decode URL encoding
    result = _decode_url_encoded(result)

    # Decode HTML entities
    result = _decode_html_entities(result)

    # Remove whitespace/newlines that might be used to break up keywords
    # But preserve for pattern matching where whitespace matters
    result_no_space = re.sub(r'[\s\r\n\t]+', '', result)

    return result.lower(), result_no_space.lower()


def detect_xss_patterns(text: str) -> Tuple[bool, Optional[str]]:
    """
    Detect comprehensive XSS attack patterns in text.

    Checks for:
    - Script tags and variants (obfuscated, encoded)
    - All event handlers (onclick, onerror, etc.)
    - Dangerous URI schemes (javascript:, vbscript:, data:, etc.)
    - URL-encoded and HTML entity-encoded variants
    - SVG/MathML vector attacks
    - CSS expression attacks
    - Other injection vectors

    Args:
        text: Text to analyze for XSS patterns

    Returns:
        (is_safe, warning_message)
        - is_safe: True if no XSS patterns detected
        - warning_message: Description of detected pattern, None if safe
    """
    if not text:
        return True, None

    # Get normalized versions for detection
    text_normalized, text_no_space = _normalize_for_detection(text)
    text_original_lower = text.lower()

    # =========================================================================
    # 1. Check for dangerous HTML tags
    # =========================================================================
    for tag in DANGEROUS_TAGS:
        # Pattern matches: <script, < script, <script/, </script, etc.
        # Allows whitespace between < and tag name
        pattern = rf'<\s*/?{tag}[\s/>]'
        if re.search(pattern, text_normalized) or re.search(pattern, text_no_space):
            return False, f"Detected dangerous HTML tag: <{tag}>"

    # =========================================================================
    # 2. Check for event handlers
    # =========================================================================
    for handler in EVENT_HANDLERS:
        # Pattern matches: onclick=, onclick =, onclick  =
        # Using normalized text to catch encoded variants
        pattern = rf'{handler}\s*='
        if re.search(pattern, text_normalized):
            return False, f"Detected event handler: {handler}"
        # Also check without spaces for obfuscated variants
        if f'{handler}=' in text_no_space:
            return False, f"Detected event handler: {handler}"

    # =========================================================================
    # 3. Check for dangerous URI schemes
    # =========================================================================
    for scheme in DANGEROUS_URI_SCHEMES:
        # Pattern matches: javascript:, java script:, java	script:
        # Allow any whitespace/null bytes between chars (obfuscation technique)
        pattern = rf'{scheme}\s*:'
        if re.search(pattern, text_normalized):
            # Special handling for data: - only flag if it's a dangerous MIME type
            if scheme == 'data':
                # Check for dangerous data: URI content types
                dangerous_data_types = [
                    r'data\s*:\s*text/html',
                    r'data\s*:\s*application/javascript',
                    r'data\s*:\s*text/javascript',
                    r'data\s*:\s*application/x-javascript',
                    r'data\s*:\s*text/vbscript',
                    r'data\s*:\s*text/x-scriptlet',
                    r'data\s*:\s*image/svg\+xml',
                ]
                for data_pattern in dangerous_data_types:
                    if re.search(data_pattern, text_normalized):
                        return False, f"Detected dangerous data: URI with executable content"
                # Also check for base64 encoded payloads in data URIs
                if re.search(r'data\s*:[^;,]*;?\s*base64', text_normalized):
                    return False, "Detected data: URI with base64 encoding"
            else:
                return False, f"Detected dangerous URI scheme: {scheme}:"

        # Check obfuscated variants (with chars between letters)
        obfuscated = r'[\s\x00]*'.join(list(scheme))
        if re.search(rf'{obfuscated}\s*:', text_original_lower):
            return False, f"Detected obfuscated URI scheme: {scheme}:"

    # =========================================================================
    # 4. Check for CSS-based attacks
    # =========================================================================
    for css_pattern in CSS_DANGEROUS_PATTERNS:
        if re.search(css_pattern, text_normalized, re.IGNORECASE):
            return False, "Detected dangerous CSS pattern"

    # =========================================================================
    # 5. Check for SVG-specific attacks
    # =========================================================================
    svg_patterns = [
        r'<\s*svg[^>]*\s+onload\s*=',  # SVG with onload
        r'<\s*svg[^>]*>.*?<\s*script',  # SVG containing script
        r'<\s*svg[^>]*>.*?<\s*animate[^>]*\s+on',  # SVG animate with event
        r'<\s*svg[^>]*>.*?<\s*set[^>]*\s+on',  # SVG set with event
        r'<\s*svg[^>]*>.*?<\s*foreignobject',  # SVG foreignObject
    ]
    for svg_pattern in svg_patterns:
        if re.search(svg_pattern, text_normalized, re.DOTALL):
            return False, "Detected SVG-based XSS vector"

    # =========================================================================
    # 6. Check for MathML attacks
    # =========================================================================
    mathml_patterns = [
        r'<\s*math[^>]*>.*?<\s*annotation-xml[^>]*>.*?<\s*svg',
        r'<\s*math[^>]*\s+on\w+\s*=',  # MathML with event handler
    ]
    for math_pattern in mathml_patterns:
        if re.search(math_pattern, text_normalized, re.DOTALL):
            return False, "Detected MathML-based XSS vector"

    # =========================================================================
    # 7. Check for other injection patterns
    # =========================================================================
    other_patterns = [
        (r'<!--.*?<\s*script', "Detected script tag hidden in HTML comment"),
        (r'<\s*meta[^>]*http-equiv\s*=\s*["\']?refresh', "Detected meta refresh injection"),
        (r'<\s*link[^>]*rel\s*=\s*["\']?import', "Detected HTML import injection"),
        (r'srcdoc\s*=', "Detected srcdoc attribute (potential iframe injection)"),
        (r'xlink:href\s*=', "Detected xlink:href attribute"),
        (r'formaction\s*=', "Detected formaction attribute"),
        (r'action\s*=\s*["\']?\s*javascript:', "Detected javascript in form action"),
        (r'href\s*=\s*["\']?\s*javascript:', "Detected javascript in href"),
        (r'src\s*=\s*["\']?\s*javascript:', "Detected javascript in src"),
        (r'poster\s*=\s*["\']?\s*javascript:', "Detected javascript in poster"),
        (r'background\s*=\s*["\']?\s*javascript:', "Detected javascript in background"),
    ]
    for pattern, message in other_patterns:
        if re.search(pattern, text_normalized, re.DOTALL | re.IGNORECASE):
            return False, message

    # =========================================================================
    # 8. Check for DOM clobbering patterns
    # =========================================================================
    dom_patterns = [
        r'<\s*(?:form|input|img|a)[^>]*\s+(?:id|name)\s*=\s*["\']?(?:location|document|window)',
    ]
    for dom_pattern in dom_patterns:
        if re.search(dom_pattern, text_normalized):
            return False, "Detected potential DOM clobbering pattern"

    # =========================================================================
    # 9. Check for encoded patterns that survived normalization
    # =========================================================================
    # Look for suspicious URL encoding patterns that might indicate obfuscation
    encoded_patterns = [
        (r'%[0-9a-f]{2}', 3),  # If many URL-encoded chars remain, suspicious
    ]
    for pattern, threshold in encoded_patterns:
        matches = re.findall(pattern, text_original_lower)
        if len(matches) >= threshold:
            # Check if the encoded content is suspicious after decode
            decoded = _decode_url_encoded(text)
            if decoded != text:
                is_safe, msg = detect_xss_patterns(decoded)
                if not is_safe:
                    return False, f"Detected URL-encoded XSS: {msg}"

    return True, None


def validate_title(title: Optional[str]) -> Tuple[bool, str, Optional[str]]:
    """
    Validate and sanitize incident title field.

    Applies:
    - Length validation (max 500 characters)
    - Full text sanitization (unicode normalization, control char removal,
      HTML stripping, whitespace normalization)
    - XSS pattern detection

    Args:
        title: Raw title text from user input (may be None)

    Returns:
        (is_valid, sanitized_title, error_message)
        - is_valid: True if title is valid and safe
        - sanitized_title: Cleaned title text (empty string if None/empty input)
        - error_message: Error description if invalid, None if valid
    """
    # Handle None/empty values gracefully
    if title is None or (isinstance(title, str) and not title.strip()):
        return True, '', None

    # Ensure it's a string
    if not isinstance(title, str):
        return False, '', "Title must be a string"

    # Apply sanitization first
    sanitized = sanitize_text(title)

    # Check length after sanitization
    is_valid_length, length_error = validate_text_length(
        sanitized, MAX_TITLE_LENGTH, "Title"
    )
    if not is_valid_length:
        return False, sanitized, length_error

    # Check for XSS patterns in original text (before sanitization stripped them)
    is_safe, xss_warning = detect_xss_patterns(title)
    if not is_safe:
        return False, sanitized, f"Title contains potentially malicious content: {xss_warning}"

    return True, sanitized, None


def validate_narrative(narrative: Optional[str]) -> Tuple[bool, str, Optional[str]]:
    """
    Validate and sanitize incident narrative field.

    Applies:
    - Length validation (max 10000 characters)
    - Full text sanitization (unicode normalization, control char removal,
      HTML stripping, whitespace normalization)
    - XSS pattern detection

    Args:
        narrative: Raw narrative text from user input (may be None)

    Returns:
        (is_valid, sanitized_narrative, error_message)
        - is_valid: True if narrative is valid and safe
        - sanitized_narrative: Cleaned narrative text (empty string if None/empty input)
        - error_message: Error description if invalid, None if valid
    """
    # Handle None/empty values gracefully
    if narrative is None or (isinstance(narrative, str) and not narrative.strip()):
        return True, '', None

    # Ensure it's a string
    if not isinstance(narrative, str):
        return False, '', "Narrative must be a string"

    # Apply sanitization first
    sanitized = sanitize_text(narrative)

    # Check length after sanitization
    is_valid_length, length_error = validate_text_length(
        sanitized, MAX_NARRATIVE_LENGTH, "Narrative"
    )
    if not is_valid_length:
        return False, sanitized, length_error

    # Check for XSS patterns in original text (before sanitization stripped them)
    is_safe, xss_warning = detect_xss_patterns(narrative)
    if not is_safe:
        return False, sanitized, f"Narrative contains potentially malicious content: {xss_warning}"

    return True, sanitized, None
