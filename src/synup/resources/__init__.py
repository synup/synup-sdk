"""Synup API resources."""

from synup.resources.locations import Locations
from synup.resources.reviews import Reviews
from synup.resources.listings import Listings
from synup.resources.analytics import Analytics
from synup.resources.folders import Folders
from synup.resources.users import Users
from synup.resources.keywords import Keywords
from synup.resources.campaigns import Campaigns
from synup.resources.connected_accounts import ConnectedAccounts
from synup.resources.tags import Tags
from synup.resources.grid_reports import GridReports
from synup.resources.photos import Photos
from synup.resources.automations import Automations
from synup.resources.workflows import Workflows

__all__ = [
    "Locations",
    "Reviews",
    "Listings",
    "Analytics",
    "Folders",
    "Users",
    "Keywords",
    "Campaigns",
    "ConnectedAccounts",
    "Tags",
    "GridReports",
    "Photos",
    "Automations",
    "Workflows",
]
