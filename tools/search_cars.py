"""
Car rental search tool for the Travel Planner MCP Server.

Provides mock car rental data that simulates real car rental APIs.
In a production environment, this would integrate with APIs like Hertz, Enterprise, or Budget.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Mock car rental companies and their fleets
CAR_COMPANIES = {
    "Hertz": {
        "economy": ["Nissan Versa", "Chevrolet Spark", "Mitsubishi Mirage"],
        "compact": ["Nissan Sentra", "Toyota Corolla", "Honda Civic"],
        "midsize": ["Toyota Camry", "Honda Accord", "Nissan Altima"],
        "suv": ["Toyota RAV4", "Honda CR-V", "Chevrolet Tahoe"]
    },
    "Enterprise": {
        "economy": ["Chevrolet Spark", "Nissan Versa", "Kia Rio"],
        "compact": ["Honda Civic", "Toyota Corolla", "Nissan Sentra"],
        "midsize": ["Honda Accord", "Toyota Camry", "Chevrolet Malibu"],
        "suv": ["Honda CR-V", "Toyota RAV4", "Ford Explorer"]
    },
    "Budget": {
        "economy": ["Mitsubishi Mirage", "Chevrolet Spark", "Kia Rio"],
        "compact": ["Toyota Corolla", "Nissan Sentra", "Honda Civic"],
        "midsize": ["Toyota Camry", "Honda Accord", "Nissan Altima"],
        "suv": ["Toyota RAV4", "Honda CR-V", "Chevrolet Suburban"]
    },
    "Avis": {
        "economy": ["Nissan Versa", "Kia Rio", "Chevrolet Spark"],
        "compact": ["Honda Civic", "Toyota Corolla", "Nissan Sentra"],
        "midsize": ["Honda Accord", "Toyota Camry", "Chevrolet Malibu"],
        "suv": ["Honda CR-V", "Toyota RAV4", "Ford Expedition"]
    },
    "National": {
        "economy": ["Chevrolet Spark", "Nissan Versa", "Mitsubishi Mirage"],
        "compact": ["Toyota Corolla", "Honda Civic", "Nissan Sentra"],
        "midsize": ["Toyota Camry", "Honda Accord", "Nissan Altima"],
        "suv": ["Toyota RAV4", "Honda CR-V", "Chevrolet Tahoe"]
    }
}

PICKUP_LOCATIONS = {
    "Austin": ["Austin Airport", "Downtown Austin", "South Congress", "The Domain", "East Austin"],
    "San Francisco": ["SFO Airport", "Downtown SF", "Union Square", "Financial District", "Mission District"],
    "New York": ["JFK Airport", "LaGuardia Airport", "Manhattan", "Brooklyn", "Times Square"],
    "Miami": ["Miami Airport", "South Beach", "Downtown Miami", "Coral Gables", "Brickell"],
    "Los Angeles": ["LAX Airport", "Downtown LA", "Hollywood", "Santa Monica", "Beverly Hills"],
    "Chicago": ["O'Hare Airport", "Downtown Chicago", "Lincoln Park", "Millennium Park"],
    "Seattle": ["Seattle Airport", "Downtown Seattle", "Capitol Hill", "Fremont"],
    "Denver": ["Denver Airport", "Downtown Denver", "LoDo", "Cherry Creek"]
}

CAR_FEATURES = [
    "Air Conditioning", "Automatic Transmission", "GPS Navigation", "Bluetooth",
    "USB Charging", "Backup Camera", "Cruise Control", "Power Windows",
    "Power Locks", "AM/FM Radio", "Satellite Radio", "WiFi Hotspot"
]

async def search_cars(city: str, pickup_date: str, days: int, car_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for rental cars in a specified city.

    Args:
        city: City name for car rental pickup
        pickup_date: Pickup date in YYYY-MM-DD format
        days: Number of rental days
        car_type: Preferred car type (optional)

    Returns:
        Dictionary containing car rental search results with metadata
    """

    # Validate city
    if city not in PICKUP_LOCATIONS:
        return {
            "error": f"Car rentals not available in: {city}",
            "available_cities": list(PICKUP_LOCATIONS.keys())
        }

    # Validate pickup date
    try:
        pickup_dt = datetime.strptime(pickup_date, "%Y-%m-%d")
        if pickup_dt < datetime.now():
            return {"error": "Pickup date cannot be in the past"}
        return_dt = pickup_dt + timedelta(days=days)
    except ValueError:
        return {"error": "Invalid pickup date format. Use YYYY-MM-DD"}

    # Validate rental duration
    if days < 1 or days > 60:
        return {"error": "Rental duration must be between 1 and 60 days"}

    # Validate car type if specified
    valid_car_types = ["economy", "compact", "midsize", "suv"]
    if car_type and car_type not in valid_car_types:
        return {
            "error": f"Invalid car type: {car_type}",
            "valid_types": valid_car_types
        }

    # Generate car rental results
    available_cars = []
    companies = list(CAR_COMPANIES.keys())

    # Determine which car types to show
    car_types_to_show = [car_type] if car_type else valid_car_types

    for company in companies:
        for car_category in car_types_to_show:
            # Simulate availability (not all companies have all types available)
            if random.random() > 0.2:  # 80% chance of availability
                available_models = CAR_COMPANIES[company][car_category]
                model = random.choice(available_models)

                # Generate pricing
                base_price = _get_car_base_price(car_category)
                daily_rate = base_price + random.randint(-20, 50)  # Add some variation
                total_cost = daily_rate * days

                # Add fees and taxes
                taxes_fees = int(total_cost * random.uniform(0.15, 0.25))
                final_total = total_cost + taxes_fees

                # Generate pickup location
                pickup_location = random.choice(PICKUP_LOCATIONS[city])

                # Generate features
                car_features = random.sample(CAR_FEATURES, random.randint(6, 10))

                # Generate car specifications
                specs = _get_car_specs(car_category)

                car_rental = {
                    "company": company,
                    "carType": car_category.title(),
                    "model": model,
                    "pickupLocation": pickup_location,
                    "city": city,
                    "pickupDate": pickup_date,
                    "returnDate": return_dt.strftime("%Y-%m-%d"),
                    "rentalDays": days,
                    "pricing": {
                        "dailyRate": daily_rate,
                        "subtotal": total_cost,
                        "taxesAndFees": taxes_fees,
                        "totalCost": final_total
                    },
                    "specifications": specs,
                    "features": car_features,
                    "policies": {
                        "minimumAge": 21 if car_category in ["economy", "compact"] else 25,
                        "mileage": "Unlimited mileage",
                        "fuelPolicy": "Full to Full",
                        "cancellation": "Free cancellation up to 24 hours before pickup"
                    },
                    "pickupTime": "9:00 AM - 6:00 PM",
                    "contact": f"1-800-{company.upper()[:3]}-RENT"
                }

                available_cars.append(car_rental)

    # Sort by total cost
    available_cars.sort(key=lambda x: x["pricing"]["totalCost"])

    return {
        "searchCriteria": {
            "city": city,
            "pickupDate": pickup_date,
            "returnDate": return_dt.strftime("%Y-%m-%d"),
            "days": days,
            "carType": car_type or "any"
        },
        "resultsFound": len(available_cars),
        "cars": available_cars,
        "searchTimestamp": datetime.now().isoformat(),
        "note": "This is mock data. In production, this would integrate with real car rental APIs."
    }

def _get_car_base_price(car_type: str) -> int:
    """Generate realistic base prices based on car category."""
    price_ranges = {
        "economy": (25, 45),
        "compact": (35, 55),
        "midsize": (45, 75),
        "suv": (65, 120)
    }

    min_price, max_price = price_ranges.get(car_type, (40, 70))
    return random.randint(min_price, max_price)

def _get_car_specs(car_type: str) -> Dict[str, Any]:
    """Generate car specifications based on category."""
    specs = {
        "economy": {
            "passengers": "4-5",
            "luggage": "2 bags",
            "doors": "4",
            "transmission": "Automatic",
            "fuelType": "Gasoline",
            "mpg": f"{random.randint(28, 35)}-{random.randint(36, 42)}"
        },
        "compact": {
            "passengers": "5",
            "luggage": "2-3 bags",
            "doors": "4",
            "transmission": "Automatic",
            "fuelType": "Gasoline",
            "mpg": f"{random.randint(26, 32)}-{random.randint(33, 38)}"
        },
        "midsize": {
            "passengers": "5",
            "luggage": "3-4 bags",
            "doors": "4",
            "transmission": "Automatic",
            "fuelType": "Gasoline",
            "mpg": f"{random.randint(22, 28)}-{random.randint(29, 35)}"
        },
        "suv": {
            "passengers": "7-8",
            "luggage": "4-6 bags",
            "doors": "4",
            "transmission": "Automatic",
            "fuelType": "Gasoline",
            "mpg": f"{random.randint(18, 24)}-{random.randint(25, 30)}"
        }
    }

    return specs.get(car_type, specs["compact"])