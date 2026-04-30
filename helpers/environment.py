from os import getenv
from os.path import join, dirname
from dotenv import load_dotenv
import logging
import sys

dotenv_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

def _require(name):
    value = getenv(name)
    if not value:
        logging.critical("Required environment variable '%s' is not set. Exiting.", name)
        sys.exit(1)
    return value

# API configuration
MEGALERT_HOST = getenv("MEGALERT_HOST", "0.0.0.0")
MEGALERT_PORT = int(getenv("MEGALERT_PORT", "5000"))
MEGALERT_DEBUG = getenv("MEGALERT_DEBUG", "false").lower() == "true"

# Mikrotik device configuration
MIKROTIK_HOST = _require("MIKROTIK_HOST")
MIKROTIK_PORT = int(getenv("MIKROTIK_PORT", "8728"))
MIKROTIK_USER = _require("MIKROTIK_USER")
MIKROTIK_PASS = _require("MIKROTIK_PASS")
MIKROTIK_SMS_PORT = getenv("MIKROTIK_SMS_PORT", "lte1")

# Authentication — API_TOKEN is the primary secret (Bearer token)
API_TOKEN = _require("API_TOKEN")
AUTH_SECRET = getenv("AUTH_SECRET", API_TOKEN)  # legacy fallback

# Validation
_raw_cc = getenv("ALLOWED_COUNTRY_CODES", "")
ALLOWED_COUNTRY_CODES = [c.strip() for c in _raw_cc.split(",") if c.strip()]
MAX_MESSAGE_LENGTH = int(getenv("MAX_MESSAGE_LENGTH", "480"))

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(getenv("RATE_LIMIT_PER_MINUTE", "10"))
