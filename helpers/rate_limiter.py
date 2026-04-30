from collections import deque
from threading import Lock
from time import time
from helpers.environment import RATE_LIMIT_PER_MINUTE

_lock = Lock()
_timestamps: deque = deque()


def check_rate_limit() -> bool:
    """Return True if the request is within the allowed rate, False if exceeded."""
    now = time()
    with _lock:
        while _timestamps and now - _timestamps[0] > 60:
            _timestamps.popleft()
        if len(_timestamps) >= RATE_LIMIT_PER_MINUTE:
            return False
        _timestamps.append(now)
        return True
