"""Locations resource — client.locations.*"""

from __future__ import annotations

import json
from typing import Any

from synup._types import SynupObject, SyncPage
from synup._utils import encode_location_id
from synup.resources._base import APIResource


class Locations(APIResource):
    """Manage locations.

    Example:
        # List locations
        page = client.locations.list(first=10)
        for loc in page:
            print(loc.name, loc.city)

        # Auto-paginate
        for loc in client.locations.list(first=50).auto_paging_iter():
            print(loc.name)

        # Create
        result = client.locations.create({"name": "Acme", "street": "123 Main St", ...})
    """

    def list(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        before: str | None = None,
        last: int | None = None,
    ) -> SyncPage:
        """List locations with cursor-based pagination.

        Returns:
            SyncPage of location objects. Use .auto_paging_iter() to iterate all.
        """
        params: dict[str, Any] = {}
        if first is not None:
            params["first"] = first
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if last is not None:
            params["last"] = last

        data = self._get("locations", params)
        all_locs = data.get("data", {}).get("allLocations") or {}
        edges = all_locs.get("edges") or []
        page_info = all_locs.get("pageInfo") or {}
        items = [edge["node"] for edge in edges]
        end_cursor = edges[-1]["cursor"] if edges else None

        return SyncPage(
            data=items,
            has_more=page_info.get("hasNextPage", False),
            end_cursor=end_cursor,
            total=page_info.get("total"),
            _fetch_next=lambda cursor: self.list(first=first, after=cursor),
        )

    def retrieve(self, location_id: str | int) -> SynupObject:
        """Get a single location by ID.

        Args:
            location_id: Numeric (e.g. 16808) or base64-encoded ID.
        """
        results = self.list_by_ids([location_id])
        if not results:
            from synup.exceptions import NotFoundError

            raise NotFoundError(f"Location {location_id} not found", status_code=404)
        return results[0]

    def list_by_ids(self, location_ids: list[str | int]) -> list[SynupObject]:
        """Get locations by a list of IDs (numeric or base64)."""
        if not location_ids:
            return []
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._get("locations-by-ids", {"ids": json.dumps(encoded)})
        items = data.get("data", {}).get("getLocationsByIds") or []
        return [SynupObject(item) for item in items]

    def list_by_store_codes(self, store_codes: list[str]) -> list[SynupObject]:
        """Get locations matching the given store codes."""
        if not store_codes:
            return []
        data = self._get("locations-by-store-codes", {"storeCodes": json.dumps(store_codes)})
        items = data.get("data", {}).get("getLocationsByStoreCodes") or []
        return [SynupObject(item) for item in items]

    def search(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        first: int | None = None,
        after: str | None = None,
        before: str | None = None,
        last: int | None = None,
    ) -> SyncPage:
        """Search locations by keyword (name, address, or store ID).

        Args:
            query: Search term.
            fields: Restrict search to specific fields (e.g. ["name"], ["store_id"]).
        """
        params: dict[str, Any] = {"query": query}
        if fields is not None:
            params["fields"] = json.dumps(fields)
        if first is not None:
            params["first"] = first
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if last is not None:
            params["last"] = last

        data = self._get("locations/search", params)
        result = data.get("data", {}).get("searchLocations") or {}
        edges = result.get("edges") or []
        page_info = result.get("pageInfo") or {}
        items = [e["node"] for e in edges]
        end_cursor = edges[-1]["cursor"] if edges else None

        return SyncPage(
            data=items,
            has_more=page_info.get("hasNextPage", False),
            end_cursor=end_cursor,
            total=page_info.get("total"),
            _fetch_next=lambda cursor: self.search(query, fields=fields, first=first, after=cursor),
        )

    def list_by_folder(
        self, *, folder_id: str | None = None, folder_name: str | None = None
    ) -> list[SynupObject]:
        """Get all locations in a folder (including subfolders)."""
        if not folder_id and not folder_name:
            raise ValueError("Provide either folder_id or folder_name")
        params: dict[str, str] = {}
        if folder_id:
            params["folderId"] = folder_id
        if folder_name:
            params["folderName"] = folder_name
        data = self._get("folder-locations", params)
        items = data.get("data", {}).get("getLocationsForFolder") or []
        return [SynupObject(item) for item in items]

    def list_by_tags(
        self,
        tags: list[str],
        *,
        archived: bool | None = None,
        first: int | None = None,
        after: str | None = None,
        before: str | None = None,
        last: int | None = None,
    ) -> SyncPage:
        """Get locations with any of the given tags."""
        if not tags:
            return SyncPage(data=[], has_more=False)
        params: dict[str, Any] = {"tags": json.dumps(tags)}
        if archived is not None:
            params["archived"] = json.dumps(archived)
        if first is not None:
            params["first"] = first
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if last is not None:
            params["last"] = last

        data = self._get("tags/locations", params)
        result = data.get("data", {}).get("searchLocationsByTag") or {}
        edges = result.get("edges") or []
        page_info = result.get("pageInfo") or {}
        items = [e["node"] for e in edges]
        end_cursor = edges[-1]["cursor"] if edges else None

        return SyncPage(
            data=items,
            has_more=page_info.get("hasNextPage", False),
            end_cursor=end_cursor,
            total=page_info.get("total"),
            _fetch_next=lambda cursor: self.list_by_tags(tags, archived=archived, first=first, after=cursor),
        )

    def create(self, input: dict[str, Any]) -> SynupObject:
        """Create a new location. Pass camelCase field names.

        Args:
            input: Location data dict. Required: name, storeId, street, city, stateIso,
                   postalCode, countryIso, phone.
        """
        data = self._post("locations", {"input": input})
        return SynupObject(data.get("data", {}).get("createLocation") or {})

    def update(self, input: dict[str, Any]) -> SynupObject:
        """Update a location. Pass id plus fields to change."""
        if "id" in input:
            input = {**input, "id": encode_location_id(input["id"])}
        data = self._post("locations/update", {"input": input})
        return SynupObject(data.get("data", {}).get("updateLocation") or {})

    def archive(self, location_ids: list[str | int]) -> SynupObject:
        """Archive one or more locations."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post("locations/archive", {"input": {"locationIds": encoded}})
        return SynupObject(data.get("data", {}).get("archiveLocations") or {})

    def activate(self, location_ids: list[str | int]) -> SynupObject:
        """Reactivate previously archived locations."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post("locations/activate", {"input": {"locationIds": encoded}})
        return SynupObject(data.get("data", {}).get("activateLocations") or {})

    def cancel_archive(
        self, location_ids: list[str | int], selection_type: str, changed_by: str
    ) -> SynupObject:
        """Cancel a scheduled archival."""
        encoded = [encode_location_id(lid) for lid in location_ids]
        data = self._post(
            "locations/cancel_archive",
            {"input": {"locationIds": encoded, "selectionType": selection_type, "changedBy": changed_by}},
        )
        return SynupObject(data.get("data", {}).get("cancelLocationsArchive") or {})

    def connection_info(self, location_id: str | int) -> SynupObject:
        """Get OAuth connection status (Google/Facebook) for a location."""
        data = self._location_get(location_id, "connection_info")
        return SynupObject(data.get("data", {}).get("locationConnectionInfo") or {})
