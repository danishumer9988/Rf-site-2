from django import template

register = template.Library()

@register.filter
def splitlines(value):
    """Split a string by newline and return a list of non‑empty stripped lines."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]