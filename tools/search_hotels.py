"""
Hotel search tool for the Travel Planner MCP Server.

Provides mock hotel data that simulates real hotel booking APIs.
In a production environment, this would integrate with APIs like Booking.com or Expedia.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock hotel data organized by city
HOTELS_BY_CITY = {
    "Austin": [
        {"name": "Austin Downtown Suites", "category": "luxury", "rating": 4.5},
        {"name": "South by Southwest Hotel", "category": "boutique", "rating": 4.3},
        {"name": "Lady Bird Lake Resort", "category": "resort", "rating": 4.7},
        {"name": "Capitol View Inn", "category": "business", "rating": 4.2},
        {"name": "Austin Budget Lodge", "category": "budget", "rating": 3.8},
        {"name": "Music City Motel", "category": "budget", "rating": 3.5},
        {"name": "Hill Country Retreat", "category": "resort", "rating": 4.6},
        {"name": "Domain Luxury Suites", "category": "luxury", "rating": 4.8}
    ],
    "San Francisco": [
        {"name": "Golden Gate Grand Hotel", "category": "luxury", "rating": 4.9},
        {"name": "Fisherman's Wharf Inn", "category": "boutique", "rating": 4.4},
        {"name": "Silicon Valley Business Hotel", "category": "business", "rating": 4.3},
        {"name": "Bay Area Budget Inn", "category": "budget", "rating": 3.7},
        {"name": "Nob Hill Luxury Suites", "category": "luxury", "rating": 4.8},
        {"name": "Mission District Boutique", "category": "boutique", "rating": 4.5},
        {"name": "Airport Express Inn", "category": "budget", "rating": 3.6}
    ],
    "New York": [
        {"name": "Manhattan Luxury Tower", "category": "luxury", "rating": 4.9},
        {"name": "Times Square Boutique", "category": "boutique", "rating": 4.4},
        {"name": "Central Park View Hotel", "category": "luxury", "rating": 4.8},
        {"name": "Brooklyn Bridge Inn", "category": "boutique", "rating": 4.3},
        {"name": "Midtown Business Hotel", "category": "business", "rating": 4.2},
        {"name": "East Village Budget Stay", "category": "budget", "rating": 3.9},
        {"name": "Upper East Side Suites", "category": "luxury", "rating": 4.7}
    ],
    "Miami": [
        {"name": "South Beach Luxury Resort", "category": "resort", "rating": 4.8},
        {"name": "Art Deco Boutique Hotel", "category": "boutique", "rating": 4.5},
        {"name": "Biscayne Bay Business Center", "category": "business", "rating": 4.2},
        {"name": "Miami Beach Budget Inn", "category": "budget", "rating": 3.8},
        {"name": "Ocean Drive Grand Hotel", "category": "luxury", "rating": 4.9}
    ]
}

AMENITIES = [
    "Free WiFi", "Swimming Pool", "Fitness Center", "Restaurant", "Room Service",
    "Parking", "Pet Friendly", "Business Center", "Spa", "Concierge Service",
    "Airport Shuttle", "Laundry Service", "24/7 Front Desk", "Bar/Lounge"
]

LOCATIONS = {
    "Austin": ["Downtown", "South Congress", "East Austin", "The Domain", "Airport Area", "Lake Travis"],
    "San Francisco": ["Union Square", "Fisherman's Wharf", "Mission District", "Nob Hill", "SOMA", "Airport Area"],
    "New York": ["Manhattan", "Brooklyn", "Times Square", "Central Park", "Financial District", "Upper East Side"],
    "Miami": ["South Beach", "Downtown", "Coral Gables", "Brickell", "Airport Area", "Key Biscayne"]
}

async def search_hotels(city: str, check_in: str, nights: int, guests: int = 2) -> Dict[str, Any]:
    """
    Search for hotels in a specified city.

    Args:
        city: City name for hotel search
        check_in: Check-in date in YYYY-MM-DD format
        nights: Number of nights to stay
        guests: Number of guests

    Returns:
        Dictionary containing hotel search results with metadata
    """

    # Validate city
    if city not in HOTELS_BY_CITY:
        return {
            "error": f"No hotels available for city: {city}",
            "available_cities": list(HOTELS_BY_CITY.keys())
        }

    # Validate check-in date
    try:
        checkin_date = datetime.strptime(check_in, "%Y-%m-%d")
        if checkin_date < datetime.now():
            return {"error": "Check-in date cannot be in the past"}
        checkout_date = checkin_date + timedelta(days=nights)
    except ValueError:
        return {"error": "Invalid check-in date format. Use YYYY-MM-DD"}

    # Validate nights
    if nights < 1 or nights > 30:
        return {"error": "Number of nights must be between 1 and 30"}

    # Generate hotel results by simulating availability
    city_hotels = HOTELS_BY_CITY[city].copy()
    available_hotels = []

    # Simulate some hotels being unavailable (realistic booking scenario)
    # Ensure at least 3 hotels are available, but not all
    num_available = random.randint(max(3, len(city_hotels) - 3), len(city_hotels))
    available_city_hotels = random.sample(city_hotels, num_available)

    for hotel_data in available_city_hotels:
        # Generate room types and pricing based on hotel category
        room_types = []

        # Standard room - available at all hotels
        base_price = _get_base_price(hotel_data["category"])
        room_types.append({
            "type": "Standard Room",
            "pricePerNight": base_price,
            "totalPrice": base_price * nights,
            "bedsDescription": "1 Queen Bed" if guests <= 2 else "2 Queen Beds",
            "maxOccupancy": 2 if guests <= 2 else 4,
            "roomSize": "300 sq ft"
        })

        # Deluxe room - only available at luxury and resort properties
        if hotel_data["category"] in ["luxury", "resort"]:
            deluxe_price = int(base_price * 1.4)
            room_types.append({
                "type": "Deluxe Room",
                "pricePerNight": deluxe_price,
                "totalPrice": deluxe_price * nights,
                "bedsDescription": "1 King Bed",
                "maxOccupancy": 3,
                "roomSize": "400 sq ft"
            })

        # Executive suite - exclusive to luxury hotels
        if hotel_data["category"] == "luxury":
            suite_price = int(base_price * 2.2)
            room_types.append({
                "type": "Executive Suite",
                "pricePerNight": suite_price,
                "totalPrice": suite_price * nights,
                "bedsDescription": "1 King Bed + Sofa Bed",
                "maxOccupancy": 4,
                "roomSize": "650 sq ft"
            })

        # Generate amenities
        hotel_amenities = random.sample(AMENITIES, random.randint(4, 8))

        # Generate location
        location = random.choice(LOCATIONS[city])

        hotel = {
            "hotelName": hotel_data["name"],
            "location": location,
            "city": city,
            "rating": hotel_data["rating"],
            "category": hotel_data["category"].title(),
            "checkIn": check_in,
            "checkOut": checkout_date.strftime("%Y-%m-%d"),
            "nights": nights,
            "guests": guests,
            "roomTypes": room_types,
            "amenities": hotel_amenities,
            "distance": {
                "downtown": f"{random.uniform(0.1, 15.0):.1f} miles",
                "airport": f"{random.uniform(5.0, 25.0):.1f} miles"
            },
            "policies": {
                "checkInTime": "3:00 PM",
                "checkOutTime": "11:00 AM",
                "cancellation": "Free cancellation until 24 hours before check-in",
                "petPolicy": "Pet friendly" if "Pet Friendly" in hotel_amenities else "No pets allowed"
            }
        }

        available_hotels.append(hotel)

    # Sort hotels by lowest price room
    available_hotels.sort(key=lambda x: min(room["pricePerNight"] for room in x["roomTypes"]))

    return {
        "searchCriteria": {
            "city": city,
            "checkIn": check_in,
            "checkOut": checkout_date.strftime("%Y-%m-%d"),
            "nights": nights,
            "guests": guests
        },
        "resultsFound": len(available_hotels),
        "hotels": available_hotels,
        "searchTimestamp": datetime.now().isoformat(),
        "note": "This is mock data. In production, this would integrate with real hotel booking APIs."
    }

def _get_base_price(category: str) -> int:
    """
    Generate realistic base prices based on hotel category.

    Args:
        category: Hotel category (budget, business, boutique, luxury, resort).

    Returns:
        int: Random base price within the category's price range.

    Note:
        Prices are per night in USD and represent typical market rates.
    """
    price_ranges = {
        "budget": (50, 100),
        "business": (120, 200),
        "boutique": (150, 250),
        "luxury": (250, 500),
        "resort": (200, 400)
    }

    min_price, max_price = price_ranges.get(category, (100, 200))
    return random.randint(min_price, max_price)