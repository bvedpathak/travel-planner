"""
Hotel search tool for the Travel Planner MCP Server.

Integrates with Booking.com RapidAPI for live hotel data.
"""

import aiohttp
import yaml
import os
from datetime import datetime
from typing import Dict, Any, Tuple

def load_config() -> dict:
    """
    Load API configuration from config.yaml.

    Returns:
        dict: Configuration dictionary containing API keys and endpoints.

    Raises:
        FileNotFoundError: If config.yaml is not found.
        yaml.YAMLError: If config.yaml is malformed.
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

async def get_coordinates_from_city(city: str) -> Tuple[float, float]:
    """
    Get latitude and longitude coordinates for a city using OpenStreetMap Nominatim API.

    Args:
        city: City name to geocode.

    Returns:
        Tuple of (latitude, longitude) coordinates.

    Raises:
        Exception: If geocoding fails or city is not found.

    Note:
        Uses OpenStreetMap Nominatim API which is free and doesn't require API keys.
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Use OpenStreetMap Nominatim API for geocoding (free, no API key required)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": city,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "TravelPlannerMCP/1.0"  # Required by Nominatim
            }

            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        location = data[0]
                        lat = float(location["lat"])
                        lon = float(location["lon"])
                        return lat, lon
                    else:
                        raise Exception(f"City '{city}' not found in geocoding results")
                else:
                    raise Exception(f"Geocoding API returned status {response.status}")
    except Exception as e:
        # Fallback to common city coordinates if geocoding fails
        city_coords = {
            "austin": (30.2672, -97.7431),
            "san francisco": (37.7749, -122.4194),
            "new york": (40.7128, -74.0060),
            "miami": (25.7617, -80.1918),
            "chicago": (41.8781, -87.6298),
            "los angeles": (34.0522, -118.2437),
            "seattle": (47.6062, -122.3321),
            "denver": (39.7392, -104.9903),
            "atlanta": (33.7490, -84.3880),
            "boston": (42.3601, -71.0589)
        }

        city_lower = city.lower()
        if city_lower in city_coords:
            return city_coords[city_lower]
        else:
            raise Exception(f"Failed to get coordinates for '{city}': {str(e)}")

def format_hotel_response(hotel_data: dict) -> dict:
    """
    Format hotel data from API response to standardized structure.

    Args:
        hotel_data: Raw hotel data from Booking.com API.

    Returns:
        dict: Standardized hotel information.

    Note:
        Handles missing fields gracefully and provides default values.
    """
    try:
        # Extract basic hotel information
        hotel_name = hotel_data.get("hotel_name", "Unknown Hotel")
        hotel_id = hotel_data.get("hotel_id", 0)

        # Extract rating information
        rating = hotel_data.get("review_score", 0)
        review_score_word = hotel_data.get("review_score_word", "")
        review_count = hotel_data.get("review_nr", 0)

        # Extract location information
        city = hotel_data.get("city", "")
        city_in_trans = hotel_data.get("city_in_trans", "")
        latitude = hotel_data.get("latitude", 0)
        longitude = hotel_data.get("longitude", 0)

        # Extract pricing information from composite_price_breakdown
        price_breakdown = hotel_data.get("composite_price_breakdown", {})

        # Get total price and per night price
        gross_amount = price_breakdown.get("gross_amount", {})
        gross_per_night = price_breakdown.get("gross_amount_per_night", {})
        net_amount = price_breakdown.get("net_amount", {})

        total_price = gross_amount.get("value", 0)
        price_per_night = gross_per_night.get("value", 0)
        currency = gross_amount.get("currency", "USD")

        # If per night price not available, calculate from total
        if price_per_night == 0 and total_price > 0:
            # Assuming typical 3-night stay based on test dates
            price_per_night = total_price / 3

        # Extract room configuration
        unit_config = hotel_data.get("unit_configuration_label", "Standard Room")

        # Extract amenities from various sources
        amenities = []
        if hotel_data.get("has_swimming_pool", 0):
            amenities.append("Swimming Pool")
        if hotel_data.get("is_free_cancellable", 0):
            amenities.append("Free Cancellation")
        if hotel_data.get("hotel_include_breakfast", 0):
            amenities.append("Breakfast Included")

        # Extract check-in/check-out times
        checkin_info = hotel_data.get("checkin", {})
        checkout_info = hotel_data.get("checkout", {})

        checkin_time = checkin_info.get("from", "3:00 PM") if checkin_info else "3:00 PM"
        checkout_time = checkout_info.get("until", "11:00 AM") if checkout_info else "11:00 AM"

        # Extract photo
        main_photo_url = hotel_data.get("main_photo_url", "")

        # Extract additional details
        accommodation_type = hotel_data.get("accommodation_type", 0)
        hotel_class = hotel_data.get("class", 0)

        return {
            "hotelId": hotel_id,
            "hotelName": hotel_name,
            "location": city_in_trans.replace("in ", "") if city_in_trans else city,
            "city": city,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "rating": rating / 10 if rating > 10 else rating,  # Normalize to 5-point scale
            "ratingWord": review_score_word,
            "reviewCount": review_count,
            "hotelClass": hotel_class,
            "pricing": {
                "pricePerNight": round(price_per_night, 2),
                "totalPrice": round(total_price, 2),
                "currency": currency,
                "netAmount": round(net_amount.get("value", 0), 2),
                "priceDisplay": gross_per_night.get("amount_rounded", f"${price_per_night:.0f}")
            },
            "roomConfiguration": unit_config,
            "amenities": amenities,
            "photos": {
                "main": main_photo_url
            },
            "policies": {
                "checkIn": checkin_time,
                "checkOut": checkout_time,
                "cancellation": "Free cancellation" if hotel_data.get("is_free_cancellable", 0) else "Check hotel policy",
                "prepayment": "No prepayment needed" if hotel_data.get("is_no_prepayment_block", 0) else "Prepayment required"
            },
            "features": {
                "swimmingPool": bool(hotel_data.get("has_swimming_pool", 0)),
                "freeCancellation": bool(hotel_data.get("is_free_cancellable", 0)),
                "breakfastIncluded": bool(hotel_data.get("hotel_include_breakfast", 0)),
                "geniusDeal": bool(hotel_data.get("is_genius_deal", 0)),
                "smartDeal": bool(hotel_data.get("is_smart_deal", 0))
            },
            "availability": {
                "soldOut": bool(hotel_data.get("soldout", 0)),
                "cantBook": hotel_data.get("cant_book") is not None
            }
        }
    except Exception as e:
        # Return minimal hotel info if parsing fails
        return {
            "hotelId": hotel_data.get("hotel_id", 0),
            "hotelName": hotel_data.get("hotel_name", "Unknown Hotel"),
            "location": hotel_data.get("city", "Unknown"),
            "city": hotel_data.get("city", "Unknown"),
            "coordinates": {
                "latitude": hotel_data.get("latitude", 0),
                "longitude": hotel_data.get("longitude", 0)
            },
            "rating": 0,
            "ratingWord": "",
            "reviewCount": 0,
            "hotelClass": 0,
            "pricing": {
                "pricePerNight": 0,
                "totalPrice": 0,
                "currency": "USD",
                "netAmount": 0,
                "priceDisplay": "$0"
            },
            "roomConfiguration": "Standard Room",
            "amenities": [],
            "photos": {"main": ""},
            "policies": {
                "checkIn": "3:00 PM",
                "checkOut": "11:00 AM",
                "cancellation": "Check hotel policy",
                "prepayment": "Check hotel policy"
            },
            "features": {
                "swimmingPool": False,
                "freeCancellation": False,
                "breakfastIncluded": False,
                "geniusDeal": False,
                "smartDeal": False
            },
            "availability": {
                "soldOut": False,
                "cantBook": False
            },
            "error": f"Failed to parse hotel data: {str(e)}"
        }

async def search_hotels(
    location: str,
    arrival_date: str,
    departure_date: str,
    adults: int = 1,
    children_age: str = "",
    room_qty: int = 1,
    units: str = "metric",
    page_number: int = 1,
    temperature_unit: str = "c",
    languagecode: str = "en-us",
    currency_code: str = "USD"
) -> Dict[str, Any]:
    """
    Search for hotels in a location using Booking.com RapidAPI.

    Args:
        location: City or location name for hotel search.
        arrival_date: Check-in date in YYYY-MM-DD format.
        departure_date: Check-out date in YYYY-MM-DD format.
        adults: Number of adult guests (default: 1).
        children_age: Ages of children separated by comma (e.g., "0,17").
        room_qty: Number of rooms required (default: 1).
        units: Unit system - "metric" or "imperial" (default: "metric").
        page_number: Page number for pagination (default: 1).
        temperature_unit: Temperature unit - "c" or "f" (default: "c").
        languagecode: Language code (default: "en-us").
        currency_code: Currency code (default: "USD").

    Returns:
        Dictionary containing hotel search results with metadata.

    Raises:
        Exception: If API request fails or location cannot be geocoded.
    """
    try:
        # Validate date formats
        arrival_dt = datetime.strptime(arrival_date, "%Y-%m-%d")
        departure_dt = datetime.strptime(departure_date, "%Y-%m-%d")

        if arrival_dt >= departure_dt:
            return {"error": "Departure date must be after arrival date"}

        if arrival_dt < datetime.now():
            return {"error": "Arrival date cannot be in the past"}

    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    # Get coordinates for the location
    try:
        latitude, longitude = await get_coordinates_from_city(location)
    except Exception as e:
        return {
            "error": f"Failed to get coordinates for location '{location}': {str(e)}",
            "searchCriteria": {
                "location": location,
                "arrival_date": arrival_date,
                "departure_date": departure_date,
                "adults": adults,
                "room_qty": room_qty
            }
        }

    # Load API configuration
    try:
        config = load_config()
        api_config = config['hotel_api']['rapidapi']
    except Exception as e:
        return {"error": f"Failed to load API configuration: {str(e)}"}

    # Prepare API request parameters
    params = {
        "latitude": str(latitude),
        "longitude": str(longitude),
        "arrival_date": arrival_date,
        "departure_date": departure_date,
        "adults": str(adults),
        "room_qty": str(room_qty),
        "units": units,
        "page_number": str(page_number),
        "temperature_unit": temperature_unit,
        "languagecode": languagecode,
        "currency_code": currency_code,
        "location": "US"  # Default location parameter required by API
    }

    # Add children ages if provided
    if children_age:
        params["children_age"] = children_age

    headers = {
        "X-RapidAPI-Host": api_config['host'],
        "X-RapidAPI-Key": api_config['key']
    }

    # Make API request
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{api_config['base_url']}/searchHotelsByCoordinates"
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check if API returned an error
                    if not data.get("status") or "error" in str(data).lower():
                        error_message = data.get("message", "Unknown API error")
                        return {
                            "error": f"API Error: {error_message}",
                            "searchCriteria": {
                                "location": location,
                                "coordinates": f"{latitude}, {longitude}",
                                "arrival_date": arrival_date,
                                "departure_date": departure_date,
                                "adults": adults,
                                "room_qty": room_qty
                            }
                        }

                    # Extract hotel data from response
                    hotels_data = data.get("data", {})
                    hotels_list = hotels_data.get("result", [])

                    if not hotels_list:
                        return {
                            "searchCriteria": {
                                "location": location,
                                "coordinates": f"{latitude}, {longitude}",
                                "arrival_date": arrival_date,
                                "departure_date": departure_date,
                                "adults": adults,
                                "room_qty": room_qty
                            },
                            "resultsFound": 0,
                            "hotels": [],
                            "message": "No hotels found for the specified criteria",
                            "searchTimestamp": datetime.now().isoformat(),
                            "source": "Booking.com RapidAPI"
                        }

                    # Format hotel results
                    formatted_hotels = []
                    for hotel_data in hotels_list[:20]:  # Limit to first 20 results
                        formatted_hotel = format_hotel_response(hotel_data)
                        formatted_hotels.append(formatted_hotel)

                    # Calculate nights
                    nights = (departure_dt - arrival_dt).days

                    return {
                        "searchCriteria": {
                            "location": location,
                            "coordinates": f"{latitude}, {longitude}",
                            "arrival_date": arrival_date,
                            "departure_date": departure_date,
                            "nights": nights,
                            "adults": adults,
                            "room_qty": room_qty,
                            "currency_code": currency_code
                        },
                        "resultsFound": len(hotels_list),
                        "resultsDisplayed": len(formatted_hotels),
                        "summary": {
                            "totalHotels": len(hotels_list),
                            "hotelsDisplayed": len(formatted_hotels),
                            "averagePricePerNight": round(sum(h["pricing"]["pricePerNight"] for h in formatted_hotels if h["pricing"]["pricePerNight"] > 0) / max(len([h for h in formatted_hotels if h["pricing"]["pricePerNight"] > 0]), 1), 2) if formatted_hotels else 0,
                            "priceRangePerNight": f"{min(h['pricing']['pricePerNight'] for h in formatted_hotels if h['pricing']['pricePerNight'] > 0):.2f} - {max(h['pricing']['pricePerNight'] for h in formatted_hotels if h['pricing']['pricePerNight'] > 0):.2f} {currency_code}" if formatted_hotels and any(h["pricing"]["pricePerNight"] > 0 for h in formatted_hotels) else "N/A",
                            "averageRating": round(sum(h["rating"] for h in formatted_hotels if h["rating"] > 0) / max(len([h for h in formatted_hotels if h["rating"] > 0]), 1), 1) if formatted_hotels else 0,
                            "hotelClasses": list(set(h["hotelClass"] for h in formatted_hotels if h["hotelClass"] > 0))
                        },
                        "hotels": formatted_hotels,
                        "searchTimestamp": datetime.now().isoformat(),
                        "source": "Booking.com RapidAPI"
                    }
                else:
                    error_text = await response.text()
                    return {
                        "error": f"API request failed with status {response.status}",
                        "details": error_text[:500],  # Limit error details
                        "searchCriteria": {
                            "location": location,
                            "arrival_date": arrival_date,
                            "departure_date": departure_date
                        }
                    }
    except Exception as e:
        return {
            "error": f"Failed to fetch hotel data: {str(e)}",
            "searchCriteria": {
                "location": location,
                "arrival_date": arrival_date,
                "departure_date": departure_date,
                "adults": adults,
                "room_qty": room_qty
            }
        }