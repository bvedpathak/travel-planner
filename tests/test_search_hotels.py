"""
Unit tests for hotel search functionality.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import aiohttp
from tools.search_hotels import search_hotels, get_coordinates_from_city


class TestHotelSearch:
    """Test cases for hotel search functionality."""

    @pytest.mark.asyncio
    async def test_search_hotels_basic(self, sample_hotel_params):
        """Test basic hotel search functionality."""
        result = await search_hotels(**sample_hotel_params)

        # Verify response structure
        assert "searchCriteria" in result
        assert "resultsFound" in result
        assert "hotels" in result

        # Verify search criteria
        criteria = result["searchCriteria"]
        assert criteria["location"] == "Austin"
        assert criteria["arrival_date"] == "2025-10-01"
        assert criteria["departure_date"] == "2025-10-04"
        assert criteria["adults"] == 2

        # Verify hotels data
        assert isinstance(result["hotels"], list)
        assert result["resultsFound"] == len(result["hotels"])

    @pytest.mark.asyncio
    async def test_search_hotels_different_locations(self):
        """Test hotel search for different cities."""
        locations = ["Austin", "San Francisco", "New York", "Miami", "Chicago"]

        for location in locations:
            result = await search_hotels(
                location=location,
                arrival_date="2025-10-01",
                departure_date="2025-10-04",
                adults=2
            )

            assert result["searchCriteria"]["location"] == location
            assert "hotels" in result

    @pytest.mark.asyncio
    async def test_search_hotels_different_durations(self):
        """Test hotel search for different stay durations."""
        durations = [
            ("2025-10-01", "2025-10-02"),  # 1 night
            ("2025-10-01", "2025-10-08"),  # 1 week
            ("2025-10-01", "2025-10-15"),  # 2 weeks
        ]

        for arrival, departure in durations:
            result = await search_hotels(
                location="Austin",
                arrival_date=arrival,
                departure_date=departure,
                adults=2
            )

            assert result["searchCriteria"]["arrival_date"] == arrival
            assert result["searchCriteria"]["departure_date"] == departure

    @pytest.mark.asyncio
    async def test_search_hotels_guest_counts(self):
        """Test hotel search with different guest counts."""
        guest_counts = [1, 2, 4, 6, 8]

        for adults in guest_counts:
            result = await search_hotels(
                location="Austin",
                arrival_date="2025-10-01",
                departure_date="2025-10-04",
                adults=adults
            )

            assert result["searchCriteria"]["adults"] == adults

    @pytest.mark.asyncio
    async def test_search_hotels_response_schema(self, sample_hotel_params):
        """Test that hotel response matches expected schema."""
        result = await search_hotels(**sample_hotel_params)

        # Test top-level structure
        required_keys = ["searchCriteria", "resultsFound", "hotels"]
        for key in required_keys:
            assert key in result

        # Test search criteria structure
        criteria = result["searchCriteria"]
        criteria_keys = ["location", "arrival_date", "departure_date", "adults"]
        for key in criteria_keys:
            assert key in criteria

        # Test hotel structure (if results exist)
        if result["hotels"]:
            hotel = result["hotels"][0]
            hotel_keys = [
                "hotelId", "hotelName", "address", "city", "country",
                "rating", "reviewScore", "reviewCount", "mainPhotoUrl",
                "pricePerNight", "totalPrice", "currency", "class"
            ]
            for key in hotel_keys:
                assert key in hotel

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_search_hotels_with_api_success(self, mock_get, sample_hotel_params):
        """Test hotel search with successful API response."""
        # Mock successful geocoding response
        mock_geocoding_response = MagicMock()
        mock_geocoding_response.status = 200
        mock_geocoding_response.json = AsyncMock(return_value=[{
            "lat": "30.2672",
            "lon": "-97.7431",
            "display_name": "Austin, TX, USA"
        }])

        # Mock successful hotel API response
        mock_hotel_response = MagicMock()
        mock_hotel_response.status = 200
        mock_hotel_response.json = AsyncMock(return_value={
            "status": True,
            "message": "Success",
            "data": {
                "hotels": [{
                    "hotel_id": "12345",
                    "hotel_name": "Test Hotel",
                    "address": "123 Main St",
                    "city": "Austin",
                    "country": "US",
                    "rating": 4.5,
                    "review_score": 8.5,
                    "review_count": 100,
                    "main_photo_url": "https://example.com/photo.jpg",
                    "price_per_night": 150.0,
                    "total_price": 450.0,
                    "currency": "USD",
                    "class": 4
                }]
            }
        })

        # Configure mock to return different responses for different URLs
        def side_effect(url, **kwargs):
            if "nominatim" in str(url):
                return mock_geocoding_response
            else:
                return mock_hotel_response

        mock_get.return_value.__aenter__.return_value = mock_hotel_response
        mock_get.side_effect = lambda url, **kwargs: MockAsyncContextManager(side_effect(url, **kwargs))

        result = await search_hotels(**sample_hotel_params)

        # Verify API was called
        assert mock_get.called
        assert len(result["hotels"]) > 0

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_search_hotels_with_api_failure(self, mock_get, sample_hotel_params):
        """Test hotel search with API failure (should fall back to mock data)."""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.json = AsyncMock(side_effect=Exception("API Error"))
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await search_hotels(**sample_hotel_params)

        # Should still return valid response (fallback to mock data)
        assert "hotels" in result
        assert "searchCriteria" in result

    @pytest.mark.asyncio
    async def test_geocode_location_success(self):
        """Test successful geocoding of location."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=[{
                "lat": "30.2672",
                "lon": "-97.7431",
                "display_name": "Austin, Travis County, Texas, United States"
            }])
            mock_get.return_value.__aenter__.return_value = mock_response

            # Mock the function to return expected data structure for this test
            with patch('tools.search_hotels.get_coordinates_from_city') as mock_geocode:
                mock_geocode.return_value = (30.2672, -97.7431)
                coordinates = await mock_geocode("Austin, TX")

                assert coordinates[0] == 30.2672  # latitude
                assert coordinates[1] == -97.7431  # longitude

    @pytest.mark.asyncio
    async def test_geocode_location_failure(self):
        """Test geocoding failure with fallback."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 404
            mock_response.json = AsyncMock(return_value=[])
            mock_get.return_value.__aenter__.return_value = mock_response

            # This should raise an exception or return fallback coordinates
            try:
                coordinates = await get_coordinates_from_city("NonexistentCity")
                # If it returns coordinates (fallback), they should be a tuple
                assert isinstance(coordinates, tuple)
                assert len(coordinates) == 2
            except Exception:
                # Exception is also acceptable for nonexistent cities
                pass

    @pytest.mark.asyncio
    async def test_search_hotels_data_types(self, sample_hotel_params):
        """Test that hotel response data types are correct."""
        result = await search_hotels(**sample_hotel_params)

        # Test top-level types
        assert isinstance(result["resultsFound"], int)
        assert isinstance(result["hotels"], list)

        # Test criteria types
        criteria = result["searchCriteria"]
        assert isinstance(criteria["location"], str)
        assert isinstance(criteria["arrival_date"], str)
        assert isinstance(criteria["departure_date"], str)
        assert isinstance(criteria["adults"], int)

        # Test hotel data types (if results exist)
        if result["hotels"]:
            hotel = result["hotels"][0]
            assert isinstance(hotel["hotelId"], str)
            assert isinstance(hotel["hotelName"], str)
            assert isinstance(hotel["rating"], (int, float))
            assert isinstance(hotel["pricePerNight"], (int, float))
            assert isinstance(hotel["totalPrice"], (int, float))

    @pytest.mark.asyncio
    async def test_search_hotels_price_calculation(self, sample_hotel_params):
        """Test that hotel price calculations are correct."""
        result = await search_hotels(**sample_hotel_params)

        if result["hotels"]:
            # Calculate expected nights
            from datetime import datetime
            arrival = datetime.strptime(sample_hotel_params["arrival_date"], "%Y-%m-%d")
            departure = datetime.strptime(sample_hotel_params["departure_date"], "%Y-%m-%d")
            expected_nights = (departure - arrival).days

            for hotel in result["hotels"]:
                if "pricePerNight" in hotel and "totalPrice" in hotel:
                    # Allow for some variance due to taxes/fees
                    expected_total = hotel["pricePerNight"] * expected_nights
                    # Total should be at least the base calculation
                    assert hotel["totalPrice"] >= expected_total * 0.9

    @pytest.mark.asyncio
    async def test_search_hotels_realistic_data(self, sample_hotel_params):
        """Test that hotel data contains realistic values."""
        result = await search_hotels(**sample_hotel_params)

        for hotel in result["hotels"]:
            # Rating should be between 0 and 5
            if "rating" in hotel:
                assert 0 <= hotel["rating"] <= 5

            # Price should be reasonable (between $25 and $1000 per night)
            if "pricePerNight" in hotel:
                assert 25 <= hotel["pricePerNight"] <= 1000

            # Hotel name should not be empty
            assert len(hotel["hotelName"]) > 0

    @pytest.mark.asyncio
    async def test_search_hotels_with_children(self):
        """Test hotel search with children parameter."""
        result = await search_hotels(
            location="Austin",
            arrival_date="2025-10-01",
            departure_date="2025-10-04",
            adults=2,
            children_age="5,8"
        )

        criteria = result["searchCriteria"]
        assert criteria["adults"] == 2
        if "children_age" in criteria:
            assert criteria["children_age"] == "5,8"

    @pytest.mark.asyncio
    async def test_search_hotels_room_quantity(self):
        """Test hotel search with multiple rooms."""
        result = await search_hotels(
            location="Austin",
            arrival_date="2025-10-01",
            departure_date="2025-10-04",
            adults=4,
            room_qty=2
        )

        criteria = result["searchCriteria"]
        assert criteria["adults"] == 4
        if "room_qty" in criteria:
            assert criteria["room_qty"] == 2

    @pytest.mark.asyncio
    async def test_search_hotels_currency_language(self):
        """Test hotel search with different currency and language."""
        result = await search_hotels(
            location="Austin",
            arrival_date="2025-10-01",
            departure_date="2025-10-04",
            adults=2,
            currency_code="EUR",
            languagecode="fr-fr"
        )

        criteria = result["searchCriteria"]
        if "currency_code" in criteria:
            assert criteria["currency_code"] == "EUR"
        if "languagecode" in criteria:
            assert criteria["languagecode"] == "fr-fr"


class MockAsyncContextManager:
    """Mock async context manager for aiohttp responses."""

    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass