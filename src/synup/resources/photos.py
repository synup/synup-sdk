"""Photos resource — client.photos.*"""

from __future__ import annotations

from typing import Any

from synup._types import SynupObject
from synup._utils import encode_location_id
from synup.resources._base import APIResource


class Photos(APIResource):
    """Manage location photos.

    Example:
        photos = client.photos.list(16808)
        client.photos.add(16808, [{"photo": "https://example.com/img.jpg", "type": "ADDITIONAL"}])
    """

    def list(self, location_id: str | int) -> list[SynupObject]:
        """Get photos attached to a location."""
        data = self._location_get(location_id, "photos")
        items = data.get("data", {}).get("mediaFilesOfLocation") or []
        return [SynupObject(item) for item in items]

    def add(self, location_id: str | int, photos: list[dict[str, Any]]) -> SynupObject:
        """Add photos to a location. Each item needs 'photo' (URL) and 'type' (LOGO, COVER, ADDITIONAL)."""
        data = self._post(
            "locations/photos",
            {"input": {"locationId": encode_location_id(location_id), "photos": photos}},
        )
        return SynupObject(data.get("data", {}).get("addLocationPhotos") or {})

    def remove(self, location_id: str | int, photo_ids: list[str]) -> SynupObject:
        """Remove photos from a location."""
        data = self._post(
            "locations/photos/remove",
            {"input": {"locationId": encode_location_id(location_id), "photoIds": photo_ids}},
        )
        return SynupObject(data.get("data", {}).get("removeLocationPhotos") or {})

    def star(self, location_id: str | int, media_ids: list[str], *, starred: bool = True) -> SynupObject:
        """Star or unstar photos. Max 4 starred photos per account."""
        data = self._post(
            "locations/photos/star",
            {"input": {"locationId": encode_location_id(location_id), "mediaIds": media_ids, "starred": starred}},
        )
        return SynupObject(data.get("data", {}).get("starUnstarLocationPhotos") or {})

    def upload_status(self, request_id: str) -> SynupObject:
        """Get processing status for a bulk photo upload."""
        data = self._get(f"locations/photos/requests/{request_id}")
        return SynupObject(data.get("data", {}).get("bulkImageProcessingStatus") or {})
