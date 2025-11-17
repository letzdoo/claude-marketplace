"""PII redaction utilities for ReasoningBank."""

import re
from typing import Dict, Any


# Patterns for common PII
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
IP_ADDRESS_PATTERN = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
UUID_PATTERN = re.compile(
    r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
    re.IGNORECASE
)
URL_PATTERN = re.compile(
    r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
)

# API keys and tokens
API_KEY_PATTERN = re.compile(
    r'\b(?:api[_-]?key|token|secret|password|passwd|pwd)["\s:=]+["\']?([a-zA-Z0-9_\-]{16,})["\']?',
    re.IGNORECASE
)


def redact_pii(text: str, placeholder: str = "[REDACTED]") -> str:
    """
    Redact PII from text.

    Args:
        text: Input text potentially containing PII
        placeholder: Replacement string for redacted content

    Returns:
        Text with PII redacted
    """
    # Redact emails
    text = EMAIL_PATTERN.sub(f"{placeholder}_EMAIL", text)

    # Redact phone numbers
    text = PHONE_PATTERN.sub(f"{placeholder}_PHONE", text)

    # Redact SSN
    text = SSN_PATTERN.sub(f"{placeholder}_SSN", text)

    # Redact credit cards
    text = CREDIT_CARD_PATTERN.sub(f"{placeholder}_CC", text)

    # Redact full IP addresses (keep last octet for debugging)
    def redact_ip(match):
        ip = match.group(0)
        parts = ip.split('.')
        if len(parts) == 4:
            return f"XXX.XXX.XXX.{parts[3]}"
        return f"{placeholder}_IP"

    text = IP_ADDRESS_PATTERN.sub(redact_ip, text)

    # Redact API keys and tokens
    text = API_KEY_PATTERN.sub(f"\\1={placeholder}_KEY", text)

    # Redact full UUIDs but keep format recognizable
    text = UUID_PATTERN.sub(f"{placeholder}_UUID", text)

    # Partially redact URLs (keep domain for context)
    def redact_url(match):
        url = match.group(0)
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}/[REDACTED_PATH]"
        except:
            return f"{placeholder}_URL"

    text = URL_PATTERN.sub(redact_url, text)

    return text


def redact_memory_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact PII from a memory item.

    Args:
        item: Memory item dictionary

    Returns:
        Memory item with PII redacted
    """
    redacted = item.copy()

    # Redact title, description, content
    if 'title' in redacted:
        redacted['title'] = redact_pii(redacted['title'])

    if 'description' in redacted:
        redacted['description'] = redact_pii(redacted['description'])

    if 'content' in redacted:
        redacted['content'] = redact_pii(redacted['content'])

    # Redact evidence if present
    if 'source' in redacted and 'evidence' in redacted['source']:
        # Keep evidence IDs but redact any text in them
        evidence = redacted['source']['evidence']
        if isinstance(evidence, list):
            redacted['source']['evidence'] = [
                redact_pii(str(e)) for e in evidence
            ]

    return redacted


def contains_sensitive_data(text: str) -> bool:
    """
    Check if text contains potentially sensitive data.

    Args:
        text: Text to check

    Returns:
        True if sensitive data detected
    """
    patterns = [
        EMAIL_PATTERN,
        PHONE_PATTERN,
        SSN_PATTERN,
        CREDIT_CARD_PATTERN,
        API_KEY_PATTERN,
    ]

    for pattern in patterns:
        if pattern.search(text):
            return True

    return False
