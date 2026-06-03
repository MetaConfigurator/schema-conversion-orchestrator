def simple_cname_convert(text: str) -> str:
    """Simple CNAME conversion"""
    import re
    # Convert to lowercase and replace invalid chars with hyphens
    result = re.sub(r'[^a-z0-9\-]', '-', text.lower())
    # Remove consecutive hyphens
    result = re.sub(r'-+', '-', result)
    # Remove leading/trailing hyphens
    result = result.strip('-')
    # Ensure not empty
    return result if result else 'host'