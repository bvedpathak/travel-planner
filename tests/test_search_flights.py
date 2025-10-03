"""
Unit tests for flight search functionality.
"""

import pytest
from unittest.mock import patch, AsyncMock
from tools.search_flights import search_flights


class TestFlightSearch:
    """Test cases for flight search functionality."""

    @pytest.mark.asyncio
    async def test_search_flights_basic(self, sample_flight_params):
        """Test basic flight search functionality."""
        result = await search_flights(**sample_flight_params)

        # Verify response structure
        assert "searchCriteria" in result
        assert "resultsFound" in result
        assert "flights" in result

        # Verify search criteria
        criteria = result["searchCriteria"]
        assert criteria["from_id"] == "AUS"
        assert criteria["to_id"] == "SFO"
        assert criteria["adults"] == 2

        # Verify flights data
        assert isinstance(result["flights"], list)
        assert result["resultsFound"] == len(result["flights"])
        assert result["resultsFound"] > 0

    @pytest.mark.asyncio
    async def test_search_flights_single_passenger(self):
        """Test flight search with single passenger."""
        result = await search_flights(
            from_id="NYC",
            to_id="LAX",
            depart_date="2025-10-01",
            adults=1
        )

        criteria = result["searchCriteria"]
        assert criteria["adults"] == 1

        # Verify all flights have correct passenger count
        for flight in result["flights"]:
            assert flight["adults"] == 1

    @pytest.mark.asyncio
    async def test_search_flights_multiple_passengers(self):
        """Test flight search with multiple passengers."""
        result = await search_flights("LAX", "NYC", "2025-10-01", 5)

        criteria = result["searchCriteria"]
        assert criteria["passengers"] == 5

        # Verify pricing scales with passengers
        for flight in result["flights"]:
            assert flight["passengers"] == 5
            assert flight["price"] == flight["pricePerPerson"] * 5

    @pytest.mark.asyncio
    async def test_search_flights_different_routes(self):
        """Test flight search for different city pairs."""
        routes = [
            ("AUS", "NYC"),
            ("SFO", "CHI"),
            ("MIA", "SEA"),
            ("DEN", "BOS")
        ]

        for from_city, to_city in routes:
            result = await search_flights(from_city, to_city, "2025-10-01", 1)

            assert result["searchCriteria"]["from"] == from_city
            assert result["searchCriteria"]["to"] == to_city
            assert len(result["flights"]) > 0

    @pytest.mark.asyncio
    async def test_search_flights_response_schema(self, sample_flight_params):
        """Test that flight response matches expected schema."""
        result = await search_flights(**sample_flight_params)

        # Test top-level structure
        required_keys = ["searchCriteria", "resultsFound", "flights"]
        for key in required_keys:
            assert key in result

        # Test search criteria structure
        criteria = result["searchCriteria"]
        criteria_keys = ["from", "to", "date", "passengers"]
        for key in criteria_keys:
            assert key in criteria

        # Test flight structure
        if result["flights"]:
            flight = result["flights"][0]
            flight_keys = [
                "flightNumber", "airline", "departure", "arrival",
                "duration", "price", "pricePerPerson", "bookingClass",
                "passengers", "stops", "aircraft"
            ]
            for key in flight_keys:
                assert key in flight

            # Test departure/arrival structure
            for location in [flight["departure"], flight["arrival"]]:
                location_keys = ["airport", "airportName", "city", "time", "date"]
                for key in location_keys:
                    assert key in location

    @pytest.mark.asyncio
    async def test_search_flights_data_types(self, sample_flight_params):
        """Test that flight response data types are correct."""
        result = await search_flights(**sample_flight_params)

        # Test top-level types
        assert isinstance(result["resultsFound"], int)
        assert isinstance(result["flights"], list)

        # Test criteria types
        criteria = result["searchCriteria"]
        assert isinstance(criteria["from"], str)
        assert isinstance(criteria["to"], str)
        assert isinstance(criteria["date"], str)
        assert isinstance(criteria["passengers"], int)

        # Test flight data types
        if result["flights"]:
            flight = result["flights"][0]
            assert isinstance(flight["flightNumber"], str)
            assert isinstance(flight["airline"], str)
            assert isinstance(flight["duration"], str)
            assert isinstance(flight["price"], (int, float))
            assert isinstance(flight["pricePerPerson"], (int, float))
            assert isinstance(flight["passengers"], int)
            assert isinstance(flight["stops"], int)

    @pytest.mark.asyncio
    async def test_search_flights_price_consistency(self, sample_flight_params):
        """Test that flight pricing is mathematically consistent."""
        result = await search_flights(**sample_flight_params)

        for flight in result["flights"]:
            expected_total = flight["pricePerPerson"] * flight["passengers"]
            assert flight["price"] == expected_total, (
                f"Price inconsistency: {flight['price']} != "
                f"{flight['pricePerPerson']} * {flight['passengers']}"
            )

    @pytest.mark.asyncio
    async def test_search_flights_realistic_data(self, sample_flight_params):
        """Test that flight data contains realistic values."""
        result = await search_flights(**sample_flight_params)

        for flight in result["flights"]:
            # Price should be reasonable (between $50 and $2000 per person)
            assert 50 <= flight["pricePerPerson"] <= 2000

            # Stops should be reasonable (0-2)
            assert 0 <= flight["stops"] <= 2

            # Duration should be reasonable format
            assert "h" in flight["duration"]

            # Flight number should contain letters and numbers
            assert any(c.isalpha() for c in flight["flightNumber"])
            assert any(c.isdigit() for c in flight["flightNumber"])

    @pytest.mark.asyncio
    async def test_search_flights_date_consistency(self, sample_flight_params):
        """Test that departure and arrival dates are consistent."""
        result = await search_flights(**sample_flight_params)

        search_date = sample_flight_params["date"]

        for flight in result["flights"]:
            # Departure date should match search date
            assert flight["departure"]["date"] == search_date

            # Arrival date should be same day or next day for domestic flights
            arrival_date = flight["arrival"]["date"]
            assert arrival_date in [search_date, search_date]  # Simplified check

    @pytest.mark.asyncio
    async def test_search_flights_empty_parameters(self):
        """Test flight search with edge case parameters."""
        # Test with minimal valid parameters
        result = await search_flights("", "", "2025-10-01", 1)

        # Should still return some structure even with empty cities
        assert "searchCriteria" in result
        assert "flights" in result

    @pytest.mark.asyncio
    async def test_search_flights_large_passenger_count(self):
        """Test flight search with large passenger count."""
        result = await search_flights("AUS", "SFO", "2025-10-01", 10)

        criteria = result["searchCriteria"]
        assert criteria["passengers"] == 10

        # Should handle large groups
        for flight in result["flights"]:
            assert flight["passengers"] == 10
            assert flight["price"] > 0

    @pytest.mark.asyncio
    async def test_search_flights_weekend_vs_weekday(self):
        """Test flight search for different days of week."""
        # Test weekend (Saturday)
        weekend_result = await search_flights("AUS", "SFO", "2025-10-04", 1)

        # Test weekday (Tuesday)
        weekday_result = await search_flights("AUS", "SFO", "2025-10-07", 1)

        # Both should return valid results
        assert len(weekend_result["flights"]) > 0
        assert len(weekday_result["flights"]) > 0

        # Dates should match requests
        assert weekend_result["searchCriteria"]["date"] == "2025-10-04"
        assert weekday_result["searchCriteria"]["date"] == "2025-10-07"