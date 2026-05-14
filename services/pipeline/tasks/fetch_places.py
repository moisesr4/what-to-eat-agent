"""
Fetch restaurants from the Google Places API (v1) for a given location.
Returns a list of flattened dicts ready for BigQuery insertion.

Usage (standalone):
    from services.pipeline.tasks.fetch_places import fetch_restaurants
    rows = fetch_restaurants("48.8330,2.3322", "paris_14", radius_m=1000)
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = "https://places.googleapis.com/v1/places:searchNearby"
MAX_RESULTS = 20  # API hard limit per request
MIN_REVIEW_CHARS = 50  # discard one-liners that add no semantic value

FIELD_MASK = (
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
    "places.nationalPhoneNumber,"
    "places.internationalPhoneNumber,"
    "places.websiteUri,"
    "places.googleMapsUri,"
    "places.photos,"
    "places.takeout,"
    "places.delivery,"
    "places.dineIn,"
    "places.reservable,"
    "places.servesBeer,"
    "places.servesWine,"
    "places.servesCocktails,"
    "places.outdoorSeating,"
    "places.liveMusic,"
    "places.goodForChildren,"
    "places.goodForGroups,"
    "places.paymentOptions,"
    "places.parkingOptions,"
    "places.accessibilityOptions,"
    "places.reviews"
)


def _flatten(place: dict, zone: str, fetched_at: str) -> dict:
    location = place.get("location", {})
    display_name = place.get("displayName", {})
    current_hours = place.get("currentOpeningHours", {})
    payment = place.get("paymentOptions", {})
    parking = place.get("parkingOptions", {})
    accessibility = place.get("accessibilityOptions", {})
    photos = place.get("photos", [])

    return {
        "place_id": place.get("id"),
        "name": display_name.get("text"),
        "address": place.get("formattedAddress"),
        "lat": location.get("latitude"),
        "lng": location.get("longitude"),
        "rating": place.get("rating"),
        "user_rating_count": place.get("userRatingCount"),
        "price_level": place.get("priceLevel"),
        "primary_type": place.get("primaryType"),
        "types": json.dumps(place.get("types", []), ensure_ascii=False),
        "business_status": place.get("businessStatus"),
        "phone_national": place.get("nationalPhoneNumber"),
        "phone_international": place.get("internationalPhoneNumber"),
        "website_uri": place.get("websiteUri"),
        "google_maps_uri": place.get("googleMapsUri"),
        "open_now": current_hours.get("openNow"),
        "next_close_time": current_hours.get("nextCloseTime"),
        "weekday_descriptions": json.dumps(
            current_hours.get("weekdayDescriptions", []), ensure_ascii=False
        ),
        "takeout": place.get("takeout"),
        "delivery": place.get("delivery"),
        "dine_in": place.get("dineIn"),
        "reservable": place.get("reservable"),
        "serves_beer": place.get("servesBeer"),
        "serves_wine": place.get("servesWine"),
        "serves_cocktails": place.get("servesCocktails"),
        "outdoor_seating": place.get("outdoorSeating"),
        "live_music": place.get("liveMusic"),
        "good_for_children": place.get("goodForChildren"),
        "good_for_groups": place.get("goodForGroups"),
        "accepts_credit_cards": payment.get("acceptsCreditCards"),
        "accepts_debit_cards": payment.get("acceptsDebitCards"),
        "accepts_cash_only": payment.get("acceptsCashOnly"),
        "accepts_nfc": payment.get("acceptsNfc"),
        "free_parking_lot": parking.get("freeParkingLot"),
        "free_street_parking": parking.get("freeStreetParking"),
        "paid_street_parking": parking.get("paidStreetParking"),
        "valet_parking": parking.get("valetParking"),
        "wheelchair_accessible_entrance": accessibility.get("wheelchairAccessibleEntrance"),
        "wheelchair_accessible_restroom": accessibility.get("wheelchairAccessibleRestroom"),
        "wheelchair_accessible_seating": accessibility.get("wheelchairAccessibleSeating"),
        "photo_count": len(photos),
        "reviews": " ".join(
            r["text"]["text"]
            for r in place.get("reviews", [])
            if len(r.get("text", {}).get("text", "")) >= MIN_REVIEW_CHARS
        ) or None,
        "zone": zone,
        "fetched_at": fetched_at,
    }


def fetch_restaurants(
    lat_lng: str,
    zone: str,
    radius_m: float = 1000.0,
    fetched_at: str | None = None,
) -> list[dict]:
    """
    Call the Places Nearby Search API and return flattened restaurant rows.

    Args:
        lat_lng: "lat,lng" string e.g. "48.8330,2.3322"
        zone: human label for this search area e.g. "paris_14"
        radius_m: search radius in metres (default 1000)
        fetched_at: ISO timestamp string; defaults to UTC now if not provided

    Returns:
        List of flattened dicts matching the raw.restaurants schema.
    """
    from datetime import datetime, timezone

    if fetched_at is None:
        fetched_at = datetime.now(timezone.utc).isoformat()

    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY is not set")

    lat, lng = (float(x.strip()) for x in lat_lng.split(","))

    payload = {
        "includedTypes": ["restaurant"],
        "maxResultCount": MAX_RESULTS,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius_m,
            }
        },
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }

    response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=15)
    response.raise_for_status()

    places = response.json().get("places", [])
    return [_flatten(p, zone, fetched_at) for p in places]
