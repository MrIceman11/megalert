from flask import request
from helpers.environment import API_TOKEN, AUTH_SECRET


def is_authorized(legacy_secret=None):
    """Check Authorization: Bearer <token> header, fall back to legacy secret."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:] == API_TOKEN
    # legacy: plain secret via query param or JSON body
    if legacy_secret:
        return legacy_secret == AUTH_SECRET
    return False
