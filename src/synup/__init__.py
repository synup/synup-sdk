"""Synup Python SDK — build on Synup's local presence infrastructure.

Example:
    import synup

    client = synup.Synup()  # reads SYNUP_API_KEY from env

    for location in client.locations.list(first=10):
        print(location.name, location.city)
"""

from synup._client import Synup
from synup._types import SyncPage, SynupObject
from synup.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    SynupAPIError,
    SynupError,
    ValidationError,
)

# Backward compat
from synup.client import SynupClient

__version__ = "0.4.0"

__all__ = [
    # Client
    "Synup",
    "SynupClient",
    # Types
    "SynupObject",
    "SyncPage",
    # Exceptions
    "SynupError",
    "APIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "InternalServerError",
    "APIConnectionError",
    "SynupAPIError",
    # Version
    "__version__",
]
