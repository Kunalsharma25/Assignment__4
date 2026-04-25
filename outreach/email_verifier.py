import re
import dns.resolver
from typing import Tuple

def is_valid_syntax(email: str) -> bool:
    """Basic regex check for email syntax."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def has_mx_record(email: str) -> bool:
    """Checks if the email domain has valid MX records with a timeout."""
    try:
        domain = email.split('@')[-1]
        # Use a short timeout (2s) to keep the pipeline fast
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 2
        records = resolver.resolve(domain, 'MX')
        return len(records) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, Exception):
        return False

def verify_email(email: str) -> Tuple[bool, str]:
    """
    Performs lightweight verification.
    Returns (is_valid, reason)
    """
    if not email:
        return False, "No email provided"
        
    if not is_valid_syntax(email):
        return False, "Invalid syntax"
        
    if not has_mx_record(email):
        return False, "No mail server (MX) found for domain"
        
    return True, "Valid"
