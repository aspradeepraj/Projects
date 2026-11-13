import re

class GovernanceGuardrails:
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system prompt",
        r"bypass compliance",
        r"override risk score"
    ]

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError(f"Security Alert: Potential Prompt Injection blocked ({pattern}).")
        
        # Redact email addresses and SSNs/Employee IDs
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
        text = re.sub(r'\bEMP-\d{4,6}\b', '[REDACTED_EMP_ID]', text)
        return text