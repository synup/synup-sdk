"""Tags resource — client.tags.*"""

from __future__ import annotations

from synup._types import SynupObject
from synup._utils import encode_location_id
from synup.resources._base import APIResource


class Tags(APIResource):
    """Manage location tags.

    Example:
        tags = client.tags.list()
        client.tags.add(16808, "vip")
    """

    def list(self) -> list[SynupObject]:
        """Get all tags in the account."""
        data = self._get("tags")
        items = data.get("data", {}).get("listAllTags") or []
        return [SynupObject(item) for item in items]

    def add(self, location_id: str | int, tag: str) -> SynupObject:
        """Add a tag to a location (tag is created if it doesn't exist)."""
        data = self._post(
            "locations/tags",
            {"input": {"locationId": encode_location_id(location_id), "tag": tag}},
        )
        return SynupObject(data.get("data", {}).get("addTag") or {})

    def remove(self, location_id: str | int, tag: str) -> SynupObject:
        """Remove a tag from a location."""
        data = self._post(
            "locations/tags/remove",
            {"input": {"locationId": encode_location_id(location_id), "tag": tag}},
        )
        return SynupObject(data.get("data", {}).get("removeTag") or {})
