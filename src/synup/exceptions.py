"""Synup SDK exceptions. Catch specific errors for fine-grained handling."""

from __future__ import annotations


class SynupError(Exception):
    """Base exception for all Synup SDK errors."""


class APIError(SynupError):
    """Raised when the API returns a non-2xx response.

    Attributes:
        status_code: HTTP status code (e.g. 400, 401, 500).
        response_body: Raw response text from the API.

    Example:
        try:
            client.locations.list()
        except synup.APIError as e:
            print(e.status_code, e.response_body)
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        full = f"{message} — {response_body}" if response_body else message
        super().__init__(full)


class AuthenticationError(APIError):
    """401 — Invalid or missing API key."""


class PermissionDeniedError(APIError):
    """403 — Insufficient permissions for this action."""


class NotFoundError(APIError):
    """404 — Resource not found."""


class ValidationError(APIError):
    """400/422 — Invalid request parameters."""


class RateLimitError(APIError):
    """429 — Too many requests. Check retry_after for backoff.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header), or None.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        retry_after: str | None = None,
    ):
        super().__init__(message, status_code=status_code, response_body=response_body)
        self.retry_after = float(retry_after) if retry_after else None


class InternalServerError(APIError):
    """5xx — Server-side error. Safe to retry."""


class APIConnectionError(SynupError):
    """Network failure — could not reach the API."""


# Backward compat
SynupAPIError = APIError
