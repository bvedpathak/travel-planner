"""
Flight search tool for the Travel Planner MCP Server.

Provides mock flight data that simulates real airline APIs.
In a production environment, this would integrate with actual airline APIs.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock flight data - in production, this would come from airline APIs
AIRLINES = [
    {"code": "UA", "name": "United Airlines"},
    {"code": "AA", "name": "American Airlines"},
    {"code": "DL", "name": "Delta Air Lines"},
    {"code": "SW", "name": "Southwest Airlines"},
    {"code": "B6", "name": "JetBlue Airways"},
    {"code": "AS", "name": "Alaska Airlines"}
]

AIRPORTS = {
    "AUS": {"name": "Austin-Bergstrom International", "city": "Austin", "timezone": "America/Chicago"},
    "SFO": {"name": "San Francisco International", "city": "San Francisco", "timezone": "America/Los_Angeles"},
    "NYC": {"name": "John F. Kennedy International", "city": "New York", "timezone": "America/New_York"},
    "JFK": {"name": "John F. Kennedy International", "city": "New York", "timezone": "America/New_York"},
    "LAX": {"name": "Los Angeles International", "city": "Los Angeles", "timezone": "America/Los_Angeles"},
    "ORD": {"name": "O'Hare International", "city": "Chicago", "timezone": "America/Chicago"},
    "DEN": {"name": "Denver International", "city": "Denver", "timezone": "America/Denver"},
    "MIA": {"name": "Miami International", "city": "Miami", "timezone": "America/New_York"},
    "SEA": {"name": "Seattle-Tacoma International", "city": "Seattle", "timezone": "America/Los_Angeles"},
    "BOS": {"name": "Logan International", "city": "Boston", "timezone": "America/New_York"}
}

async def search_flights(from_city: str, to_city: str, date: str, passengers: int = 1) -> Dict[str, Any]:
    """
    Search for flights between two cities.

    Args:
        from_city: Departure airport code
        to_city: Arrival airport code
        date: Travel date in YYYY-MM-DD format
        passengers: Number of passengers

    Returns:
        Dictionary containing flight search results with metadata
    """

    # Validate airport codes
    if from_city not in AIRPORTS:
        return {
            "error": f"Unknown departure airport code: {from_city}",
            "valid_codes": list(AIRPORTS.keys())
        }

    if to_city not in AIRPORTS:
        return {
            "error": f"Unknown arrival airport code: {to_city}",
            "valid_codes": list(AIRPORTS.keys())
        }

    # Validate date format
    try:
        flight_date = datetime.strptime(date, "%Y-%m-%d")
        if flight_date < datetime.now():
            return {"error": "Flight date cannot be in the past"}
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    # Generate mock flight results
    flights = []
    num_flights = random.randint(3, 8)  # Random number of available flights

    for i in range(num_flights):
        airline = random.choice(AIRLINES)
        flight_number = f"{airline['code']}{random.randint(100, 9999)}"

        # Generate realistic departure times
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"

        # Calculate arrival time (1-6 hours later depending on distance)
        base_duration = random.randint(60, 360)  # 1-6 hours in minutes
        departure_dt = datetime.strptime(f"{date} {departure_time}", "%Y-%m-%d %H:%M")
        arrival_dt = departure_dt + timedelta(minutes=base_duration)
        arrival_time = arrival_dt.strftime("%H:%M")

        # Generate realistic pricing
        base_price = random.randint(150, 800)
        total_price = base_price * passengers

        # Add some variation for different booking classes
        booking_class = random.choice(["Economy", "Premium Economy", "Business"])
        if booking_class == "Premium Economy":
            total_price = int(total_price * 1.3)
        elif booking_class == "Business":
            total_price = int(total_price * 2.2)

        flight = {
            "flightNumber": flight_number,
            "airline": airline["name"],
            "departure": {
                "airport": from_city,
                "airportName": AIRPORTS[from_city]["name"],
                "city": AIRPORTS[from_city]["city"],
                "time": departure_time,
                "date": date
            },
            "arrival": {
                "airport": to_city,
                "airportName": AIRPORTS[to_city]["name"],
                "city": AIRPORTS[to_city]["city"],
                "time": arrival_time,
                "date": date if arrival_dt.date() == departure_dt.date() else arrival_dt.strftime("%Y-%m-%d")
            },
            "duration": f"{base_duration // 60}h {base_duration % 60}m",
            "price": total_price,
            "pricePerPerson": base_price,
            "bookingClass": booking_class,
            "passengers": passengers,
            "stops": random.choice([0, 0, 0, 1]),  # Most flights are direct
            "aircraft": random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A350"])
        }

        flights.append(flight)

    # Sort flights by price
    flights.sort(key=lambda x: x["price"])

    return {
        "searchCriteria": {
            "from": from_city,
            "to": to_city,
            "date": date,
            "passengers": passengers
        },
        "resultsFound": len(flights),
        "flights": flights,
        "searchTimestamp": datetime.now().isoformat(),
        "note": "This is mock data. In production, this would integrate with real airline APIs."
    }