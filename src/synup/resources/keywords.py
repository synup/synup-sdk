"""Keywords resource — client.keywords.*"""

from __future__ import annotations

from typing import Any

from synup._types import SynupObject
from synup._utils import encode_location_id
from synup.resources._base import APIResource


class Keywords(APIResource):
    """Manage tracked keywords for ranking.

    Example:
        keywords = client.keywords.list(16808)
        client.keywords.add(16808, ["plumber", "plumbing near me"])
    """

    def list(self, location_id: str | int) -> list[SynupObject]:
        """Get all tracked keywords for a location."""
        data = self._location_get(location_id, "keywords")
        items = data.get("data", {}).get("keywordsByLocationId") or []
        return [SynupObject(item) for item in items]

    def performance(
        self, location_id: str | int, *, from_date: str | None = None, to_date: str | None = None
    ) -> list[SynupObject]:
        """Get ranking performance for a location's keywords."""
        params: dict[str, str] = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._location_get(location_id, "keywords-performance", params)
        items = data.get("data", {}).get("keywordsByLocationId") or []
        return [SynupObject(item) for item in items]

    def add(self, location_id: str | int, keywords: list[str]) -> list[SynupObject]:
        """Add keywords to a location. Returns the created keyword objects."""
        data = self._post(
            "locations/keywords",
            {"locationId": encode_location_id(location_id), "inputKeywords": keywords},
        )
        result = data.get("data", {}).get("addKeywords") or {}
        items = result.get("keywords") or []
        return [SynupObject(item) for item in items]

    def archive(self, keyword_id: str) -> SynupObject:
        """Archive a keyword so it is no longer tracked."""
        data = self._post("locations/keywords/archive", {"id": keyword_id})
        result = data.get("data", {}).get("archiveKeyword") or {}
        return SynupObject(result.get("keyword") or {})
