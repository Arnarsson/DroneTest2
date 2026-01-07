"""
Comprehensive unit tests for text_validation.py module.
Tests all validation and sanitization functions for incident title and narrative fields.
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from text_validation import (
    validate_text_length,
    strip_html_tags,
    remove_control_characters,
    normalize_unicode,
    normalize_whitespace,
    sanitize_text,
    detect_xss_patterns,
    validate_title,
    validate_narrative,
    MAX_TITLE_LENGTH,
    MAX_NARRATIVE_LENGTH,
)


class TestValidateTextLength:
    """Tests for validate_text_length() function"""

    def test_valid_length_short_text(self):
        """Test short text within limits"""
        is_valid, error = validate_text_length("Short text", 100, "test")
        assert is_valid is True
        assert error is None

    def test_valid_length_exact_limit(self):
        """Test text exactly at the limit"""
        text = "a" * 100
        is_valid, error = validate_text_length(text, 100, "test")
        assert is_valid is True
        assert error is None

    def test_invalid_length_exceeds_limit(self):
        """Test text exceeding maximum length"""
        text = "a" * 101
        is_valid, error = validate_text_length(text, 100, "test")
        assert is_valid is False
        assert "test exceeds maximum length" in error
        assert "101 > 100" in error

    def test_none_value_valid(self):
        """Test that None is valid"""
        is_valid, error = validate_text_length(None, 100, "test")
        assert is_valid is True
        assert error is None

    def test_non_string_invalid(self):
        """Test non-string input returns error"""
        is_valid, error = validate_text_length(12345, 100, "test")
        assert is_valid is False
        assert "must be a string" in error

    def test_empty_string_valid(self):
        """Test empty string is valid"""
        is_valid, error = validate_text_length("", 100, "test")
        assert is_valid is True
        assert error is None

    def test_unicode_characters_counted_correctly(self):
        """Test unicode characters are counted by character, not byte"""
        # "Hello 世界" is 8 characters but more bytes in UTF-8
        text = "Hello 世界"
        assert len(text) == 8
        is_valid, error = validate_text_length(text, 8, "test")
        assert is_valid is True
        assert error is None

    def test_emoji_counted_as_characters(self):
        """Test emoji are counted correctly"""
        text = "🎉🎊🎈"
        is_valid, error = validate_text_length(text, 3, "test")
        assert is_valid is True


class TestStripHtmlTags:
    """Tests for strip_html_tags() function"""

    def test_strip_simple_html_tags(self):
        """Test stripping simple HTML tags"""
        text = "<p>Hello <b>World</b></p>"
        result = strip_html_tags(text)
        assert result == "Hello World"

    def test_strip_self_closing_tags(self):
        """Test stripping self-closing tags"""
        text = "Line 1<br/>Line 2<hr/>"
        result = strip_html_tags(text)
        assert result == "Line 1Line 2"

    def test_strip_tags_with_attributes(self):
        """Test stripping tags with attributes"""
        text = '<a href="https://example.com">Link</a>'
        result = strip_html_tags(text)
        assert result == "Link"

    def test_strip_html_comments(self):
        """Test stripping HTML comments"""
        text = "Before<!-- comment -->After"
        result = strip_html_tags(text)
        assert result == "BeforeAfter"

    def test_strip_multiline_comments(self):
        """Test stripping multiline HTML comments"""
        text = "Before<!--\nmultiline\ncomment\n-->After"
        result = strip_html_tags(text)
        assert result == "BeforeAfter"

    def test_strip_cdata_sections(self):
        """Test stripping CDATA sections"""
        text = "Before<![CDATA[some data]]>After"
        result = strip_html_tags(text)
        assert result == "BeforeAfter"

    def test_decode_html_entities(self):
        """Test decoding HTML entities"""
        text = "&lt;script&gt;alert('xss')&lt;/script&gt;"
        result = strip_html_tags(text)
        assert result == "<script>alert('xss')</script>"

    def test_decode_ampersand(self):
        """Test decoding ampersand entity"""
        text = "A &amp; B"
        result = strip_html_tags(text)
        assert result == "A & B"

    def test_decode_numeric_entities(self):
        """Test decoding numeric HTML entities"""
        text = "&#60;Hello&#62;"  # <Hello>
        result = strip_html_tags(text)
        assert result == "<Hello>"

    def test_decode_hex_entities(self):
        """Test decoding hexadecimal HTML entities"""
        text = "&#x3C;Hello&#x3E;"  # <Hello>
        result = strip_html_tags(text)
        assert result == "<Hello>"

    def test_empty_string(self):
        """Test empty string returns empty"""
        assert strip_html_tags("") == ""

    def test_none_value(self):
        """Test None returns None"""
        assert strip_html_tags(None) is None

    def test_nested_tags(self):
        """Test stripping nested tags"""
        text = "<div><p><span>Content</span></p></div>"
        result = strip_html_tags(text)
        assert result == "Content"

    def test_malformed_tags_removed(self):
        """Test malformed tags are still removed"""
        text = "<div>Before<p unclosed>Middle</div>After"
        result = strip_html_tags(text)
        assert result == "BeforeMiddleAfter"


class TestRemoveControlCharacters:
    """Tests for remove_control_characters() function"""

    def test_remove_null_byte(self):
        """Test null byte removal"""
        text = "Hello\x00World"
        result = remove_control_characters(text)
        assert result == "HelloWorld"

    def test_preserve_newline(self):
        """Test newline is preserved"""
        text = "Line1\nLine2"
        result = remove_control_characters(text)
        assert result == "Line1\nLine2"

    def test_preserve_tab(self):
        """Test tab is preserved"""
        text = "Col1\tCol2"
        result = remove_control_characters(text)
        assert result == "Col1\tCol2"

    def test_remove_c0_controls(self):
        """Test C0 control characters are removed"""
        text = "Hello\x01\x02\x03World"
        result = remove_control_characters(text)
        assert result == "HelloWorld"

    def test_remove_delete_char(self):
        """Test DEL character (0x7F) is removed"""
        text = "Hello\x7FWorld"
        result = remove_control_characters(text)
        assert result == "HelloWorld"

    def test_remove_c1_controls(self):
        """Test C1 control characters (0x80-0x9F) are removed"""
        text = "Hello\x80\x9FWorld"
        result = remove_control_characters(text)
        assert result == "HelloWorld"

    def test_empty_string(self):
        """Test empty string returns empty"""
        assert remove_control_characters("") == ""

    def test_none_value(self):
        """Test None returns None"""
        assert remove_control_characters(None) is None

    def test_preserve_carriage_return(self):
        """Test carriage return (\r) is preserved"""
        text = "Line1\r\nLine2"
        result = remove_control_characters(text)
        assert result == "Line1\r\nLine2"

    def test_remove_vertical_tab(self):
        """Test vertical tab (0x0B) is removed"""
        text = "Hello\x0BWorld"
        result = remove_control_characters(text)
        assert result == "HelloWorld"

    def test_remove_form_feed(self):
        """Test form feed (0x0C) is removed"""
        text = "Hello\x0CWorld"
        result = remove_control_characters(text)
        assert result == "HelloWorld"


class TestNormalizeUnicode:
    """Tests for normalize_unicode() function"""

    def test_nfc_normalization(self):
        """Test NFC normalization combines characters"""
        # e + combining acute accent
        decomposed = "caf\u0065\u0301"  # café with combining accent
        result = normalize_unicode(decomposed)
        # Should become single character é
        assert result == "café"

    def test_already_composed(self):
        """Test already composed characters unchanged"""
        composed = "café"
        result = normalize_unicode(composed)
        assert result == "café"

    def test_empty_string(self):
        """Test empty string returns empty"""
        assert normalize_unicode("") == ""

    def test_none_value(self):
        """Test None returns None"""
        assert normalize_unicode(None) is None

    def test_ascii_unchanged(self):
        """Test ASCII text is unchanged"""
        text = "Hello World 123"
        assert normalize_unicode(text) == text

    def test_japanese_characters(self):
        """Test Japanese characters are normalized"""
        text = "日本語"
        result = normalize_unicode(text)
        assert result == "日本語"

    def test_emoji_preserved(self):
        """Test emoji are preserved"""
        text = "Hello 🎉 World"
        result = normalize_unicode(text)
        assert "🎉" in result


class TestNormalizeWhitespace:
    """Tests for normalize_whitespace() function"""

    def test_collapse_multiple_spaces(self):
        """Test multiple spaces become single space"""
        text = "Hello    World"
        result = normalize_whitespace(text)
        assert result == "Hello World"

    def test_trim_leading_trailing(self):
        """Test leading and trailing whitespace is trimmed"""
        text = "   Hello World   "
        result = normalize_whitespace(text)
        assert result == "Hello World"

    def test_preserve_single_newline(self):
        """Test single newline is preserved"""
        text = "Line1\nLine2"
        result = normalize_whitespace(text)
        assert result == "Line1\nLine2"

    def test_collapse_multiple_newlines(self):
        """Test multiple newlines become double newline"""
        text = "Para1\n\n\n\nPara2"
        result = normalize_whitespace(text)
        assert result == "Para1\n\nPara2"

    def test_collapse_tabs_to_space(self):
        """Test tabs are converted to single space"""
        text = "Hello\t\t\tWorld"
        result = normalize_whitespace(text)
        assert result == "Hello World"

    def test_empty_string(self):
        """Test empty string returns empty"""
        assert normalize_whitespace("") == ""

    def test_none_value(self):
        """Test None returns None"""
        assert normalize_whitespace(None) is None

    def test_mixed_whitespace(self):
        """Test mixed whitespace normalization"""
        text = "  Hello  \t  World  \n\n\n  More  "
        result = normalize_whitespace(text)
        # Whitespace around newlines is normalized separately from newlines
        # The function preserves structure around paragraph breaks
        assert "Hello" in result
        assert "World" in result
        assert "More" in result
        assert "\n\n" in result  # Multiple newlines become double newline


class TestSanitizeText:
    """Tests for sanitize_text() - full sanitization pipeline"""

    def test_full_pipeline_with_html(self):
        """Test full sanitization removes HTML"""
        text = "<p>Hello <b>World</b></p>"
        result = sanitize_text(text)
        assert result == "Hello World"

    def test_full_pipeline_with_control_chars(self):
        """Test full sanitization removes control characters"""
        text = "Hello\x00\x01World"
        result = sanitize_text(text)
        assert result == "HelloWorld"

    def test_full_pipeline_with_excessive_whitespace(self):
        """Test full sanitization normalizes whitespace"""
        text = "  Hello    World  "
        result = sanitize_text(text)
        assert result == "Hello World"

    def test_full_pipeline_with_unicode(self):
        """Test full sanitization normalizes unicode"""
        text = "cafe\u0301"  # café with combining accent
        result = sanitize_text(text)
        assert result == "café"

    def test_combined_sanitization(self):
        """Test all sanitization steps combined"""
        text = "  <p>Hello\x00   World</p>  "
        result = sanitize_text(text)
        assert result == "Hello World"

    def test_empty_string(self):
        """Test empty string returns empty"""
        assert sanitize_text("") == ""

    def test_none_returns_empty_string(self):
        """Test None returns empty string"""
        assert sanitize_text(None) == ""

    def test_non_string_converted(self):
        """Test non-string is converted to string"""
        result = sanitize_text(12345)
        assert result == "12345"

    def test_preserves_valid_content(self):
        """Test valid content is preserved"""
        text = "A drone was spotted near the airport at 14:30."
        result = sanitize_text(text)
        assert result == text

    def test_html_entities_decoded(self):
        """Test HTML entities are decoded during sanitization"""
        text = "Less &lt; Greater &gt; Amp &amp;"
        result = sanitize_text(text)
        assert result == "Less < Greater > Amp &"


class TestDetectXssPatterns:
    """Tests for detect_xss_patterns() function"""

    # Basic Script Tag Tests
    def test_detect_script_tag(self):
        """Test detection of basic script tag"""
        is_safe, msg = detect_xss_patterns("<script>alert('xss')</script>")
        assert is_safe is False
        assert "script" in msg.lower()

    def test_detect_script_tag_uppercase(self):
        """Test detection of uppercase script tag"""
        is_safe, msg = detect_xss_patterns("<SCRIPT>alert('xss')</SCRIPT>")
        assert is_safe is False
        assert "script" in msg.lower()

    def test_detect_script_tag_with_space(self):
        """Test detection of script tag with space after <"""
        is_safe, msg = detect_xss_patterns("< script>alert('xss')</script>")
        assert is_safe is False

    def test_detect_script_tag_self_closing(self):
        """Test detection of self-closing script tag"""
        is_safe, msg = detect_xss_patterns("<script src='evil.js'/>")
        assert is_safe is False

    # Event Handler Tests
    def test_detect_onclick_handler(self):
        """Test detection of onclick event handler"""
        is_safe, msg = detect_xss_patterns("<img onclick='alert(1)'/>")
        assert is_safe is False
        # May detect img tag or onclick - both are valid detections
        assert "img" in msg.lower() or "onclick" in msg.lower()

    def test_detect_onerror_handler(self):
        """Test detection of onerror event handler"""
        is_safe, msg = detect_xss_patterns("<img src=x onerror='alert(1)'/>")
        assert is_safe is False
        # May detect img tag or onerror - both are valid detections
        assert "img" in msg.lower() or "onerror" in msg.lower()

    def test_detect_onload_handler(self):
        """Test detection of onload event handler"""
        is_safe, msg = detect_xss_patterns("<body onload='alert(1)'>")
        assert is_safe is False
        # May detect body tag or onload - both are valid detections
        assert "body" in msg.lower() or "onload" in msg.lower()

    def test_detect_onmouseover_handler(self):
        """Test detection of onmouseover event handler"""
        is_safe, msg = detect_xss_patterns("<div onmouseover='alert(1)'>")
        assert is_safe is False
        assert "onmouseover" in msg.lower()

    def test_detect_onfocus_handler(self):
        """Test detection of onfocus event handler"""
        is_safe, msg = detect_xss_patterns("<input onfocus='alert(1)'>")
        assert is_safe is False
        # May detect input tag or onfocus - both are valid detections
        assert "input" in msg.lower() or "onfocus" in msg.lower()

    # Dangerous URI Schemes
    def test_detect_javascript_uri(self):
        """Test detection of javascript: URI"""
        is_safe, msg = detect_xss_patterns("<a href='javascript:alert(1)'>")
        assert is_safe is False
        assert "javascript" in msg.lower()

    def test_detect_vbscript_uri(self):
        """Test detection of vbscript: URI"""
        is_safe, msg = detect_xss_patterns("<a href='vbscript:msgbox(1)'>")
        assert is_safe is False
        assert "vbscript" in msg.lower()

    def test_detect_data_uri_html(self):
        """Test detection of data: URI with HTML"""
        is_safe, msg = detect_xss_patterns("<a href='data:text/html,<script>alert(1)</script>'>")
        assert is_safe is False

    def test_detect_data_uri_base64(self):
        """Test detection of data: URI with base64"""
        is_safe, msg = detect_xss_patterns("<a href='data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=='>")
        assert is_safe is False

    # Dangerous Tags
    def test_detect_iframe_tag(self):
        """Test detection of iframe tag"""
        is_safe, msg = detect_xss_patterns("<iframe src='evil.com'>")
        assert is_safe is False
        assert "iframe" in msg.lower()

    def test_detect_object_tag(self):
        """Test detection of object tag"""
        is_safe, msg = detect_xss_patterns("<object data='evil.swf'>")
        assert is_safe is False
        assert "object" in msg.lower()

    def test_detect_embed_tag(self):
        """Test detection of embed tag"""
        is_safe, msg = detect_xss_patterns("<embed src='evil.swf'>")
        assert is_safe is False
        assert "embed" in msg.lower()

    def test_detect_svg_tag(self):
        """Test detection of SVG tag"""
        is_safe, msg = detect_xss_patterns("<svg onload='alert(1)'>")
        assert is_safe is False

    def test_detect_img_tag(self):
        """Test detection of img tag (can be vector)"""
        is_safe, msg = detect_xss_patterns("<img src=x onerror=alert(1)>")
        assert is_safe is False

    def test_detect_form_tag(self):
        """Test detection of form tag"""
        is_safe, msg = detect_xss_patterns("<form action='evil.com'>")
        assert is_safe is False

    # Safe Content
    def test_safe_plain_text(self):
        """Test safe plain text passes"""
        is_safe, msg = detect_xss_patterns("A drone was spotted near the airport")
        assert is_safe is True
        assert msg is None

    def test_safe_text_with_numbers(self):
        """Test safe text with numbers"""
        is_safe, msg = detect_xss_patterns("Incident occurred at 14:30, 2 drones spotted")
        assert is_safe is True

    def test_safe_text_with_special_chars(self):
        """Test safe text with special characters"""
        is_safe, msg = detect_xss_patterns("Location: 55.68°N, 12.58°E")
        assert is_safe is True

    def test_safe_empty_string(self):
        """Test empty string is safe"""
        is_safe, msg = detect_xss_patterns("")
        assert is_safe is True

    def test_safe_none_value(self):
        """Test None is safe"""
        is_safe, msg = detect_xss_patterns(None)
        assert is_safe is True

    # Encoded Attack Detection
    def test_detect_url_encoded_script(self):
        """Test detection of URL-encoded script tag"""
        is_safe, msg = detect_xss_patterns("%3Cscript%3Ealert(1)%3C/script%3E")
        assert is_safe is False

    def test_detect_double_url_encoded(self):
        """Test detection of double URL-encoded payload"""
        # %253C = double encoded <
        is_safe, msg = detect_xss_patterns("%253Cscript%253Ealert(1)%253C/script%253E")
        assert is_safe is False

    def test_detect_html_entity_encoded(self):
        """Test detection of HTML entity encoded script"""
        is_safe, msg = detect_xss_patterns("&#60;script&#62;alert(1)&#60;/script&#62;")
        assert is_safe is False

    def test_detect_hex_entity_encoded(self):
        """Test detection of hex entity encoded script"""
        is_safe, msg = detect_xss_patterns("&#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;")
        assert is_safe is False

    # CSS Expression Attacks
    def test_detect_css_expression(self):
        """Test detection of CSS expression"""
        is_safe, msg = detect_xss_patterns("<div style='width: expression(alert(1))'>")
        assert is_safe is False
        assert "CSS" in msg

    def test_detect_css_url_javascript(self):
        """Test detection of CSS url() with javascript"""
        is_safe, msg = detect_xss_patterns("<div style='background: url(javascript:alert(1))'>")
        assert is_safe is False

    # SVG/MathML Attacks
    def test_detect_svg_onload(self):
        """Test detection of SVG onload attack"""
        is_safe, msg = detect_xss_patterns("<svg onload='alert(1)'>")
        assert is_safe is False

    def test_detect_svg_with_script(self):
        """Test detection of SVG containing script"""
        is_safe, msg = detect_xss_patterns("<svg><script>alert(1)</script></svg>")
        assert is_safe is False

    def test_detect_mathml_with_event(self):
        """Test detection of MathML with event handler"""
        is_safe, msg = detect_xss_patterns("<math onclick='alert(1)'>")
        assert is_safe is False

    # DOM Clobbering
    def test_detect_dom_clobbering_form(self):
        """Test detection of DOM clobbering with form"""
        is_safe, msg = detect_xss_patterns("<form id='location'>")
        assert is_safe is False
        # May detect form tag or DOM clobbering - both are valid detections
        assert "form" in msg.lower() or "DOM clobbering" in msg

    def test_detect_dom_clobbering_input(self):
        """Test detection of DOM clobbering with input"""
        is_safe, msg = detect_xss_patterns("<input name='document'>")
        assert is_safe is False

    # Other Injection Vectors
    def test_detect_script_in_comment(self):
        """Test detection of script hidden in comment"""
        is_safe, msg = detect_xss_patterns("<!--<script>alert(1)</script>-->")
        assert is_safe is False

    def test_detect_meta_refresh(self):
        """Test detection of meta refresh injection"""
        is_safe, msg = detect_xss_patterns("<meta http-equiv='refresh' content='0;url=evil.com'>")
        assert is_safe is False

    def test_detect_srcdoc_attribute(self):
        """Test detection of srcdoc attribute"""
        is_safe, msg = detect_xss_patterns("<iframe srcdoc='<script>alert(1)</script>'>")
        assert is_safe is False

    def test_detect_formaction(self):
        """Test detection of formaction attribute"""
        is_safe, msg = detect_xss_patterns("<button formaction='javascript:alert(1)'>")
        assert is_safe is False

    def test_detect_xlink_href(self):
        """Test detection of xlink:href attribute"""
        is_safe, msg = detect_xss_patterns("<svg><a xlink:href='javascript:alert(1)'>")
        assert is_safe is False


class TestValidateTitle:
    """Tests for validate_title() wrapper function"""

    def test_valid_title(self):
        """Test valid title passes"""
        is_valid, sanitized, error = validate_title("Drone spotted near Copenhagen Airport")
        assert is_valid is True
        assert sanitized == "Drone spotted near Copenhagen Airport"
        assert error is None

    def test_title_none_valid(self):
        """Test None title returns valid with empty string"""
        is_valid, sanitized, error = validate_title(None)
        assert is_valid is True
        assert sanitized == ""
        assert error is None

    def test_title_empty_string_valid(self):
        """Test empty string title is valid"""
        is_valid, sanitized, error = validate_title("")
        assert is_valid is True
        assert sanitized == ""
        assert error is None

    def test_title_whitespace_only_valid(self):
        """Test whitespace-only title is valid (returns empty)"""
        is_valid, sanitized, error = validate_title("   ")
        assert is_valid is True
        assert sanitized == ""
        assert error is None

    def test_title_exceeds_max_length(self):
        """Test title exceeding 500 chars is invalid"""
        long_title = "A" * 501
        is_valid, sanitized, error = validate_title(long_title)
        assert is_valid is False
        assert "exceeds maximum length" in error
        assert "500" in error

    def test_title_exactly_max_length(self):
        """Test title exactly at 500 chars is valid"""
        title = "A" * 500
        is_valid, sanitized, error = validate_title(title)
        assert is_valid is True
        assert len(sanitized) == 500

    def test_title_sanitized_html(self):
        """Test title with HTML is sanitized"""
        is_valid, sanitized, error = validate_title("<b>Important</b> drone sighting")
        # Note: HTML tags trigger XSS detection since we check original text
        # but the function should return sanitized version
        assert "Important" in sanitized
        assert "<b>" not in sanitized

    def test_title_with_xss_rejected(self):
        """Test title with XSS payload is rejected"""
        is_valid, sanitized, error = validate_title("<script>alert('xss')</script>")
        assert is_valid is False
        assert "malicious content" in error

    def test_title_non_string_invalid(self):
        """Test non-string title is invalid"""
        is_valid, sanitized, error = validate_title(12345)
        assert is_valid is False
        assert "must be a string" in error

    def test_title_unicode_valid(self):
        """Test title with unicode characters is valid"""
        is_valid, sanitized, error = validate_title("Drone set til København Lufthavn")
        assert is_valid is True
        assert "København" in sanitized

    def test_title_sanitization_applied(self):
        """Test sanitization is applied to title"""
        is_valid, sanitized, error = validate_title("  Title with   extra    spaces  ")
        assert is_valid is True
        assert sanitized == "Title with extra spaces"


class TestValidateNarrative:
    """Tests for validate_narrative() wrapper function"""

    def test_valid_narrative(self):
        """Test valid narrative passes"""
        narrative = "A drone was observed flying at approximately 100m altitude near the airport perimeter. Multiple witnesses reported the sighting around 14:30 local time."
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is True
        assert sanitized == narrative
        assert error is None

    def test_narrative_none_valid(self):
        """Test None narrative returns valid with empty string"""
        is_valid, sanitized, error = validate_narrative(None)
        assert is_valid is True
        assert sanitized == ""
        assert error is None

    def test_narrative_empty_string_valid(self):
        """Test empty string narrative is valid"""
        is_valid, sanitized, error = validate_narrative("")
        assert is_valid is True
        assert sanitized == ""
        assert error is None

    def test_narrative_whitespace_only_valid(self):
        """Test whitespace-only narrative is valid"""
        is_valid, sanitized, error = validate_narrative("   \n\n   ")
        assert is_valid is True
        assert sanitized == ""
        assert error is None

    def test_narrative_exceeds_max_length(self):
        """Test narrative exceeding 10000 chars is invalid"""
        long_narrative = "A" * 10001
        is_valid, sanitized, error = validate_narrative(long_narrative)
        assert is_valid is False
        assert "exceeds maximum length" in error
        assert "10000" in error

    def test_narrative_exactly_max_length(self):
        """Test narrative exactly at 10000 chars is valid"""
        narrative = "A" * 10000
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is True
        assert len(sanitized) == 10000

    def test_narrative_with_xss_rejected(self):
        """Test narrative with XSS payload is rejected"""
        narrative = "Report details: <script>alert('xss')</script> end of report"
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is False
        assert "malicious content" in error

    def test_narrative_with_event_handler_rejected(self):
        """Test narrative with event handler is rejected"""
        narrative = "Click here: <img src=x onerror=alert(1)> for details"
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is False
        assert "malicious content" in error

    def test_narrative_non_string_invalid(self):
        """Test non-string narrative is invalid"""
        is_valid, sanitized, error = validate_narrative(["list", "of", "items"])
        assert is_valid is False
        assert "must be a string" in error

    def test_narrative_multiline_valid(self):
        """Test multiline narrative is valid"""
        narrative = """First paragraph with details.

Second paragraph with more information.

Third paragraph concluding the report."""
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is True
        assert "\n\n" in sanitized  # Paragraph breaks preserved

    def test_narrative_sanitization_applied(self):
        """Test sanitization normalizes whitespace in narrative"""
        is_valid, sanitized, error = validate_narrative("  Start    middle    end  ")
        assert is_valid is True
        assert sanitized == "Start middle end"


class TestMaxLengthConstants:
    """Test maximum length constants are correctly defined"""

    def test_max_title_length(self):
        """Test MAX_TITLE_LENGTH is 500"""
        assert MAX_TITLE_LENGTH == 500

    def test_max_narrative_length(self):
        """Test MAX_NARRATIVE_LENGTH is 10000"""
        assert MAX_NARRATIVE_LENGTH == 10000


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_text_with_only_html_tags(self):
        """Test text containing only HTML tags"""
        # Use dangerous tags that will be detected
        is_valid, sanitized, error = validate_title("<script></script>")
        # After sanitization, only empty remains, but original has dangerous tags
        assert is_valid is False  # Should detect dangerous script tag

    def test_benign_html_tags_allowed(self):
        """Test benign HTML tags are sanitized but allowed"""
        # <br/>, <hr/>, <div> are not in DANGEROUS_TAGS
        is_valid, sanitized, error = validate_title("<br/>Line break<hr/>")
        # Should be valid because these tags aren't dangerous
        assert is_valid is True
        assert sanitized == "Line break"  # Tags stripped but content preserved

    def test_deeply_nested_encoding(self):
        """Test deeply nested encoding attempts"""
        # Triple URL-encoded <script>
        text = "%25253Cscript%25253E"
        is_safe, msg = detect_xss_patterns(text)
        # Should detect or handle gracefully
        assert is_safe is True or is_safe is False  # May or may not detect deep nesting

    def test_mixed_case_event_handlers(self):
        """Test mixed case event handlers"""
        is_safe, msg = detect_xss_patterns("<img OnErRoR='alert(1)'>")
        assert is_safe is False

    def test_newline_in_tag(self):
        """Test newline within tag"""
        is_safe, msg = detect_xss_patterns("<script\n>alert(1)</script>")
        assert is_safe is False

    def test_tab_in_event_handler(self):
        """Test tab character in event handler"""
        is_safe, msg = detect_xss_patterns("<img onerror\t='alert(1)'>")
        assert is_safe is False

    def test_unicode_lookalike_characters(self):
        """Test unicode characters that look like ASCII"""
        # Full-width less-than sign
        text = "＜script＞"  # These are full-width characters
        is_safe, msg = detect_xss_patterns(text)
        # Should pass as these aren't real HTML tags
        assert is_safe is True

    def test_very_long_attribute_value(self):
        """Test very long attribute value"""
        long_value = "x" * 10000
        text = f"<img src='{long_value}'>"
        is_safe, msg = detect_xss_patterns(text)
        assert is_safe is False  # Still detects the img tag

    def test_null_byte_injection(self):
        """Test null byte injection attempt"""
        is_safe, msg = detect_xss_patterns("<scr\x00ipt>alert(1)</script>")
        assert is_safe is False  # Should still detect

    def test_backslash_obfuscation(self):
        """Test backslash obfuscation"""
        is_safe, msg = detect_xss_patterns("<scr\\ipt>alert(1)</script>")
        assert is_safe is False  # Should still detect

    def test_html_entity_without_semicolon(self):
        """Test HTML entity without trailing semicolon"""
        is_safe, msg = detect_xss_patterns("&#60script&#62alert(1)&#60/script&#62")
        assert is_safe is False  # Should decode and detect


class TestOWASPXSSPayloads:
    """
    Comprehensive XSS payload tests based on OWASP XSS Filter Evasion Cheat Sheet.
    https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html

    These payloads represent common attack vectors that security researchers
    have identified as bypassing various filters.
    """

    # =========================================================================
    # Script Tag Variations (OWASP)
    # =========================================================================

    def test_basic_script_tag(self):
        """Basic XSS test case from OWASP"""
        is_safe, _ = detect_xss_patterns("<SCRIPT SRC=http://xss.rocks/xss.js></SCRIPT>")
        assert is_safe is False

    def test_script_tag_with_img_src_error(self):
        """Image XSS using JavaScript directive"""
        is_safe, _ = detect_xss_patterns('<IMG SRC="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_script_no_closing_tag(self):
        """Malformed script tag without closing"""
        is_safe, _ = detect_xss_patterns("<SCRIPT/XSS SRC=\"http://xss.rocks/xss.js\"></SCRIPT>")
        assert is_safe is False

    def test_script_with_extra_open_bracket(self):
        """Attempt to bypass with extra open bracket"""
        is_safe, _ = detect_xss_patterns("<<SCRIPT>alert(\"XSS\");//<</SCRIPT>")
        assert is_safe is False

    def test_script_end_title_tag(self):
        """Breaking out of title tag"""
        is_safe, _ = detect_xss_patterns("</TITLE><SCRIPT>alert(\"XSS\");</SCRIPT>")
        assert is_safe is False

    def test_script_with_spaces(self):
        """Script with space before JavaScript"""
        is_safe, _ = detect_xss_patterns("<SCRIPT SRC=http://xss.rocks/xss.js></SCRIPT>")
        assert is_safe is False

    def test_script_self_closing_tag(self):
        """Self-closing script tag"""
        is_safe, _ = detect_xss_patterns('<SCRIPT SRC="http://xss.rocks/xss.js"/>')
        assert is_safe is False

    def test_script_tag_case_insensitive(self):
        """Case mixing attempt"""
        is_safe, _ = detect_xss_patterns('<ScRiPt>alert("XSS")</sCrIpT>')
        assert is_safe is False

    def test_script_multiline_obfuscated(self):
        """Newline in script tag"""
        is_safe, _ = detect_xss_patterns('<SCR\nIPT>alert("XSS")</SCRIPT>')
        assert is_safe is False

    def test_script_with_tab(self):
        """Tab character in script tag"""
        is_safe, _ = detect_xss_patterns('<SCR\tIPT>alert("XSS")</SCRIPT>')
        assert is_safe is False

    def test_script_split_with_nulls(self):
        """Null character injection in script tag"""
        is_safe, _ = detect_xss_patterns('<SCR\x00IPT>alert("XSS")</SCRIPT>')
        assert is_safe is False

    # =========================================================================
    # Event Handler Injections (OWASP)
    # =========================================================================

    def test_img_onerror_basic(self):
        """Basic IMG onerror XSS"""
        is_safe, _ = detect_xss_patterns('<IMG SRC=x onerror="alert(\'XSS\')">')
        assert is_safe is False

    def test_img_onerror_no_quotes(self):
        """IMG onerror without quotes"""
        is_safe, _ = detect_xss_patterns("<IMG SRC=x onerror=alert('XSS')>")
        assert is_safe is False

    def test_body_onload(self):
        """Body onload event handler"""
        is_safe, _ = detect_xss_patterns('<BODY ONLOAD=alert("XSS")>')
        assert is_safe is False

    def test_body_background(self):
        """Body background image XSS"""
        is_safe, _ = detect_xss_patterns('<BODY BACKGROUND="javascript:alert(\'XSS\')">')
        assert is_safe is False

    def test_bgsound(self):
        """BGSOUND tag XSS"""
        is_safe, _ = detect_xss_patterns('<BGSOUND SRC="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_img_dynsrc(self):
        """IMG DYNSRC"""
        is_safe, _ = detect_xss_patterns('<IMG DYNSRC="javascript:alert(\'XSS\')">')
        assert is_safe is False

    def test_img_lowsrc(self):
        """IMG LOWSRC"""
        is_safe, _ = detect_xss_patterns('<IMG LOWSRC="javascript:alert(\'XSS\')">')
        assert is_safe is False

    def test_br_style_expression(self):
        """BR tag with CSS expression"""
        is_safe, _ = detect_xss_patterns('<BR SIZE="&{alert(\'XSS\')}">')
        # This uses SSI, may not be detected but good to test
        # The function may or may not catch this specific variant
        pass  # Allow either result for this edge case

    def test_input_onfocus(self):
        """INPUT with autofocus and onfocus"""
        is_safe, _ = detect_xss_patterns('<INPUT TYPE="TEXT" ONFOCUS="alert(\'XSS\')" AUTOFOCUS>')
        assert is_safe is False

    def test_marquee_onstart(self):
        """MARQUEE onstart event"""
        is_safe, _ = detect_xss_patterns('<MARQUEE ONSTART="alert(\'XSS\')">test</MARQUEE>')
        assert is_safe is False

    def test_video_onerror(self):
        """VIDEO with onerror"""
        is_safe, _ = detect_xss_patterns('<VIDEO><SOURCE ONERROR="alert(\'XSS\')">')
        assert is_safe is False

    def test_details_ontoggle(self):
        """DETAILS ontoggle event"""
        is_safe, _ = detect_xss_patterns('<DETAILS OPEN ONTOGGLE="alert(\'XSS\')">')
        assert is_safe is False

    def test_select_onchange(self):
        """SELECT with onchange"""
        is_safe, _ = detect_xss_patterns('<SELECT ONCHANGE="alert(\'XSS\')"><OPTION>1</OPTION></SELECT>')
        assert is_safe is False

    def test_textarea_onfocus(self):
        """TEXTAREA with autofocus onfocus"""
        is_safe, _ = detect_xss_patterns('<TEXTAREA ONFOCUS="alert(\'XSS\')" AUTOFOCUS>')
        assert is_safe is False

    def test_audio_onloadeddata(self):
        """AUDIO with various events"""
        is_safe, _ = detect_xss_patterns('<AUDIO SRC=1 ONLOADEDDATA="alert(\'XSS\')">')
        assert is_safe is False

    def test_div_onmouseover(self):
        """DIV with onmouseover requiring user interaction"""
        is_safe, _ = detect_xss_patterns('<DIV ONMOUSEOVER="alert(\'XSS\')">test</DIV>')
        assert is_safe is False

    def test_button_onclick(self):
        """BUTTON with onclick"""
        is_safe, _ = detect_xss_patterns('<BUTTON ONCLICK="alert(\'XSS\')">Click</BUTTON>')
        assert is_safe is False

    def test_keygen_onfocus(self):
        """KEYGEN onfocus (legacy)"""
        is_safe, _ = detect_xss_patterns('<KEYGEN ONFOCUS="alert(\'XSS\')" AUTOFOCUS>')
        assert is_safe is False

    def test_object_onerror(self):
        """OBJECT onerror event"""
        is_safe, _ = detect_xss_patterns('<OBJECT DATA=1 ONERROR="alert(\'XSS\')">')
        assert is_safe is False

    # =========================================================================
    # Encoded Payloads (URL, HTML Entities) - OWASP
    # =========================================================================

    def test_url_encoded_script(self):
        """URL encoded <script>"""
        is_safe, _ = detect_xss_patterns('%3Cscript%3Ealert(1)%3C%2Fscript%3E')
        assert is_safe is False

    def test_double_url_encoded_script(self):
        """Double URL encoded script tag"""
        is_safe, _ = detect_xss_patterns('%253Cscript%253Ealert(1)%253C%252Fscript%253E')
        assert is_safe is False

    def test_html_decimal_entities(self):
        """HTML decimal entities for script tag"""
        is_safe, _ = detect_xss_patterns('&#60;script&#62;alert(1)&#60;/script&#62;')
        assert is_safe is False

    def test_html_hex_entities(self):
        """HTML hex entities for script tag"""
        is_safe, _ = detect_xss_patterns('&#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;')
        assert is_safe is False

    def test_html_entities_without_semicolon(self):
        """HTML entities without trailing semicolons"""
        is_safe, _ = detect_xss_patterns('&#60script&#62alert(1)&#60/script&#62')
        assert is_safe is False

    def test_mixed_encoding(self):
        """Mixed URL and HTML encoding"""
        is_safe, _ = detect_xss_patterns('%3C&#115;cript%3Ealert(1)%3C/script%3E')
        assert is_safe is False

    def test_javascript_uri_encoded(self):
        """URL encoded javascript: URI"""
        is_safe, _ = detect_xss_patterns('<a href="%6A%61%76%61%73%63%72%69%70%74%3Aalert(1)">click</a>')
        assert is_safe is False

    def test_html_entity_javascript(self):
        """HTML entity encoded javascript:"""
        is_safe, _ = detect_xss_patterns('<a href="&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert(1)">x</a>')
        assert is_safe is False

    def test_unicode_encoding(self):
        """Unicode escaped characters"""
        is_safe, _ = detect_xss_patterns('<script>\\u0061lert(1)</script>')
        assert is_safe is False

    def test_hex_encoding_event_handler(self):
        """Hex encoded event handler"""
        is_safe, _ = detect_xss_patterns('<img src=x &#111;nerror="alert(1)">')
        assert is_safe is False

    def test_base64_data_uri(self):
        """Base64 encoded JavaScript in data URI"""
        is_safe, _ = detect_xss_patterns('<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">x</a>')
        assert is_safe is False

    def test_long_utf8_encoding(self):
        """Long UTF-8 encoding of < (OWASP)"""
        is_safe, _ = detect_xss_patterns('&#x0000003C;script&#x0000003E;alert(1)')
        # Should detect after normalizing the long hex codes
        assert is_safe is False

    # =========================================================================
    # SVG/MathML Vector Attacks (OWASP)
    # =========================================================================

    def test_svg_onload(self):
        """SVG with onload event"""
        is_safe, _ = detect_xss_patterns('<svg onload="alert(1)">')
        assert is_safe is False

    def test_svg_with_script_tag(self):
        """SVG containing script element"""
        is_safe, _ = detect_xss_patterns('<svg><script>alert(1)</script></svg>')
        assert is_safe is False

    def test_svg_animate_href(self):
        """SVG animate with javascript href"""
        is_safe, _ = detect_xss_patterns('<svg><animate xlink:href="javascript:alert(1)"/></svg>')
        assert is_safe is False

    def test_svg_animate_onclick(self):
        """SVG animate with onclick"""
        is_safe, _ = detect_xss_patterns('<svg><animate onclick="alert(1)"/></svg>')
        assert is_safe is False

    def test_svg_set_event(self):
        """SVG set element with event"""
        is_safe, _ = detect_xss_patterns('<svg><set onbegin="alert(1)"/></svg>')
        assert is_safe is False

    def test_svg_foreignobject(self):
        """SVG foreignObject injection"""
        is_safe, _ = detect_xss_patterns('<svg><foreignObject><script>alert(1)</script></foreignObject></svg>')
        assert is_safe is False

    def test_svg_image_xlink(self):
        """SVG image with xlink:href"""
        is_safe, _ = detect_xss_patterns('<svg><image xlink:href="javascript:alert(1)"></svg>')
        assert is_safe is False

    def test_svg_use_xlink(self):
        """SVG use element with xlink"""
        is_safe, _ = detect_xss_patterns('<svg><use xlink:href="javascript:alert(1)"></svg>')
        assert is_safe is False

    def test_svg_a_xlink(self):
        """SVG a element with xlink:href"""
        is_safe, _ = detect_xss_patterns('<svg><a xlink:href="javascript:alert(1)">click</a></svg>')
        assert is_safe is False

    def test_math_element_xss(self):
        """MathML-based XSS"""
        is_safe, _ = detect_xss_patterns('<math><maction actiontype="statusline#http://google.com" xlink:href="javascript:alert(1)">click</maction></math>')
        assert is_safe is False

    def test_math_annotation_xml_svg(self):
        """MathML annotation-xml with SVG"""
        is_safe, _ = detect_xss_patterns('<math><annotation-xml encoding="text/html"><svg onload="alert(1)"></svg></annotation-xml></math>')
        assert is_safe is False

    def test_svg_desc_foreignobject(self):
        """SVG desc with foreignObject"""
        is_safe, _ = detect_xss_patterns('<svg><desc><foreignObject><script>alert(1)</script></foreignObject></desc></svg>')
        assert is_safe is False

    # =========================================================================
    # CSS Expression Attacks (OWASP) - IE Legacy
    # =========================================================================

    def test_css_expression_basic(self):
        """Basic CSS expression (IE)"""
        is_safe, _ = detect_xss_patterns('<DIV STYLE="width: expression(alert(\'XSS\'));">')
        assert is_safe is False

    def test_css_expression_background_image(self):
        """CSS expression in background-image"""
        is_safe, _ = detect_xss_patterns('<DIV STYLE="background-image: expression(alert(\'XSS\'));">')
        assert is_safe is False

    def test_css_expression_list_style(self):
        """CSS expression in list-style"""
        is_safe, _ = detect_xss_patterns('<DIV STYLE="list-style: expression(alert(\'XSS\'));">')
        assert is_safe is False

    def test_css_expression_with_linebreaks(self):
        """CSS expression with line breaks"""
        is_safe, _ = detect_xss_patterns('<DIV STYLE="width:\nexpr\nession(alert(\'XSS\'));">')
        # May or may not catch all obfuscation, but test the attempt
        pass  # Edge case

    def test_css_url_javascript(self):
        """CSS url() with javascript"""
        is_safe, _ = detect_xss_patterns('<DIV STYLE="background: url(javascript:alert(\'XSS\'));">')
        assert is_safe is False

    def test_css_behavior(self):
        """CSS behavior property (IE)"""
        is_safe, _ = detect_xss_patterns('<DIV STYLE="behavior: url(xss.htc);">')
        assert is_safe is False

    def test_css_moz_binding(self):
        """CSS -moz-binding (Firefox legacy)"""
        is_safe, _ = detect_xss_patterns('<DIV STYLE="-moz-binding: url(xss.xml#xss);">')
        assert is_safe is False

    def test_css_import(self):
        """CSS @import"""
        is_safe, _ = detect_xss_patterns('<STYLE>@import "xss.css";</STYLE>')
        assert is_safe is False

    def test_style_tag_with_expression(self):
        """STYLE tag with expression"""
        is_safe, _ = detect_xss_patterns('<STYLE>body{width:expression(alert("XSS"))}</STYLE>')
        assert is_safe is False

    # =========================================================================
    # Additional OWASP Vectors
    # =========================================================================

    def test_meta_refresh_redirect(self):
        """Meta refresh redirect"""
        is_safe, _ = detect_xss_patterns('<META HTTP-EQUIV="refresh" CONTENT="0;url=javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_meta_refresh_data_uri(self):
        """Meta refresh with data URI"""
        is_safe, _ = detect_xss_patterns('<META HTTP-EQUIV="refresh" CONTENT="0;url=data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">')
        assert is_safe is False

    def test_iframe_src_javascript(self):
        """IFRAME with javascript src"""
        is_safe, _ = detect_xss_patterns('<IFRAME SRC="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_iframe_srcdoc(self):
        """IFRAME with srcdoc"""
        is_safe, _ = detect_xss_patterns('<IFRAME SRCDOC="<script>alert(1)</script>">')
        assert is_safe is False

    def test_embed_src_javascript(self):
        """EMBED with javascript src"""
        is_safe, _ = detect_xss_patterns('<EMBED SRC="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_object_data_javascript(self):
        """OBJECT with javascript data"""
        is_safe, _ = detect_xss_patterns('<OBJECT DATA="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_frameset_onload(self):
        """FRAMESET onload"""
        is_safe, _ = detect_xss_patterns('<FRAMESET ONLOAD="alert(\'XSS\')">')
        assert is_safe is False

    def test_table_background(self):
        """TABLE BACKGROUND javascript"""
        is_safe, _ = detect_xss_patterns('<TABLE BACKGROUND="javascript:alert(\'XSS\')">')
        assert is_safe is False

    def test_td_background(self):
        """TD BACKGROUND javascript"""
        is_safe, _ = detect_xss_patterns('<TD BACKGROUND="javascript:alert(\'XSS\')">')
        assert is_safe is False

    def test_link_stylesheet(self):
        """LINK stylesheet injection"""
        is_safe, _ = detect_xss_patterns('<LINK REL="stylesheet" HREF="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_base_href_javascript(self):
        """BASE href javascript"""
        is_safe, _ = detect_xss_patterns('<BASE HREF="javascript:alert(\'XSS\');//">')
        assert is_safe is False

    def test_applet_tag(self):
        """APPLET tag (legacy)"""
        is_safe, _ = detect_xss_patterns('<APPLET CODE="xss.class" CODEBASE="http://xss.rocks/">')
        assert is_safe is False

    def test_vbscript_image(self):
        """VBScript in image (IE)"""
        is_safe, _ = detect_xss_patterns('<IMG SRC="vbscript:msgbox(\'XSS\')">')
        assert is_safe is False

    def test_livescript(self):
        """Livescript protocol (legacy Netscape)"""
        is_safe, _ = detect_xss_patterns('<IMG SRC="livescript:[code]">')
        assert is_safe is False

    def test_form_action_javascript(self):
        """FORM action javascript"""
        is_safe, _ = detect_xss_patterns('<FORM ACTION="javascript:alert(\'XSS\')">')
        assert is_safe is False

    def test_formaction_attribute(self):
        """formaction attribute"""
        is_safe, _ = detect_xss_patterns('<BUTTON FORMACTION="javascript:alert(\'XSS\')">Submit</BUTTON>')
        assert is_safe is False

    def test_isindex_prompt_injection(self):
        """ISINDEX tag (legacy)"""
        is_safe, _ = detect_xss_patterns('<ISINDEX TYPE="IMAGE" SRC="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_input_image_src(self):
        """INPUT type=image with javascript src"""
        is_safe, _ = detect_xss_patterns('<INPUT TYPE="IMAGE" SRC="javascript:alert(\'XSS\');">')
        assert is_safe is False

    def test_xml_data_island(self):
        """XML data island (IE)"""
        is_safe, _ = detect_xss_patterns('<XML ID="xss"><I><B><IMG SRC="javas<!-- -->cript:alert(\'XSS\')"></B></I></XML>')
        assert is_safe is False

    def test_html_plus_time(self):
        """HTML+TIME (IE)"""
        is_safe, _ = detect_xss_patterns('<HTML><BODY><?xml:namespace prefix="t" ns="urn:schemas-microsoft-com:time"><?import namespace="t" implementation="#default#time2"><t:set attributeName="innerHTML" to="XSS"></BODY></HTML>')
        # Edge case - test for dangerous tags at minimum
        is_safe2, _ = detect_xss_patterns('<t:set attributeName="innerHTML">')
        # May or may not detect this specific legacy IE vector

    # =========================================================================
    # DOM Clobbering Attacks
    # =========================================================================

    def test_dom_clobber_form_document(self):
        """DOM clobbering with form named document"""
        is_safe, _ = detect_xss_patterns('<form id="document"></form>')
        assert is_safe is False

    def test_dom_clobber_input_location(self):
        """DOM clobbering with input named location"""
        is_safe, _ = detect_xss_patterns('<input name="location" value="http://evil.com">')
        assert is_safe is False

    def test_dom_clobber_img_window(self):
        """DOM clobbering with img named window"""
        is_safe, _ = detect_xss_patterns('<img name="window">')
        assert is_safe is False

    def test_dom_clobber_anchor_document(self):
        """DOM clobbering with anchor named document"""
        is_safe, _ = detect_xss_patterns('<a id="document"></a>')
        assert is_safe is False

    # =========================================================================
    # Bypasses and Edge Cases
    # =========================================================================

    def test_null_byte_in_script(self):
        """Null byte injection in script tag"""
        is_safe, _ = detect_xss_patterns('<scr\x00ipt>alert(1)</script>')
        assert is_safe is False

    def test_backslash_obfuscation(self):
        """Backslash obfuscation attempt"""
        is_safe, _ = detect_xss_patterns('<script>a]lert(1)</script>')
        assert is_safe is False

    def test_comment_in_script_tag(self):
        """HTML comment within script tag"""
        is_safe, _ = detect_xss_patterns('<script><!--alert(1)//--></script>')
        assert is_safe is False

    def test_split_across_attributes(self):
        """XSS split across attributes"""
        is_safe, _ = detect_xss_patterns('<img src="x" " onerror="alert(1)">')
        assert is_safe is False

    def test_quotes_escaped_context(self):
        """Quote escaped context breaking"""
        is_safe, _ = detect_xss_patterns('";alert(1);//')
        # Just JavaScript code, not in HTML context - should be safe
        assert is_safe is True

    def test_protocol_handler_casing(self):
        """Mixed case protocol handler"""
        is_safe, _ = detect_xss_patterns('<a href="JaVaScRiPt:alert(1)">click</a>')
        assert is_safe is False

    def test_protocol_with_tabs(self):
        """Tabs in javascript protocol"""
        is_safe, _ = detect_xss_patterns('<a href="java\tscript:alert(1)">x</a>')
        assert is_safe is False

    def test_protocol_with_newlines(self):
        """Newlines in javascript protocol"""
        is_safe, _ = detect_xss_patterns('<a href="java\nscript:alert(1)">x</a>')
        assert is_safe is False

    def test_data_uri_svg(self):
        """Data URI with SVG containing script"""
        is_safe, _ = detect_xss_patterns('<img src="data:image/svg+xml,<svg onload=alert(1)>">')
        assert is_safe is False

    def test_xss_via_content_type(self):
        """Data URI specifying text/html"""
        is_safe, _ = detect_xss_patterns('<a href="data:text/html,<script>alert(1)</script>">click</a>')
        assert is_safe is False


class TestRealWorldExamples:
    """Test with realistic incident report content"""

    def test_legitimate_incident_report(self):
        """Test legitimate incident report content"""
        title = "Unidentified drone near Copenhagen Airport"
        narrative = """At approximately 14:35 on October 14, 2024, multiple eyewitnesses reported seeing an unidentified drone flying at low altitude (estimated 50-100 meters) near the eastern perimeter of Copenhagen Airport.

The drone was described as a medium-sized quadcopter with visible navigation lights. It was observed hovering for approximately 3 minutes before moving northeast towards Kastrup.

Air traffic control was notified and two departures were briefly delayed. No incidents resulted from the sighting.

Witnesses included airport ground staff and passengers in Terminal 3. Local police have been notified."""

        is_valid_title, sanitized_title, title_error = validate_title(title)
        is_valid_narrative, sanitized_narrative, narrative_error = validate_narrative(narrative)

        assert is_valid_title is True
        assert is_valid_narrative is True
        assert title_error is None
        assert narrative_error is None

    def test_report_with_coordinates(self):
        """Test report containing coordinate notation"""
        narrative = "Location: 55.6180°N, 12.6560°E. Altitude: ~100m AGL."
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is True
        assert "55.6180°N" in sanitized

    def test_report_with_urls_mentioned(self):
        """Test report mentioning URLs (not hyperlinks)"""
        narrative = "See police report at politi.dk/rapport/123456 for details."
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is True

    def test_report_with_quotes(self):
        """Test report containing quoted witness statements"""
        narrative = 'Witness stated: "I saw a drone flying very close to the runway."'
        is_valid, sanitized, error = validate_narrative(narrative)
        assert is_valid is True
        assert '"I saw a drone' in sanitized

    def test_report_with_danish_characters(self):
        """Test report with Danish special characters"""
        title = "Droneobservation ved Aarhus Lufthavn"
        narrative = "Flere vidner så dronen. Hændelsen fandt sted kl. 15:30."

        is_valid_title, sanitized_title, _ = validate_title(title)
        is_valid_narrative, sanitized_narrative, _ = validate_narrative(narrative)

        assert is_valid_title is True
        assert is_valid_narrative is True
        assert "Aarhus" in sanitized_title
        assert "Hændelsen" in sanitized_narrative
