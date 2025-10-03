"""
Simple unit tests to verify the test framework is working.
"""

import pytest
import asyncio


class TestBasicFunctionality:
    """Basic tests to verify test framework."""

    def test_basic_assertion(self):
        """Test that basic assertions work."""
        assert 1 + 1 == 2
        assert "hello" == "hello"
        assert [1, 2, 3] == [1, 2, 3]

    def test_imports_work(self):
        """Test that we can import the main modules."""
        from tools.search_flights import search_flights
        from tools.search_hotels import search_hotels
        from tools.search_cars import search_cars
        from tools.search_trains import search_trains
        from tools.generate_itinerary import generate_itinerary

        # Just verify they're callable
        assert callable(search_flights)
        assert callable(search_hotels)
        assert callable(search_cars)
        assert callable(search_trains)
        assert callable(generate_itinerary)

    @pytest.mark.asyncio
    async def test_flight_search_basic(self):
        """Test basic flight search functionality."""
        from tools.search_flights import search_flights

        result = await search_flights(
            from_id="AUS",
            to_id="SFO",
            depart_date="2025-10-01"
        )

        # Basic structure checks
        assert isinstance(result, dict)
        assert "searchCriteria" in result

    @pytest.mark.asyncio
    async def test_hotel_search_basic(self):
        """Test basic hotel search functionality."""
        from tools.search_hotels import search_hotels

        result = await search_hotels(
            location="Austin",
            arrival_date="2025-10-01",
            departure_date="2025-10-04",
            adults=2
        )

        # Basic structure checks
        assert isinstance(result, dict)
        assert "searchCriteria" in result

    @pytest.mark.asyncio
    async def test_car_search_basic(self):
        """Test basic car search functionality."""
        from tools.search_cars import search_cars

        result = await search_cars(
            city="Austin",
            pickup_date="2025-10-01",
            return_date="2025-10-04",
            days=3
        )

        # Basic structure checks
        assert isinstance(result, dict)
        assert "searchCriteria" in result

    @pytest.mark.asyncio
    async def test_train_search_basic(self):
        """Test basic train search functionality."""
        from tools.search_trains import search_trains

        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=2
        )

        # Basic structure checks
        assert isinstance(result, dict)
        assert "searchCriteria" in result

    @pytest.mark.asyncio
    async def test_itinerary_generation_basic(self):
        """Test basic itinerary generation functionality."""
        from tools.generate_itinerary import generate_itinerary

        result = await generate_itinerary(
            city="Austin",
            days=2,
            interests=["food", "culture"]
        )

        # Basic structure checks
        assert isinstance(result, dict)
        assert "summary" in result
        assert "itinerary" in result

    @pytest.mark.asyncio
    async def test_core_services_basic(self):
        """Test basic core services functionality."""
        from core.services import DateValidator, HotelParameterMapper, HotelResponseFormatter

        # Test DateValidator
        validator = DateValidator()
        assert validator.validate_date("2025-10-01") is True
        assert validator.validate_date("invalid-date") is False

        # Test HotelParameterMapper
        mapper = HotelParameterMapper()
        params = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2
        }
        mapped = mapper.map_parameters(params)
        assert mapped["location"] == "Austin"

        # Test HotelResponseFormatter
        formatter = HotelResponseFormatter()
        raw_data = {
            "status": True,
            "data": {"hotels": []}
        }
        formatted = formatter.format_response(raw_data, params)
        assert "searchCriteria" in formatted


class TestAsyncBehavior:
    """Test async behavior works correctly."""

    @pytest.mark.asyncio
    async def test_multiple_async_calls(self):
        """Test that multiple async calls work."""
        from tools.search_flights import search_flights
        from tools.search_hotels import search_hotels

        # Make multiple concurrent calls
        flight_task = search_flights("AUS", "SFO", "2025-10-01")
        hotel_task = search_hotels("Austin", "2025-10-01", "2025-10-04", 2)

        flight_result, hotel_result = await asyncio.gather(flight_task, hotel_task)

        assert isinstance(flight_result, dict)
        assert isinstance(hotel_result, dict)

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test that functions handle errors gracefully."""
        from tools.search_flights import search_flights

        # This should not crash, even with potentially problematic inputs
        result = await search_flights("", "", "2025-10-01")
        assert isinstance(result, dict)


class TestDataValidation:
    """Test data validation and consistency."""

    @pytest.mark.asyncio
    async def test_response_structure_consistency(self):
        """Test that all tools return consistent response structures."""
        from tools.search_flights import search_flights
        from tools.search_hotels import search_hotels
        from tools.search_cars import search_cars
        from tools.search_trains import search_trains

        # All search tools should return dict with searchCriteria
        flight_result = await search_flights("AUS", "SFO", "2025-10-01")
        hotel_result = await search_hotels("Austin", "2025-10-01", "2025-10-04", 2)
        car_result = await search_cars("Austin", "2025-10-01", "2025-10-04", 3)
        train_result = await search_trains("NYC", "Boston", "2025-10-01", 2)

        for result in [flight_result, hotel_result, car_result, train_result]:
            assert isinstance(result, dict)
            assert "searchCriteria" in result

    def test_interface_compliance(self):
        """Test that core services implement their interfaces correctly."""
        from core.services import DateValidator, HotelParameterMapper, HotelResponseFormatter
        from core.interfaces import IDateValidator, IParameterMapper, IDataFormatter

        validator = DateValidator()
        mapper = HotelParameterMapper()
        formatter = HotelResponseFormatter()

        assert isinstance(validator, IDateValidator)
        assert isinstance(mapper, IParameterMapper)
        assert isinstance(formatter, IDataFormatter)