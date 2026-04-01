"""Backward-compatible SynupClient.

The old flat-method API still works but the new resource-based API is recommended:

    # New (recommended)
    client = synup.Synup()
    client.locations.list(first=10)

    # Old (still works)
    client = SynupClient(api_key="...")
    client.fetch_all_locations(first=10)
"""

from __future__ import annotations

import base64
import json
import warnings
from typing import Any

import requests

from synup.exceptions import SynupAPIError

DEFAULT_BASE_URL = "https://api.synup.com"


def _encode_location_id(id_value: str | int) -> str:
    if isinstance(id_value, int):
        return base64.b64encode(f"Location:{id_value}".encode()).decode("ascii")
    s = str(id_value).strip()
    if s.isdigit():
        return base64.b64encode(f"Location:{s}".encode()).decode("ascii")
    return s


class SynupClient:
    """Legacy client with flat method API. Use synup.Synup() for the new resource-based API."""

    def __init__(self, api_key: str, base_url: str | None = None):
        warnings.warn(
            "SynupClient is deprecated. Use synup.Synup() instead for the resource-based API.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"API {self._api_key}",
                "Content-Type": "application/json",
            }
        )

    def _api_get(self, path_suffix: str, params: dict | None = None) -> dict[str, Any]:
        url = f"{self._base_url}/api/v4/{path_suffix}"
        response = self._session.get(url, params=params or {})
        if not response.ok:
            raise SynupAPIError(
                message=f"API request failed: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )
        return response.json()

    def _api_post(self, path_suffix: str, json_body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}/api/v4/{path_suffix}"
        response = self._session.post(url, json=json_body)
        if not response.ok:
            raise SynupAPIError(
                message=f"API request failed: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )
        return response.json()

    def _listings_get(
        self, location_id: str | int, path_suffix: str, params: dict | None = None
    ) -> dict[str, Any]:
        encoded_id = _encode_location_id(location_id)
        url = f"{self._base_url}/api/v4/locations/{encoded_id}/{path_suffix}"
        response = self._session.get(url, params=params or {})
        if not response.ok:
            raise SynupAPIError(
                message=f"API request failed: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )
        return response.json()

    # Keeping only a few key methods for backward compat; users should migrate to Synup()

    def fetch_all_locations(self, first=None, after=None, before=None, last=None, fetch_all=False, page_size=100):
        if fetch_all:
            all_nodes = []
            cursor = None
            while True:
                page = self.fetch_all_locations(first=page_size, after=cursor)
                all_nodes.extend(page["locations"])
                if not page["page_info"]["has_next_page"]:
                    break
                cursor = page["page_info"]["end_cursor"]
                if not cursor:
                    break
            return all_nodes
        params = {}
        if first is not None:
            params["first"] = first
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if last is not None:
            params["last"] = last
        data = self._api_get("locations", params)
        all_locs = data.get("data", {}).get("allLocations") or {}
        edges = all_locs.get("edges") or []
        page_info = all_locs.get("pageInfo") or {}
        locations = [edge["node"] for edge in edges]
        return {
            "success": True,
            "locations": locations,
            "page_info": {
                "has_next_page": page_info.get("hasNextPage", False),
                "has_previous_page": page_info.get("hasPreviousPage", False),
                "start_cursor": edges[0]["cursor"] if edges else None,
                "end_cursor": edges[-1]["cursor"] if edges else None,
            },
            "raw": data,
        }

    def create_location(self, input: dict[str, Any]) -> dict[str, Any]:
        data = self._api_post("locations", {"input": input})
        return data.get("data", {}).get("createLocation") or {}
