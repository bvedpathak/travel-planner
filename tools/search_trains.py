"""
Train search tool for the Travel Planner MCP Server.

Provides mock train data that simulates real train booking APIs.
In a production environment, this would integrate with APIs like Amtrak, VIA Rail, or Eurail.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock train routes and operators
TRAIN_ROUTES = {
    ("NYC", "Boston"): {
        "operator": "Amtrak Northeast Regional",
        "distance": "230 miles",
        "base_duration": 240,  # 4 hours in minutes
        "base_price": 120
    },
    ("NYC", "Philadelphia"): {
        "operator": "Amtrak Northeast Regional",
        "distance": "95 miles",
        "base_duration": 90,  # 1.5 hours
        "base_price": 65
    },
    ("NYC", "Washington DC"): {
        "operator": "Amtrak Northeast Regional",
        "distance": "225 miles",
        "base_duration": 180,  # 3 hours
        "base_price": 110
    },
    ("Chicago", "Milwaukee"): {
        "operator": "Amtrak Hiawatha",
        "distance": "85 miles",
        "base_duration": 90,  # 1.5 hours
        "base_price": 45
    },
    ("San Francisco", "Los Angeles"): {
        "operator": "Amtrak Coast Starlight",
        "distance": "470 miles",
        "base_duration": 720,  # 12 hours
        "base_price": 180
    },
    ("Seattle", "Portland"): {
        "operator": "Amtrak Cascades",
        "distance": "173 miles",
        "base_duration": 210,  # 3.5 hours
        "base_price": 85
    },
    ("Austin", "Dallas"): {
        "operator": "Texas Central Railway",
        "distance": "200 miles",
        "base_duration": 180,  # 3 hours
        "base_price": 95
    },
    ("Miami", "Orlando"): {
        "operator": "Brightline",
        "distance": "235 miles",
        "base_duration": 210,  # 3.5 hours
        "base_price": 120
    }
}

# City aliases for flexibility
CITY_ALIASES = {
    "New York": "NYC",
    "New York City": "NYC",
    "San Francisco": "SF",
    "Los Angeles": "LA",
    "Washington": "Washington DC",
    "DC": "Washington DC"
}

TRAIN_CLASSES = [
    {
        "name": "Coach",
        "multiplier": 1.0,
        "amenities": ["Comfortable seating", "WiFi", "Power outlets", "Overhead storage"]
    },
    {
        "name": "Business Class",
        "multiplier": 1.6,
        "amenities": ["Extra legroom", "WiFi", "Power outlets", "Complimentary drinks", "Priority boarding"]
    },
    {
        "name": "First Class",
        "multiplier": 2.4,
        "amenities": ["Premium seating", "WiFi", "Power outlets", "Meal service", "Priority boarding", "Lounge access"]
    }
]

async def search_trains(from_city: str, to_city: str, date: str, passengers: int = 1) -> Dict[str, Any]:
    """
    Search for train routes between two cities.

    Args:
        from_city: Departure city
        to_city: Arrival city
        date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers

    Returns:
        Dictionary containing train search results with metadata
    """

    # Normalize city names
    from_normalized = CITY_ALIASES.get(from_city, from_city)
    to_normalized = CITY_ALIASES.get(to_city, to_city)

    # Check for available routes
    route_key = (from_normalized, to_normalized)
    reverse_route_key = (to_normalized, from_normalized)

    route_info = None
    if route_key in TRAIN_ROUTES:
        route_info = TRAIN_ROUTES[route_key]
        is_reverse = False
    elif reverse_route_key in TRAIN_ROUTES:
        route_info = TRAIN_ROUTES[reverse_route_key]
        is_reverse = True
    else:
        # No direct route available
        available_routes = []
        for (origin, dest) in TRAIN_ROUTES.keys():
            available_routes.append(f"{origin} → {dest}")

        return {
            "error": f"No train routes available between {from_city} and {to_city}",
            "available_routes": available_routes,
            "suggestion": "Consider connecting through a major hub city or alternative transportation"
        }

    # Validate date format
    try:
        travel_date = datetime.strptime(date, "%Y-%m-%d")
        if travel_date < datetime.now():
            return {"error": "Travel date cannot be in the past"}
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    # Generate train schedules
    trains = []
    num_trains = random.randint(3, 8)  # Multiple trains per day

    for i in range(num_trains):
        # Generate departure times throughout the day
        departure_hour = random.randint(6, 20)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"

        # Calculate arrival time
        base_duration = route_info["base_duration"]
        variation = random.randint(-15, 30)  # Add some schedule variation
        actual_duration = base_duration + variation

        departure_dt = datetime.strptime(f"{date} {departure_time}", "%Y-%m-%d %H:%M")
        arrival_dt = departure_dt + timedelta(minutes=actual_duration)
        arrival_time = arrival_dt.strftime("%H:%M")
        arrival_date = arrival_dt.strftime("%Y-%m-%d")

        # Format duration
        hours = actual_duration // 60
        minutes = actual_duration % 60
        duration_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"

        # Generate train number
        train_number = f"{route_info['operator'].split()[0][:2].upper()}{random.randint(100, 999)}"

        # Generate ticket classes and pricing
        classes = []
        for train_class in TRAIN_CLASSES:
            base_price = route_info["base_price"]
            class_price = int(base_price * train_class["multiplier"])
            total_price = class_price * passengers

            # Add peak time surcharge for popular times
            if 7 <= departure_hour <= 9 or 17 <= departure_hour <= 19:
                total_price = int(total_price * 1.15)

            classes.append({
                "className": train_class["name"],
                "pricePerPerson": class_price,
                "totalPrice": total_price,
                "amenities": train_class["amenities"],
                "availability": random.choice(["Available", "Available", "Available", "Limited", "Sold Out"])
            })

        train = {
            "trainNumber": train_number,
            "operator": route_info["operator"],
            "departure": {
                "city": from_city,
                "time": departure_time,
                "date": date,
                "station": f"{from_city} Union Station"
            },
            "arrival": {
                "city": to_city,
                "time": arrival_time,
                "date": arrival_date,
                "station": f"{to_city} Union Station"
            },
            "duration": duration_str,
            "distance": route_info["distance"],
            "passengers": passengers,
            "classes": classes,
            "amenities": [
                "Restrooms", "Snack Car", "WiFi", "Power Outlets",
                "Climate Control", "Large Windows"
            ],
            "policies": {
                "baggage": "2 personal items + 2 carry-on bags free",
                "cancellation": "Full refund up to 24 hours before departure",
                "boarding": "30 minutes before departure",
                "pets": "Small pets allowed in carriers"
            }
        }

        trains.append(train)

    # Sort trains by departure time
    trains.sort(key=lambda x: x["departure"]["time"])

    return {
        "searchCriteria": {
            "from": from_city,
            "to": to_city,
            "date": date,
            "passengers": passengers
        },
        "route": {
            "operator": route_info["operator"],
            "distance": route_info["distance"],
            "averageDuration": f"{route_info['base_duration'] // 60}h {route_info['base_duration'] % 60}m"
        },
        "resultsFound": len(trains),
        "trains": trains,
        "searchTimestamp": datetime.now().isoformat(),
        "note": "This is mock data. In production, this would integrate with real train booking APIs like Amtrak."
    }