"""Analytics resource — client.analytics.*"""

from __future__ import annotations

from typing import Any

from synup._types import SynupObject
from synup._utils import encode_location_id
from synup.resources._base import APIResource


class Analytics(APIResource):
    """Profile and ranking analytics.

    Example:
        google = client.analytics.google(16808, from_date="2024-01-01")
        bing = client.analytics.bing(16808)
    """

    def google(
        self, location_id: str | int, *, from_date: str | None = None, to_date: str | None = None
    ) -> SynupObject:
        """Get Google (GMB) profile analytics for a location."""
        params: dict[str, str] = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._location_get(location_id, "google-analytics", params)
        return SynupObject(data.get("data", {}).get("googleInsights") or {})

    def bing(
        self, location_id: str | int, *, from_date: str | None = None, to_date: str | None = None
    ) -> SynupObject:
        """Get Bing profile analytics for a location."""
        params: dict[str, str] = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._location_get(location_id, "bing-analytics", params)
        return SynupObject(data.get("data", {}).get("bingInsights") or {})

    def facebook(
        self, location_id: str | int, *, from_date: str | None = None, to_date: str | None = None
    ) -> SynupObject:
        """Get Facebook page analytics for a location."""
        params: dict[str, str] = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._location_get(location_id, "facebook-analytics", params)
        return SynupObject(data.get("data", {}).get("facebookInsights") or {})

    def rankings_timeline(
        self, location_ids: list[str | int], from_date: str, to_date: str, source: list[str]
    ) -> list[SynupObject]:
        """Get ranking positions over time for locations and source (e.g. Google)."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post(
            "locations/ranking-analytics-timeline",
            {"fromDate": from_date, "toDate": to_date, "locationIds": encoded, "source": source},
        )
        items = data.get("data", {}).get("rankingsRollupByDate") or []
        return [SynupObject(item) for item in items]

    def rankings_histogram(
        self, location_ids: list[str | int], from_date: str, to_date: str, source: list[str]
    ) -> list[SynupObject]:
        """Get ranking histogram by keyword count."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post(
            "locations/ranking-sitewise-histogram",
            {"fromDate": from_date, "toDate": to_date, "locationIds": encoded, "source": source},
        )
        items = data.get("data", {}).get("rankingsRollupByKeywordCount") or []
        return [SynupObject(item) for item in items]
