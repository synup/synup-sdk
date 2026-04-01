"""Connected accounts resource — client.connected_accounts.*"""

from __future__ import annotations

from typing import Any

from synup._types import SynupObject
from synup._utils import encode_location_id
from synup.resources._base import APIResource


class ConnectedAccounts(APIResource):
    """Manage Google and Facebook connected accounts.

    Example:
        accounts = client.connected_accounts.list()
        url = client.connected_accounts.connect_google("https://ok.com", "https://err.com")
    """

    def list(
        self,
        *,
        publisher: str | None = None,
        status: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
    ) -> SynupObject:
        """Get connected third-party accounts with optional filters."""
        params: dict[str, Any] = {}
        if publisher is not None:
            params["publisher"] = publisher
        if status is not None:
            params["status"] = status
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        data = self._get("connected-accounts", params)
        return SynupObject(data.get("data", {}).get("connectedAccountsInfo") or {})

    def details(self, connected_account_id: str) -> SynupObject:
        """Get details for a connected account."""
        data = self._get(f"connected-accounts/{connected_account_id}/details")
        return SynupObject(data.get("data", {}).get("connectedAccountDetails") or {})

    def folders(self, connected_account_id: str, *, folder_name: str | None = None) -> list[SynupObject]:
        """Get folders under a connected Google account."""
        params: dict[str, str] = {}
        if folder_name is not None:
            params["folderName"] = folder_name
        data = self._get(f"connected-accounts/{connected_account_id}/folders", params)
        items = data.get("data", {}).get("getFoldersUnderGoogleAccount") or []
        return [SynupObject(item) for item in items]

    def suggestions(
        self, connected_account_id: str, *, page: int | None = None, per_page: int | None = None
    ) -> SynupObject:
        """Get suggested matches between a connected account's listings and Synup locations."""
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        data = self._get(f"connected-accounts/{connected_account_id}/connection-suggestions", params)
        return SynupObject(data.get("data", {}).get("connectionSuggestionsForAccount") or {})

    def listings(
        self,
        connected_account_id: str,
        *,
        location_info: str | None = None,
        page: int | None = None,
        per_page: int | None = None,
    ) -> SynupObject:
        """Get listings the connected account has access to."""
        payload: dict[str, Any] = {"connectedAccountId": connected_account_id}
        if location_info is not None:
            payload["locationInfo"] = location_info
        if page is not None:
            payload["page"] = page
        if per_page is not None:
            payload["perPage"] = per_page
        data = self._post("connected-accounts/connected-account-listings", payload)
        return SynupObject(data.get("data", {}).get("connectedAccountListings") or {})

    def connect_google(self, success_url: str, error_url: str) -> SynupObject:
        """Get a URL to connect a Google account. Valid 24 hours."""
        data = self._post(
            "connected-accounts/connect-google",
            {"input": {"successUrl": success_url, "errorUrl": error_url}},
        )
        return SynupObject(data.get("data", {}).get("bulkConnectLinkForGoogle") or {})

    def connect_facebook(self, success_url: str, error_url: str) -> SynupObject:
        """Get a URL to connect a Facebook account. Valid 24 hours."""
        data = self._post(
            "connected-accounts/connect-facebook",
            {"input": {"successUrl": success_url, "errorUrl": error_url}},
        )
        return SynupObject(data.get("data", {}).get("bulkConnectLinkForFacebook") or {})

    def disconnect_google(self, connected_account_id: str) -> SynupObject:
        """Disconnect a Google connected account."""
        data = self._post(
            "connected-accounts/disconnect-google",
            {"input": {"connectedAccountId": connected_account_id}},
        )
        return SynupObject(data.get("data", {}).get("gmbBulkDisconnect") or {})

    def disconnect_facebook(self, connected_account_id: str) -> SynupObject:
        """Disconnect a Facebook connected account."""
        data = self._post(
            "connected-accounts/disconnect-facebook",
            {"input": {"connectedAccountId": connected_account_id}},
        )
        return SynupObject(data.get("data", {}).get("fbBulkDisconnect") or {})

    def trigger_matches(self, connected_account_ids: list[str]) -> SynupObject:
        """Trigger matching of profiles to Synup locations."""
        data = self._post(
            "connected-accounts/trigger-matches",
            {"input": {"connectedAccountIds": connected_account_ids}},
        )
        return SynupObject(data.get("data", {}).get("connectedAccountsTriggerMatches") or {})

    def confirm_matches(self, match_record_ids: list[str]) -> SynupObject:
        """Confirm suggested matches between connected account listings and locations."""
        data = self._post(
            "connected-accounts/confirm-matches",
            {"input": {"matchRecordIds": match_record_ids}},
        )
        return SynupObject(data.get("data", {}).get("confirmConnectMatches") or {})

    def oauth_url(
        self, location_id: str | int, site: str, success_url: str, error_url: str
    ) -> SynupObject:
        """Get a URL to connect a Google/Facebook profile to a single location. Valid 24 hours."""
        data = self._post(
            "locations/oauth_connect_url",
            {
                "input": {
                    "locationId": encode_location_id(location_id),
                    "site": site.upper(),
                    "successUrl": success_url,
                    "errorUrl": error_url,
                }
            },
        )
        return SynupObject(data.get("data", {}).get("connectUrl") or {})

    def oauth_disconnect(self, location_id: str | int, site: str) -> SynupObject:
        """Disconnect a Google/Facebook profile from a single location."""
        data = self._post(
            "locations/oauth-disconnect",
            {"input": {"locationId": encode_location_id(location_id), "site": site.upper()}},
        )
        return SynupObject(data.get("data", {}).get("disconnectConnectedAccountsLocations") or {})
