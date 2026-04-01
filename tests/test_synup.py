"""Tests for the new Synup resource-based client."""

import os

import pytest
import requests_mock

import synup
from synup import Synup, SynupObject, SyncPage
from synup.exceptions import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


# --- Fixtures ---

@pytest.fixture
def client():
    return Synup(api_key="test-key")


@pytest.fixture
def locations_response():
    return {
        "data": {
            "allLocations": {
                "edges": [
                    {
                        "cursor": "TG9jYXRpb246MTQwMjQ=",
                        "node": {
                            "id": "TG9jYXRpb246MTQwMjQ=",
                            "name": "Stumptown Coffee",
                            "city": "New York",
                            "stateIso": "NY",
                        },
                    },
                    {
                        "cursor": "TG9jYXRpb246MTQwMjM=",
                        "node": {
                            "id": "TG9jYXRpb246MTQwMjM=",
                            "name": "Blue Bottle",
                            "city": "San Francisco",
                            "stateIso": "CA",
                        },
                    },
                ],
                "pageInfo": {
                    "hasNextPage": True,
                    "hasPreviousPage": False,
                    "total": 50,
                },
            }
        }
    }


@pytest.fixture
def empty_response():
    return {"data": {"allLocations": {"edges": [], "pageInfo": {"hasNextPage": False}}}}


# --- Client initialization ---

def test_client_reads_env_var(monkeypatch):
    monkeypatch.setenv("SYNUP_API_KEY", "env-key")
    client = Synup()
    assert client.api_key == "env-key"


def test_client_explicit_key_overrides_env(monkeypatch):
    monkeypatch.setenv("SYNUP_API_KEY", "env-key")
    client = Synup(api_key="explicit-key")
    assert client.api_key == "explicit-key"


def test_client_raises_without_key(monkeypatch):
    monkeypatch.delenv("SYNUP_API_KEY", raising=False)
    with pytest.raises(AuthenticationError):
        Synup()


def test_client_default_base_url(client):
    assert client._base_url == "https://api.synup.com"


def test_client_custom_base_url():
    c = Synup(api_key="key", base_url="https://custom.synup.com/")
    assert c._base_url == "https://custom.synup.com"


def test_client_has_resources(client):
    assert hasattr(client, "locations")
    assert hasattr(client, "reviews")
    assert hasattr(client, "listings")
    assert hasattr(client, "analytics")
    assert hasattr(client, "folders")
    assert hasattr(client, "users")
    assert hasattr(client, "keywords")
    assert hasattr(client, "campaigns")
    assert hasattr(client, "connected_accounts")
    assert hasattr(client, "tags")
    assert hasattr(client, "grid_reports")
    assert hasattr(client, "photos")
    assert hasattr(client, "automations")


# --- SynupObject ---

def test_synup_object_attribute_access():
    obj = SynupObject({"name": "Test", "city": "NYC"})
    assert obj.name == "Test"
    assert obj.city == "NYC"


def test_synup_object_dict_access():
    obj = SynupObject({"name": "Test"})
    assert obj["name"] == "Test"


def test_synup_object_nested():
    obj = SynupObject({"outer": {"inner": "value"}})
    assert obj.outer.inner == "value"


def test_synup_object_list_of_dicts():
    obj = SynupObject({"items": [{"name": "a"}, {"name": "b"}]})
    assert obj.items[0].name == "a"
    assert obj.items[1].name == "b"


def test_synup_object_get():
    obj = SynupObject({"name": "Test"})
    assert obj.get("name") == "Test"
    assert obj.get("missing", "default") == "default"


def test_synup_object_contains():
    obj = SynupObject({"name": "Test"})
    assert "name" in obj
    assert "missing" not in obj


def test_synup_object_to_dict():
    data = {"name": "Test", "city": "NYC"}
    obj = SynupObject(data)
    assert obj.to_dict() == data


def test_synup_object_missing_attr():
    obj = SynupObject({"name": "Test"})
    with pytest.raises(AttributeError):
        obj.nonexistent


# --- SyncPage ---

def test_sync_page_iteration():
    page = SyncPage(data=[{"name": "a"}, {"name": "b"}], has_more=False)
    names = [item.name for item in page]
    assert names == ["a", "b"]


def test_sync_page_len():
    page = SyncPage(data=[{"a": 1}, {"b": 2}], has_more=False)
    assert len(page) == 2


def test_sync_page_indexing():
    page = SyncPage(data=[{"name": "first"}, {"name": "second"}], has_more=False)
    assert page[0].name == "first"
    assert page[1].name == "second"


def test_sync_page_has_more():
    page = SyncPage(data=[{"a": 1}], has_more=True, end_cursor="abc")
    assert page.has_more is True


def test_sync_page_next_page_none_when_no_more():
    page = SyncPage(data=[], has_more=False)
    assert page.next_page() is None


def test_sync_page_auto_paging_iter():
    page2 = SyncPage(data=[{"name": "c"}], has_more=False)
    page1 = SyncPage(
        data=[{"name": "a"}, {"name": "b"}],
        has_more=True,
        end_cursor="cursor1",
        _fetch_next=lambda cursor: page2,
    )
    names = [item.name for item in page1.auto_paging_iter()]
    assert names == ["a", "b", "c"]


# --- Exceptions ---

def test_exception_hierarchy():
    assert issubclass(AuthenticationError, APIError)
    assert issubclass(NotFoundError, APIError)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(ValidationError, APIError)
    assert issubclass(APIError, synup.SynupError)
    assert issubclass(APIConnectionError, synup.SynupError)


def test_rate_limit_error_retry_after():
    err = RateLimitError("too fast", status_code=429, retry_after="30")
    assert err.retry_after == 30.0


def test_backward_compat_synup_api_error():
    assert synup.SynupAPIError is APIError


# --- Locations resource ---

def test_locations_list(client, locations_response):
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/locations", json=locations_response)
        page = client.locations.list(first=10)

        assert isinstance(page, SyncPage)
        assert len(page) == 2
        assert page[0].name == "Stumptown Coffee"
        assert page[1].city == "San Francisco"
        assert page.has_more is True
        assert page.total == 50


def test_locations_list_empty(client, empty_response):
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/locations", json=empty_response)
        page = client.locations.list(first=10)
        assert len(page) == 0
        assert page.has_more is False


def test_locations_list_by_ids(client):
    response = {
        "data": {
            "getLocationsByIds": [
                {"id": "TG9jYXRpb246MTY4MDg=", "name": "Test Location"},
            ]
        }
    }
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/locations-by-ids", json=response)
        locations = client.locations.list_by_ids([16808])
        assert len(locations) == 1
        assert locations[0].name == "Test Location"


def test_locations_search(client):
    response = {
        "data": {
            "searchLocations": {
                "edges": [
                    {"cursor": "c1", "node": {"id": "1", "name": "Cafe A"}},
                ],
                "pageInfo": {"hasNextPage": False, "total": 1},
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/locations/search", json=response)
        page = client.locations.search("cafe", first=10)
        assert len(page) == 1
        assert page[0].name == "Cafe A"


def test_locations_create(client):
    response = {
        "data": {
            "createLocation": {
                "success": True,
                "location": {"id": "new-id", "name": "Acme"},
                "errors": [],
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.post("https://api.synup.com/api/v4/locations", json=response)
        result = client.locations.create({"name": "Acme", "city": "NYC"})
        assert result.success is True


# --- Error handling ---

def test_401_raises_authentication_error(client):
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/locations", status_code=401, text="Unauthorized")
        with pytest.raises(AuthenticationError) as exc:
            client.locations.list()
        assert exc.value.status_code == 401


def test_404_raises_not_found_error(client):
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/tags", status_code=404, text="Not found")
        with pytest.raises(NotFoundError) as exc:
            client.tags.list()
        assert exc.value.status_code == 404


def test_400_raises_validation_error(client):
    with requests_mock.Mocker() as m:
        m.post("https://api.synup.com/api/v4/locations", status_code=400, text="Bad request")
        with pytest.raises(ValidationError):
            client.locations.create({"invalid": "data"})


def test_429_raises_rate_limit_error(client):
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.synup.com/api/v4/locations",
            status_code=429,
            text="Rate limited",
            headers={"Retry-After": "60"},
        )
        with pytest.raises(RateLimitError) as exc:
            client.locations.list()
        assert exc.value.retry_after == 60.0


# --- Reviews resource ---

def test_reviews_list(client):
    response = {
        "data": {
            "interactions": {
                "edges": [
                    {"cursor": "c1", "node": {"id": "r1", "content": "Great!", "rating": 5}},
                ],
                "pageInfo": {"hasNextPage": False},
            }
        }
    }
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.synup.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/reviews",
            json=response,
        )
        page = client.reviews.list(16808, first=10)
        assert len(page) == 1
        assert page[0].content == "Great!"
        assert page[0].rating == 5


# --- Listings resource ---

def test_listings_premium(client):
    response = {"data": {"listingsForLocation": [{"id": "l1", "site": "google.com"}]}}
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.synup.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/listings/premium",
            json=response,
        )
        listings = client.listings.premium(16808)
        assert len(listings) == 1
        assert listings[0].site == "google.com"


# --- Analytics resource ---

def test_analytics_google(client):
    response = {"data": {"googleInsights": {"views": 1000}}}
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.synup.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/google-analytics",
            json=response,
        )
        result = client.analytics.google(16808)
        assert result.views == 1000


# --- Folders resource ---

def test_folders_list(client):
    response = {"data": {"getUserFolders": [{"id": "f1", "name": "franchise"}]}}
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/folders/flat", json=response)
        folders = client.folders.list()
        assert len(folders) == 1
        assert folders[0].name == "franchise"


def test_folders_create(client):
    response = {"data": {"createFolder": {"success": True}}}
    with requests_mock.Mocker() as m:
        m.post("https://api.synup.com/api/v4/folders/create", json=response)
        result = client.folders.create("new-folder")
        assert result.success is True


# --- Tags resource ---

def test_tags_list(client):
    response = {"data": {"listAllTags": [{"id": "t1", "name": "vip"}]}}
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/tags", json=response)
        tags = client.tags.list()
        assert len(tags) == 1
        assert tags[0].name == "vip"


# --- Users resource ---

def test_users_list(client):
    response = {"data": {"users": [{"id": "u1", "email": "jane@example.com"}]}}
    with requests_mock.Mocker() as m:
        m.get("https://api.synup.com/api/v4/users", json=response)
        users = client.users.list()
        assert len(users) == 1
        assert users[0].email == "jane@example.com"


def test_users_create(client):
    response = {"data": {"addUser": {"success": True, "user": {"id": "new"}}}}
    with requests_mock.Mocker() as m:
        m.post("https://api.synup.com/api/v4/users/create", json=response)
        result = client.users.create(email="j@example.com", role_id="role1", first_name="Jane")
        assert result.success is True


# --- Keywords resource ---

def test_keywords_list(client):
    response = {"data": {"keywordsByLocationId": [{"id": "k1", "name": "plumber"}]}}
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.synup.com/api/v4/locations/TG9jYXRpb246MTY4MDg=/keywords",
            json=response,
        )
        keywords = client.keywords.list(16808)
        assert len(keywords) == 1
        assert keywords[0].name == "plumber"


# --- Version ---

def test_version():
    assert synup.__version__ == "0.4.0"
