import re

def sanitize_input(user_query: str) -> str:
    # Block common prompt injection phrases
    injection_patterns = [
        r"ignore previous instructions",
        r"disregard all rules",
        r"you are nowDAN",
        r"system prompt override"
    ]
    for pattern in injection_patterns:
        if re.search(pattern, user_query, re.IGNORECASE):
            raise ValueError("Security Violation: Potential prompt injection detected.")
            
    # Redact potential PII / Employee IDs (e.g., EMP-1234 or SSN-like patterns)
    redacted = re.sub(r'\bEMP-\d{4}\b', '[REDACTED_EMP]', user_query)
    redacted = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', redacted)
    return redacted