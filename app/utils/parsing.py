from __future__ import annotations
from typing import Tuple, Dict


def parse_command_text(text: string) -> Tuple[str, str, Dict[str, str]]:
    if not text or not text.startswith("/"):
        raise ValueError("invalid_command")
    parts = text.strip().split()
    if len(parts) < 2:
        raise ValueError("missing_recipient")
    code = parts[0].lstrip("/")
    recipient = parts[1]
    variables: Dict[str, str] = {}
    for token in parts[2:]:
        if "=" in token:
            key, value = token.split("=", 1)
            variables[key] = value
    return code, recipient, variables
