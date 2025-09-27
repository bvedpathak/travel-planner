"""
Flight search tool for the Travel Planner MCP Server.

Integrates with Booking.com RapidAPI for live flight data.
"""

import os
from datetime import datetime
from typing import Any, Dict

import aiohttp
import yaml


def load_config() -> dict:
    """
    Load API configuration from config.yaml.

    Returns:
        dict: Configuration dictionary containing API keys and endpoints.

    Raises:
        FileNotFoundError: If config.yaml is not found.
        yaml.YAMLError: If config.yaml is malformed.
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def format_price(price_obj: dict) -> str:
    """
    Format price object from API response to a readable string.

    Args:
        price_obj: Price object containing currency, units, and nanos fields.

    Returns:
        str: Formatted price string like "USD 123.45" or "N/A" if invalid.

    Note:
        Nanos field represents billionths of the currency unit.
    """
    if not price_obj:
        return "N/A"

    currency = price_obj.get("currencyCode", "USD")
    units = price_obj.get("units", 0)
    nanos = price_obj.get("nanos", 0)

    # Convert nanos to decimal (nanos are billionths)
    total = units + (nanos / 1_000_000_000)
    return f"{currency} {total:.2f}"


def format_duration(total_seconds: int) -> str:
    """
    Convert seconds to a human-readable hours and minutes format.

    Args:
        total_seconds: Total duration in seconds.

    Returns:
        str: Formatted duration string like "4h 30m" or "N/A" if invalid.
    """
    if not total_seconds:
        return "N/A"

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def parse_flight_offer(offer: dict) -> dict | None:
    """
    Parse a complex flight offer from the API response into a simplified format.

    Args:
        offer: Raw flight offer object from Booking.com API.

    Returns:
        dict: Simplified flight offer with standardized structure, or None if parsing fails.

    Note:
        Handles both one-way and round-trip flights. Errors are logged but don't fail the entire request.
    """
    try:
        segments = offer.get("segments", [])
        if not segments:
            return None

        # Get price information
        price_breakdown = offer.get("priceBreakdown", {})
        total_price = price_breakdown.get("total", {})

        # Parse segments (outbound and return for round trips)
        parsed_segments = []
        for segment in segments:
            legs = segment.get("legs", [])
            if not legs:
                continue

            # For now, take the first leg (direct flights or first leg of connection)
            leg = legs[0]

            segment_data = {
                "departure": {
                    "airport": leg["departureAirport"]["code"],
                    "airportName": leg["departureAirport"]["name"],
                    "city": leg["departureAirport"]["cityName"],
                    "time": leg["departureTime"].split("T")[1][:5],  # Extract time from ISO format
                    "date": leg["departureTime"].split("T")[0],  # Extract date
                },
                "arrival": {
                    "airport": leg["arrivalAirport"]["code"],
                    "airportName": leg["arrivalAirport"]["name"],
                    "city": leg["arrivalAirport"]["cityName"],
                    "time": leg["arrivalTime"].split("T")[1][:5],
                    "date": leg["arrivalTime"].split("T")[0],
                },
                "duration": format_duration(leg.get("totalTime")),
                "flightNumber": f"{leg['flightInfo']['carrierInfo']['marketingCarrier']}{leg['flightInfo']['flightNumber']}",
                "airline": leg["carriersData"][0]["name"] if leg.get("carriersData") else "Unknown",
                "stops": len(leg.get("flightStops", [])),
                "cabinClass": leg.get("cabinClass", "ECONOMY"),
            }
            parsed_segments.append(segment_data)

        return {
            "segments": parsed_segments,
            "totalPrice": format_price(total_price),
            "priceBreakdown": {
                "baseFare": format_price(price_breakdown.get("baseFare")),
                "taxes": format_price(price_breakdown.get("tax")),
                "total": format_price(total_price),
            },
            "tripType": offer.get("tripType", "UNKNOWN"),
            "bookingToken": offer.get("token"),
            "isRoundTrip": len(segments) > 1,
        }

    except Exception as e:
        # Log error but don't fail the entire request
        print(f"Error parsing flight offer: {e}")
        return None


async def search_flights(
    from_id: str,
    to_id: str,
    depart_date: str,
    return_date: str = None,
    adults: int = 1,
    children: int = 0,
    stops: str = "none",
    cabin_class: str = "ECONOMY",
    currency_code: str = "USD",
) -> Dict[str, Any]:
    """
    Search for flights between two cities using Booking.com RapidAPI.

    Args:
        from_id: Departure airport code (e.g., BOM.AIRPORT)
        to_id: Arrival airport code (e.g., DEL.AIRPORT)
        depart_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional for round trip)
        adults: Number of adult passengers (default: 1)
        children: Number of child passengers (default: 0)
        stops: Number of stops - "none", "one", "any" (default: "none")
        cabin_class: Cabin class - "ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST" (default: "ECONOMY")
        currency_code: Currency code (default: "USD")

    Returns:
        Dictionary containing flight search results with metadata
    """

    try:
        # Validate date format
        datetime.strptime(depart_date, "%Y-%m-%d")
        if return_date:
            datetime.strptime(return_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}

    # Load API configuration
    try:
        config = load_config()
        api_config = config["flight_api"]["rapidapi"]
    except Exception as e:
        return {"error": f"Failed to load API configuration: {str(e)}"}

    # Prepare API request parameters
    params = {
        "fromId": from_id,
        "toId": to_id,
        "departDate": depart_date,
        "pageNo": "1",
        "adults": str(adults),
        "children": f"{children}%2C17",
        "sort": "BEST",
        "cabinClass": cabin_class,
        "currency_code": currency_code,
        "stops": stops,
    }

    if return_date:
        params["returnDate"] = return_date

    headers = {"X-RapidAPI-Host": api_config["host"], "X-RapidAPI-Key": api_config["key"]}

    # Make API request
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{api_config['base_url']}/searchFlights"
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check if API returned an error
                    if not data.get("status") or "error" in data.get("data", {}):
                        error_info = data.get("data", {}).get("error", {})
                        return {
                            "error": f"API Error: {error_info.get('code', 'Unknown error')}",
                            "requestId": error_info.get("requestId"),
                            "searchCriteria": {
                                "from": from_id,
                                "to": to_id,
                                "departDate": depart_date,
                                "returnDate": return_date,
                                "adults": adults,
                                "children": children,
                                "cabinClass": cabin_class,
                                "stops": stops,
                            },
                        }

                    # Transform successful response to user-friendly format
                    flight_offers = data.get("data", {}).get("flightOffers", [])
                    aggregation = data.get("data", {}).get("aggregation", {})

                    # Convert flight offers to simplified format
                    flights = []
                    for offer in flight_offers[:10]:  # Limit to first 10 results
                        flight = parse_flight_offer(offer)
                        if flight:
                            flights.append(flight)

                    return {
                        "searchCriteria": {
                            "from": from_id,
                            "to": to_id,
                            "departDate": depart_date,
                            "returnDate": return_date,
                            "adults": adults,
                            "children": children,
                            "cabinClass": cabin_class,
                            "stops": stops,
                        },
                        "resultsFound": len(flight_offers),
                        "resultsDisplayed": len(flights),
                        "summary": {
                            "totalFlights": aggregation.get("totalCount", 0),
                            "minPrice": format_price(aggregation.get("minPrice")),
                            "priceRange": f"{format_price(aggregation.get('minPrice'))} - {format_price(aggregation.get('budget', {}).get('max'))}",
                            "airlines": len(aggregation.get("airlines", [])),
                            "directFlights": next(
                                (
                                    stop["count"]
                                    for stop in aggregation.get("stops", [])
                                    if stop.get("numberOfStops") == 0
                                ),
                                0,
                            ),
                        },
                        "flights": flights,
                        "searchTimestamp": datetime.now().isoformat(),
                        "source": "Booking.com RapidAPI",
                    }
                else:
                    error_text = await response.text()
                    return {
                        "error": f"API request failed with status {response.status}",
                        "details": error_text,
                    }
    except Exception as e:
        return {
            "error": f"Failed to fetch flight data: {str(e)}",
            "searchCriteria": {
                "from": from_id,
                "to": to_id,
                "departDate": depart_date,
                "returnDate": return_date,
                "adults": adults,
                "children": children,
            },
        }
