from __future__ import annotations
from typing import Tuple, Dict, List


def parse_command_text(text: str) -> Tuple[str, List[str], Dict[str, str]]:
    """
    Parse command text to support both single and bulk emails.
    
    Supports:
    - Single: /code email@domain.com key=value
    - Bulk comma: /code email1@domain.com,email2@domain.com key=value
    - Bulk newline: /code\nemail1@domain.com\nemail2@domain.com\nkey=value
    - Random templates: /random template1,template2,template3 email1@domain.com,email2@domain.com key=value
    """
    if not text or not text.startswith("/"):
        raise ValueError("invalid_command")
    
    lines = text.strip().split('\n')
    first_line = lines[0].strip()
    
    # Parse first line: /code email(s) or /random template1,template2 email1,email2
    parts = first_line.split()
    if len(parts) < 2:
        raise ValueError("missing_recipient")
    
    code = parts[0].lstrip("/")
    second_part = parts[1]
    
    # Handle random template command
    if code == "random":
        # Format: /random template1,template2,template3 email1@domain.com,email2@domain.com key=value
        if ',' not in second_part:
            raise ValueError("random_command_requires_templates")
        
        # First part contains template codes, second part contains emails
        template_codes = [code.strip() for code in second_part.split(',') if code.strip()]
        
        # Check if we have more parts for emails
        if len(parts) < 3:
            raise ValueError("random_command_requires_emails")
        
        # Third part contains emails
        recipients_text = parts[2]
        if ',' in recipients_text:
            recipients = [email.strip() for email in recipients_text.split(',') if email.strip()]
        else:
            recipients = [recipients_text.strip()]
        
        # Add template codes as first recipient for special handling
        recipients = [','.join(template_codes)] + recipients
        
        # Parse variables from remaining parts
        variables: Dict[str, str] = {}
        for token in parts[3:]:
            if "=" in token:
                key, value = token.split("=", 1)
                variables[key] = value
        
        # Parse variables from newlines
        for line in lines[1:]:
            line = line.strip()
            if "=" in line and '@' not in line:
                key, value = line.split("=", 1)
                variables[key] = value
        
        # Validate recipients
        recipients = [r for r in recipients if '@' in r and '.' in r or ',' in r]  # Allow template codes in first position
        
        if len(recipients) < 2:  # Need at least template codes + one email
            raise ValueError("random_command_requires_emails")
        
        return code, recipients, variables
    
    # Handle regular commands
    # Handle recipients (single or comma-separated)
    if ',' in second_part:
        # Comma-separated: email1@domain.com,email2@domain.com
        recipients = [email.strip() for email in second_part.split(',') if email.strip()]
    else:
        # Single email or newline format
        recipients = [second_part.strip()]
    
    # Handle newline-separated emails (if any)
    if len(lines) > 1:
        for line in lines[1:]:
            line = line.strip()
            if line and '@' in line and '=' not in line:
                # This looks like an email address
                recipients.append(line)
    
    # Parse variables from remaining parts
    variables: Dict[str, str] = {}
    
    # Variables from first line
    for token in parts[2:]:
        if "=" in token:
            key, value = token.split("=", 1)
            variables[key] = value
    
    # Variables from newlines
    for line in lines[1:]:
        line = line.strip()
        if "=" in line and '@' not in line:
            # This looks like a variable
            key, value = line.split("=", 1)
            variables[key] = value
    
    # Remove duplicates and validate
    recipients = list(set(recipients))  # Remove duplicates
    recipients = [r for r in recipients if '@' in r and '.' in r]  # Basic email validation
    
    if not recipients:
        raise ValueError("no_valid_emails")
    
    return code, recipients, variables
