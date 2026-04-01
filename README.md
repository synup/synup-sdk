# Synup SDK

Build local presence automations in minutes — review auto-responders, listings monitors, reputation dashboards, bulk onboarding tools, and more.

## Installation

```bash
pip install synup
```

## Quick start: auto-reply to reviews in 10 lines

```python
import synup

client = synup.Synup()  # reads SYNUP_API_KEY from env

# Auto-reply to all 4-5 star reviews that haven't been answered
results = client.workflows.auto_reply_to_reviews(
    16808,
    template="Thanks for the {rating}-star review! We appreciate your support.",
    min_rating=4,
)
print(f"Replied to {len(results)} reviews")
```

## Quick start: listings health audit in 3 lines

```python
import synup

client = synup.Synup()

audit = client.workflows.listings_health_audit(16808)
print(f"Health score: {audit.health_score}%")
print(f"Synced: {audit.synced_count}, Issues: {audit.issue_count}")
print(f"Duplicates found: {len(audit.duplicates)}")
```

## Configuration

```python
import synup

# Minimal — reads SYNUP_API_KEY env var
client = synup.Synup()

# Explicit key
client = synup.Synup(api_key="your-api-key")

# With custom config
client = synup.Synup(
    api_key="your-api-key",
    timeout=300.0,       # request timeout in seconds (default: 240)
    max_retries=3,       # auto-retry on 429/5xx (default: 2)
)
```

## Locations

```python
# List with pagination
page = client.locations.list(first=10)
for loc in page:
    print(loc.name, loc.city, loc.stateIso)

# Next page
if page.has_more:
    next_page = page.next_page()

# Auto-paginate all
for loc in client.locations.list(first=100).auto_paging_iter():
    print(loc.name)

# Retrieve single location
location = client.locations.retrieve(16808)
print(location.name)

# Search
page = client.locations.search("cafe", first=20)

# By IDs, store codes, folder, or tags
locations = client.locations.list_by_ids([16808, 16749])
locations = client.locations.list_by_store_codes(["STORE01", "STORE02"])
locations = client.locations.list_by_folder(folder_name="franchise")
page = client.locations.list_by_tags(["vip", "recent"], first=20)

# Create
result = client.locations.create({
    "name": "Acme Inc",
    "storeId": "ACME01",
    "street": "123 Main St",
    "city": "New York",
    "stateIso": "NY",
    "postalCode": "10001",
    "countryIso": "US",
    "phone": "5551234567",
})
print(result.success, result.errors)

# Update, archive, activate
client.locations.update({"id": 16808, "phone": "5559876543"})
client.locations.archive([16808])
client.locations.activate([16808])
```

## Reviews

```python
# List reviews with filters
page = client.reviews.list(16808, first=20, rating_filters=[1, 2])
for review in page:
    print(review.content, review.rating)

# Auto-paginate all reviews
for review in client.reviews.list(16808, first=50).auto_paging_iter():
    print(review.content)

# Respond to a review
client.reviews.respond(interaction_id="uuid-here", content="Thank you!")

# Edit or archive a response
client.reviews.edit_response(review_id="...", response_id="...", content="Updated reply")
client.reviews.archive_response(response_id="...")

# Review analytics
overview = client.reviews.analytics.overview(16808, start_date="2024-01-01")
timeline = client.reviews.analytics.timeline(16808)
sites = client.reviews.analytics.sites_stats(16808)

# Review phrases
phrases = client.reviews.phrases(["TG9jYXRpb246MTY4MDg="], start_date="2024-01-01")
```

## Listings

```python
# Premium, voice, AI, and additional listings
premium = client.listings.premium(16808)
voice = client.listings.voice(16808)
ai = client.listings.ai(16808)
additional = client.listings.additional(16808)

# Duplicates
dupes = client.listings.duplicates(16808)
client.listings.mark_duplicate(16808, ["listing-item-id"])
client.listings.mark_not_duplicate(16808, ["listing-item-id"])

# Connect/disconnect
client.listings.connect(16808, "listing-id", "account-id")
client.listings.disconnect(16808, "GOOGLE")
```

## Analytics

```python
google = client.analytics.google(16808, from_date="2024-01-01")
bing = client.analytics.bing(16808)
facebook = client.analytics.facebook(16808)

# Rankings
timeline = client.analytics.rankings_timeline(
    [16808], "2024-01-01", "2024-03-31", ["Google"]
)
histogram = client.analytics.rankings_histogram(
    [16808], "2024-01-01", "2024-03-31", ["Google"]
)
```

## Keywords

```python
keywords = client.keywords.list(16808)
performance = client.keywords.performance(16808, from_date="2024-01-01")
created = client.keywords.add(16808, ["plumber", "plumbing near me"])
client.keywords.archive("keyword-id")
```

## Campaigns

```python
campaigns = client.campaigns.list(16808)
result = client.campaigns.create(
    16808,
    name="Holiday Feedback",
    customers=[{"name": "John", "email": "john@example.com"}],
    screening=False,
)
client.campaigns.add_customers("campaign-id", [{"name": "Jane", "email": "jane@example.com"}])
```

## Folders

```python
folders = client.folders.list()
tree = client.folders.tree()
client.folders.create("franchise", parent_folder_name="all_franchise")
client.folders.rename("Old Name", "New Name")
client.folders.add_locations("franchise", [16808, 16749])
client.folders.remove_locations([16808])
client.folders.delete("folder-name")
```

## Users

```python
users = client.users.list()
roles = client.users.roles()
result = client.users.create(email="jane@example.com", role_id="...", first_name="Jane")
client.users.update("user-id", first_name="Jane Updated")
client.users.add_locations("user-id", [16808])
client.users.remove_locations("user-id", [16808])
```

## Tags

```python
tags = client.tags.list()
client.tags.add(16808, "vip")
client.tags.remove(16808, "old-tag")
```

## Photos

```python
photos = client.photos.list(16808)
client.photos.add(16808, [{"photo": "https://example.com/img.jpg", "type": "ADDITIONAL"}])
client.photos.remove(16808, ["photo-id"])
client.photos.star(16808, ["media-id"], starred=True)
```

## Connected accounts

```python
accounts = client.connected_accounts.list()
url = client.connected_accounts.connect_google("https://ok.com", "https://err.com")
client.connected_accounts.disconnect_google("account-id")

# OAuth for single location
url = client.connected_accounts.oauth_url(16808, "GOOGLE", "https://ok.com", "https://err.com")
client.connected_accounts.oauth_disconnect(16808, "FACEBOOK")
```

## Grid reports

```python
result = client.grid_reports.create(
    location_id=16808,
    keywords=["italian restaurant"],
    business_name="Chianti",
    business_street="No 12, 5th Block",
    business_city="Bengaluru",
    business_state="Karnataka",
    business_country="India",
    latitude=12.935216,
    longitude=77.619961,
    distance=20,
    distance_unit="km",
    grid_size=3,
)
report = client.grid_reports.retrieve("report-id")
reports = client.grid_reports.list(16808, page_size=20, page=1)
```

## Automations

```python
result = client.automations.temporary_close(
    name="Holiday closure",
    start_date="2025-12-24",
    start_time="18:00:00",
    end_date="2025-12-26",
    location_id=16808,
)
```

## Account-level

```python
sites = client.plan_sites()
countries = client.countries()
subs = client.subscriptions()
```

## Workflows — pre-built automations

High-level functions that combine multiple API calls into real product features.

```python
# Auto-reply to positive reviews
results = client.workflows.auto_reply_to_reviews(
    16808,
    template="Thanks for the {rating}-star review!",
    min_rating=4,
    dry_run=True,  # preview without sending
)

# Onboard a location with folder, tags, and keywords in one call
result = client.workflows.onboard_location(
    name="Acme Coffee",
    street="123 Main St",
    city="New York",
    state="NY",
    postal_code="10001",
    country="US",
    phone="5551234567",
    folder_name="NYC Stores",
    tags=["new", "coffee"],
    keywords=["coffee shop near me"],
)

# Bulk onboard from CSV
results = client.workflows.bulk_onboard_locations("locations.csv", folder_name="Imported")

# Weekly reputation report
report = client.workflows.weekly_reputation_report(16808)
print(report.review_summary, report.analytics, report.listings_health)

# Listings health audit
audit = client.workflows.listings_health_audit(16808)
print(f"Score: {audit.health_score}%, Issues: {audit.issue_count}")
```

## Error handling

```python
import synup

client = synup.Synup()

try:
    client.locations.list()
except synup.AuthenticationError:
    print("Invalid API key")
except synup.RateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except synup.NotFoundError:
    print("Resource not found")
except synup.ValidationError as e:
    print(f"Bad request: {e.response_body}")
except synup.APIError as e:
    print(f"API error {e.status_code}: {e.response_body}")
except synup.APIConnectionError:
    print("Network error — could not reach API")
```

## Version

Current version: 0.4.1
