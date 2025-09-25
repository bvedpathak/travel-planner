"""
Hotel search service implementation following SOLID principles.

This module provides a complete hotel search service that depends on abstractions
rather than concrete implementations, following Dependency Inversion Principle.
"""

from datetime import datetime
from typing import Dict, Any, List
from core.interfaces import (
    ISearchService, IConfigurationLoader, IGeocoder, IApiClient,
    IDataFormatter, IValidator, SearchResult, HotelSearchCriteria
)


class HotelSearchService(ISearchService):
    """
    Hotel search service following Single Responsibility Principle.

    This class is responsible only for orchestrating hotel search operations,
    delegating specific responsibilities to injected dependencies.
    """

    def __init__(
        self,
        config_loader: IConfigurationLoader,
        geocoder: IGeocoder,
        api_client: IApiClient,
        formatter: IDataFormatter,
        validator: IValidator
    ):
        """Initialize service with dependencies (Dependency Inversion Principle)."""
        self.config_loader = config_loader
        self.geocoder = geocoder
        self.api_client = api_client
        self.formatter = formatter
        self.validator = validator

    async def search(self, criteria: HotelSearchCriteria) -> SearchResult:
        """
        Perform hotel search based on criteria.

        This method orchestrates the search process by:
        1. Validating input data
        2. Getting coordinates for location
        3. Loading API configuration
        4. Making API request
        5. Formatting response data
        """
        try:
            # Step 1: Validate input data
            is_valid, validation_error = self.validator.validate(criteria.__dict__)
            if not is_valid:
                return SearchResult(
                    success=False,
                    data={},
                    error=validation_error,
                    timestamp=datetime.now().isoformat()
                )

            # Step 2: Get coordinates for location
            try:
                latitude, longitude = await self.geocoder.get_coordinates(criteria.location)
            except Exception as e:
                return SearchResult(
                    success=False,
                    data={},
                    error=f"Failed to get coordinates for location '{criteria.location}': {str(e)}",
                    timestamp=datetime.now().isoformat()
                )

            # Step 3: Load API configuration
            try:
                config = self.config_loader.load_config()
                api_config = config['hotel_api']['rapidapi']
            except Exception as e:
                return SearchResult(
                    success=False,
                    data={},
                    error=f"Failed to load API configuration: {str(e)}",
                    timestamp=datetime.now().isoformat()
                )

            # Step 4: Prepare API request
            params = {
                "latitude": str(latitude),
                "longitude": str(longitude),
                "arrival_date": criteria.arrival_date,
                "departure_date": criteria.departure_date,
                "adults": str(criteria.adults),
                "room_qty": str(criteria.room_qty),
                "units": "metric",
                "page_number": "1",
                "temperature_unit": "c",
                "languagecode": criteria.languagecode,
                "currency_code": criteria.currency_code,
                "location": "US"
            }

            if criteria.children_age:
                params["children_age"] = criteria.children_age

            headers = {
                "X-RapidAPI-Host": api_config['host'],
                "X-RapidAPI-Key": api_config['key']
            }

            # Step 5: Make API request
            url = f"{api_config['base_url']}/searchHotelsByCoordinates"
            api_response = await self.api_client.make_request(url, params, headers)

            # Step 6: Process API response
            if not api_response.get("status"):
                error_message = api_response.get("message", "Unknown API error")
                return SearchResult(
                    success=False,
                    data={},
                    error=f"API Error: {error_message}",
                    timestamp=datetime.now().isoformat()
                )

            # Step 7: Extract and format hotel data
            hotels_data = api_response.get("data", {})
            hotels_list = hotels_data.get("result", [])

            if not hotels_list:
                return SearchResult(
                    success=True,
                    data={
                        "searchCriteria": self._build_search_criteria_response(criteria, latitude, longitude),
                        "resultsFound": 0,
                        "hotels": [],
                        "message": "No hotels found for the specified criteria"
                    },
                    timestamp=datetime.now().isoformat(),
                    source="Booking.com RapidAPI"
                )

            # Step 8: Format hotel results
            formatted_hotels = []
            for hotel_data in hotels_list[:20]:  # Limit to first 20 results
                formatted_hotel = self.formatter.format_response(hotel_data)
                if not formatted_hotel.get("error"):  # Only include successfully formatted hotels
                    formatted_hotels.append(formatted_hotel)

            # Step 9: Build final response
            nights = self._calculate_nights(criteria.arrival_date, criteria.departure_date)

            return SearchResult(
                success=True,
                data={
                    "searchCriteria": self._build_search_criteria_response(criteria, latitude, longitude, nights),
                    "resultsFound": len(hotels_list),
                    "resultsDisplayed": len(formatted_hotels),
                    "summary": self._build_summary(formatted_hotels, criteria.currency_code),
                    "hotels": formatted_hotels
                },
                timestamp=datetime.now().isoformat(),
                source="Booking.com RapidAPI"
            )

        except Exception as e:
            return SearchResult(
                success=False,
                data={},
                error=f"Hotel search failed: {str(e)}",
                timestamp=datetime.now().isoformat()
            )

    def _build_search_criteria_response(
        self,
        criteria: HotelSearchCriteria,
        latitude: float,
        longitude: float,
        nights: int = None
    ) -> Dict[str, Any]:
        """Build search criteria response."""
        response = {
            "location": criteria.location,
            "coordinates": f"{latitude}, {longitude}",
            "arrival_date": criteria.arrival_date,
            "departure_date": criteria.departure_date,
            "adults": criteria.adults,
            "room_qty": criteria.room_qty,
            "currency_code": criteria.currency_code
        }

        if nights is not None:
            response["nights"] = nights

        return response

    def _calculate_nights(self, arrival_date: str, departure_date: str) -> int:
        """Calculate number of nights between dates."""
        try:
            arrival_dt = datetime.strptime(arrival_date, "%Y-%m-%d")
            departure_dt = datetime.strptime(departure_date, "%Y-%m-%d")
            return (departure_dt - arrival_dt).days
        except:
            return 0

    def _build_summary(self, hotels: List[Dict[str, Any]], currency_code: str) -> Dict[str, Any]:
        """Build summary statistics for hotel results."""
        if not hotels:
            return {
                "totalHotels": 0,
                "hotelsDisplayed": 0,
                "averagePricePerNight": 0,
                "priceRangePerNight": "N/A",
                "averageRating": 0,
                "hotelClasses": []
            }

        # Calculate price statistics
        prices = [h["pricing"]["pricePerNight"] for h in hotels if h["pricing"]["pricePerNight"] > 0]
        ratings = [h["rating"] for h in hotels if h["rating"] > 0]
        classes = list(set(h["hotelClass"] for h in hotels if h["hotelClass"] > 0))

        return {
            "totalHotels": len(hotels),
            "hotelsDisplayed": len(hotels),
            "averagePricePerNight": round(sum(prices) / len(prices), 2) if prices else 0,
            "priceRangePerNight": f"{min(prices):.2f} - {max(prices):.2f} {currency_code}" if prices else "N/A",
            "averageRating": round(sum(ratings) / len(ratings), 1) if ratings else 0,
            "hotelClasses": sorted(classes)
        }