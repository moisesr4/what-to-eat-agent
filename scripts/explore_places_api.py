"""
One-shot script: make a single Google Places Nearby Search call and print
the raw JSON of the first result. Run this before writing any processing
logic to understand the real API response structure.

Usage:
    python scripts/explore_places_api.py

Requires GOOGLE_PLACES_API_KEY in .env
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
if not API_KEY:
    sys.exit("ERROR: GOOGLE_PLACES_API_KEY is not set in .env")

ENDPOINT = "https://places.googleapis.com/v1/places:searchNearby"

# Paris 14e — one location, small radius, one result
payload = {
    "includedTypes": ["restaurant"],
    "maxResultCount": 1,
    "locationRestriction": {
        "circle": {
            "center": {"latitude": 48.8330, "longitude": 2.3322},
            "radius": 500.0,
        }
    },
}

# Request all useful fields to understand the full response structure
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": (
        "places.id,"
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.rating,"
        "places.userRatingCount,"
        "places.priceLevel,"
        "places.types,"
        "places.primaryType,"
        "places.businessStatus,"
        "places.currentOpeningHours,"
        "places.regularOpeningHours,"
        "places.nationalPhoneNumber,"
        "places.internationalPhoneNumber,"
        "places.websiteUri,"
        "places.googleMapsUri,"
        "places.photos,"
        "places.editorialSummary,"
        "places.takeout,"
        "places.delivery,"
        "places.dineIn,"
        "places.reservable,"
        "places.servesLunch,"
        "places.servesDinner,"
        "places.servesBeer,"
        "places.servesWine,"
        "places.servesCocktails,"
        "places.servesCoffee,"
        "places.servesDessert,"
        "places.servesBrunch,"
        "places.servesBreakfast,"
        "places.allowsDogs,"
        "places.goodForChildren,"
        "places.goodForGroups,"
        "places.outdoorSeating,"
        "places.liveMusic,"
        "places.menuForChildren,"
        "places.accessibilityOptions,"
        "places.parkingOptions,"
        "places.paymentOptions"
    ),
}

print(f"Calling: {ENDPOINT}")
print(f"Location: 48.8330, 2.3322 (Paris 14e) | radius: 500m | maxResults: 1\n")

response = requests.post(ENDPOINT, json=payload, headers=headers)

if response.status_code != 200:
    print(f"HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

data = response.json()
places = data.get("places", [])

if not places:
    print("No results returned.")
    sys.exit(0)

print("=== RAW RESPONSE — first result ===\n")
print(json.dumps(places[0], indent=2, ensure_ascii=False))
print("\n=== Top-level keys in this result ===")
print(list(places[0].keys()))
