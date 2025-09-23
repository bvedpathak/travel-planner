"""
Car rental search tool for the Travel Planner MCP Server.

Integrates with Booking.com RapidAPI for live car rental data.
"""

import aiohttp
import yaml
import os
from datetime import datetime
from typing import Dict, Any, Optional

def load_config():
    """Load API configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def format_price(price_obj):
    """Format price object to readable string"""
    if not price_obj:
        return "N/A"

    if isinstance(price_obj, dict):
        currency = price_obj.get("currencyCode", "USD")
        units = price_obj.get("units", 0)
        nanos = price_obj.get("nanos", 0)
        total = units + (nanos / 1_000_000_000)
        return f"{currency} {total:.2f}"
    elif isinstance(price_obj, (int, float)):
        return f"USD {price_obj:.2f}"
    else:
        return str(price_obj)

def parse_car_rental(rental):
    """Parse a car rental from the API response into simplified format"""
    try:
        # Based on the actual API response structure from rentalcars provider
        # The structure includes: vendor, vehicle, pricing, etc.

        # Extract basic information
        vendor = rental.get("vendor", {})
        vehicle = rental.get("vehicle", {})
        pricing = rental.get("pricing", {})
        location_info = rental.get("location", {})

        # Extract vehicle details
        vehicle_info = vehicle.get("vehicle_info", {})

        return {
            "company": vendor.get("name", "Unknown"),
            "carType": vehicle_info.get("category", vehicle.get("category", "Unknown")),
            "model": vehicle_info.get("name", vehicle.get("name", "Unknown")),
            "pickupLocation": location_info.get("pickup", {}).get("location", "Unknown"),
            "dropoffLocation": location_info.get("dropoff", {}).get("location", "Unknown"),
            "pickupDate": rental.get("pickup_date"),
            "returnDate": rental.get("dropoff_date"),
            "pricing": {
                "totalCost": format_price(pricing.get("total_price", pricing.get("total"))),
                "dailyRate": format_price(pricing.get("daily_price", pricing.get("daily"))),
                "currency": pricing.get("currency", "USD"),
                "breakdown": {
                    "base": format_price(pricing.get("base_price")),
                    "taxes": format_price(pricing.get("taxes")),
                    "fees": format_price(pricing.get("fees"))
                }
            },
            "specifications": {
                "passengers": vehicle_info.get("passengers", vehicle.get("seats", "N/A")),
                "doors": vehicle_info.get("doors", vehicle.get("doors", "N/A")),
                "transmission": vehicle_info.get("transmission", "N/A"),
                "fuelType": vehicle_info.get("fuel_type", vehicle.get("fuel", "N/A")),
                "airConditioning": vehicle_info.get("air_conditioning", vehicle.get("airConditioning", False)),
                "category": vehicle_info.get("category", "N/A")
            },
            "policies": {
                "mileage": rental.get("mileage_policy", "Check with supplier"),
                "fuelPolicy": rental.get("fuel_policy", "Check with supplier"),
                "cancellation": rental.get("cancellation_policy", "Check with supplier"),
                "minimumAge": rental.get("minimum_age", 21)
            },
            "supplier": vendor,
            "bookingToken": rental.get("booking_token", rental.get("id")),
            "features": rental.get("features", []),
            "insurance": rental.get("insurance", {}),
            "rating": vendor.get("rating", "N/A")
        }
    except Exception as e:
        print(f"Error parsing car rental: {e}")
        return None

async def search_cars(
    pick_up_latitude: float,
    pick_up_longitude: float,
    drop_off_latitude: float,
    drop_off_longitude: float,
    pick_up_date: str,
    drop_off_date: str,
    pick_up_time: str = "10:00",
    drop_off_time: str = "10:00",
    driver_age: int = 30,
    currency_code: str = "USD",
    location: str = "US"
) -> Dict[str, Any]:
    """
    Search for rental cars using Booking.com RapidAPI.

    Args:
        pick_up_latitude: Latitude for pickup location
        pick_up_longitude: Longitude for pickup location
        drop_off_latitude: Latitude for drop-off location
        drop_off_longitude: Longitude for drop-off location
        pick_up_date: Pickup date in YYYY-MM-DD format
        drop_off_date: Drop-off date in YYYY-MM-DD format
        pick_up_time: Pickup time in HH:MM format (default: 10:00)
        drop_off_time: Drop-off time in HH:MM format (default: 10:00)
        driver_age: Driver age (default: 30)
        currency_code: Currency code (default: USD)
        location: Location code (default: US)

    Returns:
        Dictionary containing car rental search results with metadata
    """

    try:
        # Validate date format
        datetime.strptime(pick_up_date, "%Y-%m-%d")
        datetime.strptime(drop_off_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    # Load API configuration
    try:
        config = load_config()
        api_config = config['car_api']['rapidapi']
    except Exception as e:
        return {"error": f"Failed to load API configuration: {str(e)}"}

    # Prepare API request parameters
    params = {
        "pick_up_latitude": str(pick_up_latitude),
        "pick_up_longitude": str(pick_up_longitude),
        "drop_off_latitude": str(drop_off_latitude),
        "drop_off_longitude": str(drop_off_longitude),
        "pick_up_date": pick_up_date,
        "drop_off_date": drop_off_date,
        "pick_up_time": pick_up_time,
        "drop_off_time": drop_off_time,
        "driver_age": str(driver_age),
        "currency_code": currency_code,
        "location": location
    }

    headers = {
        "X-RapidAPI-Host": api_config['host'],
        "X-RapidAPI-Key": api_config['key']
    }

    # Make API request
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{api_config['base_url']}/searchCarRentals"
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check if API returned success status
                    if not data.get("status"):
                        return {
                            "error": f"API Error: {data.get('message', 'Unknown error')}",
                            "searchCriteria": {
                                "pickupLocation": f"Lat: {pick_up_latitude}, Lng: {pick_up_longitude}",
                                "dropoffLocation": f"Lat: {drop_off_latitude}, Lng: {drop_off_longitude}",
                                "pickupDate": pick_up_date,
                                "dropoffDate": drop_off_date,
                                "driverAge": driver_age,
                                "currency": currency_code
                            }
                        }

                    # Transform successful response to user-friendly format
                    data_section = data.get("data", {})
                    car_rentals = data_section.get("search_results", [])
                    count = data_section.get("count", 0)
                    provider = data_section.get("provider", "Unknown")

                    # Convert car rentals to simplified format
                    cars = []
                    for rental in car_rentals[:15]:  # Limit to first 15 results
                        car = parse_car_rental(rental)
                        if car:
                            cars.append(car)

                    # Handle case where there are no search results
                    if count == 0 and len(cars) == 0:
                        return {
                            "searchCriteria": {
                                "pickupLocation": f"Lat: {pick_up_latitude}, Lng: {pick_up_longitude}",
                                "dropoffLocation": f"Lat: {drop_off_latitude}, Lng: {drop_off_longitude}",
                                "pickupDate": pick_up_date,
                                "dropoffDate": drop_off_date,
                                "pickupTime": pick_up_time,
                                "dropoffTime": drop_off_time,
                                "driverAge": driver_age,
                                "currency": currency_code,
                                "location": location
                            },
                            "resultsFound": 0,
                            "resultsDisplayed": 0,
                            "cars": [],
                            "message": "No car rentals available for the specified criteria",
                            "provider": provider,
                            "searchTimestamp": datetime.now().isoformat(),
                            "source": "Booking.com RapidAPI"
                        }

                    return {
                        "searchCriteria": {
                            "pickupLocation": f"Lat: {pick_up_latitude}, Lng: {pick_up_longitude}",
                            "dropoffLocation": f"Lat: {drop_off_latitude}, Lng: {drop_off_longitude}",
                            "pickupDate": pick_up_date,
                            "dropoffDate": drop_off_date,
                            "pickupTime": pick_up_time,
                            "dropoffTime": drop_off_time,
                            "driverAge": driver_age,
                            "currency": currency_code,
                            "location": location
                        },
                        "resultsFound": count,
                        "resultsDisplayed": len(cars),
                        "cars": cars,
                        "provider": provider,
                        "availableFilters": data_section.get("filter", []),
                        "sortOptions": data_section.get("sort", []),
                        "searchTimestamp": datetime.now().isoformat(),
                        "source": "Booking.com RapidAPI"
                    }
                else:
                    error_text = await response.text()
                    return {
                        "error": f"API request failed with status {response.status}",
                        "details": error_text
                    }
    except Exception as e:
        return {
            "error": f"Failed to fetch car rental data: {str(e)}",
            "searchCriteria": {
                "pickupLocation": f"Lat: {pick_up_latitude}, Lng: {pick_up_longitude}",
                "dropoffLocation": f"Lat: {drop_off_latitude}, Lng: {drop_off_longitude}",
                "pickupDate": pick_up_date,
                "dropoffDate": drop_off_date
            }
        }

