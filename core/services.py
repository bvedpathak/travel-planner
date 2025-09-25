"""
Concrete implementations of core services following SOLID principles.

This module provides implementations of the interfaces defined in core.interfaces,
following Single Responsibility Principle and Dependency Inversion Principle.
"""

import os
import yaml
import aiohttp
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from core.interfaces import (
    IConfigurationLoader, IGeocoder, IApiClient, IDataFormatter,
    IParameterMapper, IValidator
)


class YamlConfigurationLoader(IConfigurationLoader):
    """Concrete implementation for loading YAML configuration."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'config.yaml'
        )

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {str(e)}")


class NominatimGeocoder(IGeocoder):
    """Geocoding service using OpenStreetMap Nominatim API."""

    def __init__(self, api_client: IApiClient):
        self.api_client = api_client
        self.fallback_coordinates = {
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

    async def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get coordinates for a location using Nominatim API with fallback."""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": location,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "TravelPlannerMCP/1.0"
            }

            response = await self.api_client.make_request(url, params, headers)

            if response and len(response) > 0:
                location_data = response[0]
                lat = float(location_data["lat"])
                lon = float(location_data["lon"])
                return lat, lon
            else:
                return self._get_fallback_coordinates(location)

        except Exception:
            return self._get_fallback_coordinates(location)

    def _get_fallback_coordinates(self, location: str) -> Tuple[float, float]:
        """Get fallback coordinates for common cities."""
        location_lower = location.lower()
        if location_lower in self.fallback_coordinates:
            return self.fallback_coordinates[location_lower]
        else:
            raise ValueError(f"Unable to get coordinates for location: {location}")


class HttpApiClient(IApiClient):
    """HTTP API client implementation."""

    async def make_request(self, url: str, params: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        """Make an HTTP GET request."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")


class HotelResponseFormatter(IDataFormatter):
    """Formatter for hotel API responses."""

    def format_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format hotel data from API response to standardized structure."""
        try:
            # Extract basic hotel information
            hotel_name = raw_data.get("hotel_name", "Unknown Hotel")
            hotel_id = raw_data.get("hotel_id", 0)

            # Extract rating information
            rating = raw_data.get("review_score", 0)
            review_score_word = raw_data.get("review_score_word", "")
            review_count = raw_data.get("review_nr", 0)

            # Extract location information
            city = raw_data.get("city", "")
            city_in_trans = raw_data.get("city_in_trans", "")
            latitude = raw_data.get("latitude", 0)
            longitude = raw_data.get("longitude", 0)

            # Extract pricing information
            price_breakdown = raw_data.get("composite_price_breakdown", {})
            gross_amount = price_breakdown.get("gross_amount", {})
            gross_per_night = price_breakdown.get("gross_amount_per_night", {})
            net_amount = price_breakdown.get("net_amount", {})

            total_price = gross_amount.get("value", 0)
            price_per_night = gross_per_night.get("value", 0)
            currency = gross_amount.get("currency", "USD")

            # If per night price not available, calculate from total
            if price_per_night == 0 and total_price > 0:
                price_per_night = total_price / 3  # Assuming 3-night stay

            return {
                "hotelId": hotel_id,
                "hotelName": hotel_name,
                "location": city_in_trans.replace("in ", "") if city_in_trans else city,
                "city": city,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "rating": rating / 10 if rating > 10 else rating,
                "ratingWord": review_score_word,
                "reviewCount": review_count,
                "hotelClass": raw_data.get("class", 0),
                "pricing": {
                    "pricePerNight": round(price_per_night, 2),
                    "totalPrice": round(total_price, 2),
                    "currency": currency,
                    "netAmount": round(net_amount.get("value", 0), 2),
                    "priceDisplay": gross_per_night.get("amount_rounded", f"${price_per_night:.0f}")
                },
                "roomConfiguration": raw_data.get("unit_configuration_label", "Standard Room"),
                "amenities": self._extract_amenities(raw_data),
                "photos": {
                    "main": raw_data.get("main_photo_url", "")
                },
                "policies": self._extract_policies(raw_data),
                "features": self._extract_features(raw_data),
                "availability": {
                    "soldOut": bool(raw_data.get("soldout", 0)),
                    "cantBook": raw_data.get("cant_book") is not None
                }
            }
        except Exception as e:
            return {
                "hotelId": raw_data.get("hotel_id", 0),
                "hotelName": raw_data.get("hotel_name", "Unknown Hotel"),
                "error": f"Failed to format hotel data: {str(e)}"
            }

    def _extract_amenities(self, raw_data: Dict[str, Any]) -> list:
        """Extract amenities from raw hotel data."""
        amenities = []
        if raw_data.get("has_swimming_pool", 0):
            amenities.append("Swimming Pool")
        if raw_data.get("is_free_cancellable", 0):
            amenities.append("Free Cancellation")
        if raw_data.get("hotel_include_breakfast", 0):
            amenities.append("Breakfast Included")
        return amenities

    def _extract_policies(self, raw_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract policies from raw hotel data."""
        checkin_info = raw_data.get("checkin", {})
        checkout_info = raw_data.get("checkout", {})

        return {
            "checkIn": checkin_info.get("from", "3:00 PM") if checkin_info else "3:00 PM",
            "checkOut": checkout_info.get("until", "11:00 AM") if checkout_info else "11:00 AM",
            "cancellation": "Free cancellation" if raw_data.get("is_free_cancellable", 0) else "Check hotel policy",
            "prepayment": "No prepayment needed" if raw_data.get("is_no_prepayment_block", 0) else "Prepayment required"
        }

    def _extract_features(self, raw_data: Dict[str, Any]) -> Dict[str, bool]:
        """Extract features from raw hotel data."""
        return {
            "swimmingPool": bool(raw_data.get("has_swimming_pool", 0)),
            "freeCancellation": bool(raw_data.get("is_free_cancellable", 0)),
            "breakfastIncluded": bool(raw_data.get("hotel_include_breakfast", 0)),
            "geniusDeal": bool(raw_data.get("is_genius_deal", 0)),
            "smartDeal": bool(raw_data.get("is_smart_deal", 0))
        }


class HotelParameterMapper(IParameterMapper):
    """Parameter mapper for hotel search with backward compatibility."""

    def map_parameters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Map parameters supporting both old and new formats."""
        # Handle both old and new parameter formats
        location = arguments.get("location") or arguments.get("city")
        arrival_date = arguments.get("arrival_date") or arguments.get("checkIn")
        departure_date = arguments.get("departure_date")

        # If using old format with nights, calculate departure_date
        if not departure_date and arguments.get("nights") and arrival_date:
            from datetime import datetime, timedelta
            arrival_dt = datetime.strptime(arrival_date, "%Y-%m-%d")
            departure_dt = arrival_dt + timedelta(days=int(arguments["nights"]))
            departure_date = departure_dt.strftime("%Y-%m-%d")

        adults = arguments.get("adults") or arguments.get("guests", 1)

        return {
            "location": location,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
            "adults": adults,
            "children_age": arguments.get("children_age", ""),
            "room_qty": arguments.get("room_qty", 1),
            "currency_code": arguments.get("currency_code", "USD"),
            "languagecode": arguments.get("languagecode", "en-us")
        }


class DateValidator(IValidator):
    """Validator for date-related data."""

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate date parameters."""
        try:
            arrival_date = data.get("arrival_date")
            departure_date = data.get("departure_date")

            if not arrival_date or not departure_date:
                return False, "Missing required dates"

            # Validate date formats
            arrival_dt = datetime.strptime(arrival_date, "%Y-%m-%d")
            departure_dt = datetime.strptime(departure_date, "%Y-%m-%d")

            if arrival_dt >= departure_dt:
                return False, "Departure date must be after arrival date"

            if arrival_dt < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                return False, "Arrival date cannot be in the past"

            return True, None

        except ValueError as e:
            return False, f"Invalid date format: {str(e)}"
        except Exception as e:
            return False, f"Date validation error: {str(e)}"