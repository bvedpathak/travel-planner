"""
Integration tests for the Travel Planner system.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from tools.search_flights import search_flights
from tools.search_hotels import search_hotels
from tools.search_cars import search_cars
from tools.search_trains import search_trains
from tools.generate_itinerary import generate_itinerary


class TestSystemIntegration:
    """Integration tests for the complete travel planning system."""

    @pytest.mark.asyncio
    async def test_complete_travel_planning_workflow(self):
        """Test a complete travel planning workflow from start to finish."""
        # Step 1: Search for flights
        flight_result = await search_flights(
            from_city="AUS",
            to_city="SFO",
            date="2025-10-01",
            passengers=2
        )

        assert "flights" in flight_result
        assert flight_result["searchCriteria"]["from"] == "AUS"
        assert flight_result["searchCriteria"]["to"] == "SFO"

        # Step 2: Search for hotels in destination city
        hotel_result = await search_hotels(
            location="San Francisco",
            arrival_date="2025-10-01",
            departure_date="2025-10-04",
            adults=2
        )

        assert "hotels" in hotel_result
        assert hotel_result["searchCriteria"]["location"] == "San Francisco"

        # Step 3: Search for rental cars
        car_result = await search_cars(
            city="San Francisco",
            pickup_date="2025-10-01",
            return_date="2025-10-04",
            days=3
        )

        assert "cars" in car_result
        assert car_result["searchCriteria"]["city"] == "San Francisco"

        # Step 4: Search for train options (if applicable)
        train_result = await search_trains(
            from_city="San Francisco",
            to_city="Los Angeles",
            date="2025-10-02",
            passengers=2
        )

        assert "searchCriteria" in train_result

        # Step 5: Generate itinerary
        itinerary_result = await generate_itinerary(
            city="San Francisco",
            days=3,
            interests=["food", "culture", "nature"]
        )

        assert "itinerary" in itinerary_result
        assert itinerary_result["summary"]["destination"] == "San Francisco"

        # Verify workflow consistency
        # Passenger counts should match
        assert flight_result["searchCriteria"]["passengers"] == hotel_result["searchCriteria"]["adults"]

        # Dates should be consistent
        assert flight_result["searchCriteria"]["date"] == hotel_result["searchCriteria"]["arrival_date"]
        assert hotel_result["searchCriteria"]["arrival_date"] == car_result["searchCriteria"]["pickupDate"]

    @pytest.mark.asyncio
    async def test_cross_tool_data_consistency(self):
        """Test that data remains consistent across different tools."""
        # Test parameters
        destination = "Austin"
        start_date = "2025-10-01"
        end_date = "2025-10-04"
        travelers = 2

        # Search flights to destination
        flights = await search_flights("NYC", "AUS", start_date, travelers)

        # Search hotels in destination
        hotels = await search_hotels(destination, start_date, end_date, travelers)

        # Search cars in destination
        cars = await search_cars(destination, start_date, end_date, 3)

        # Generate itinerary for destination
        itinerary = await generate_itinerary(destination, 3, ["food", "culture"])

        # Verify consistency
        assert flights["searchCriteria"]["to"] == "AUS"  # Austin airport code
        assert hotels["searchCriteria"]["location"] == destination
        assert cars["searchCriteria"]["city"] == destination
        assert itinerary["summary"]["destination"] == destination

        # Verify traveler counts
        assert flights["searchCriteria"]["passengers"] == travelers
        assert hotels["searchCriteria"]["adults"] == travelers

    @pytest.mark.asyncio
    async def test_error_recovery_and_fallbacks(self):
        """Test system behavior when some tools fail."""
        # Test with potentially problematic inputs
        results = {}

        # Try each tool with edge case inputs
        try:
            results["flights"] = await search_flights("", "", "2025-10-01", 1)
        except Exception as e:
            results["flights_error"] = str(e)

        try:
            results["hotels"] = await search_hotels("NonexistentCity", "2025-10-01", "2025-10-04", 1)
        except Exception as e:
            results["hotels_error"] = str(e)

        try:
            results["cars"] = await search_cars("NonexistentCity", "2025-10-01", "2025-10-04", 3)
        except Exception as e:
            results["cars_error"] = str(e)

        try:
            results["trains"] = await search_trains("RandomCity", "AnotherCity", "2025-10-01", 1)
        except Exception as e:
            results["trains_error"] = str(e)

        try:
            results["itinerary"] = await generate_itinerary("NonexistentCity", 1, ["unknown"])
        except Exception as e:
            results["itinerary_error"] = str(e)

        # System should handle errors gracefully
        # At least some tools should work or return valid fallback responses
        successful_tools = [key for key in results.keys() if not key.endswith("_error")]
        assert len(successful_tools) > 0, "At least one tool should work or provide fallback"

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test that multiple tools can run concurrently without interference."""
        # Create tasks for concurrent execution
        tasks = [
            search_flights("AUS", "SFO", "2025-10-01", 2),
            search_hotels("San Francisco", "2025-10-01", "2025-10-04", 2),
            search_cars("San Francisco", "2025-10-01", "2025-10-04", 3),
            search_trains("NYC", "Boston", "2025-10-01", 2),
            generate_itinerary("San Francisco", 3, ["food", "culture"])
        ]

        # Execute all tools concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all tools completed (successfully or with graceful handling)
        assert len(results) == 5

        # Check that results are reasonable
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                assert isinstance(result, dict), f"Tool {i} should return a dictionary"

    @pytest.mark.asyncio
    async def test_realistic_trip_planning_scenarios(self):
        """Test realistic trip planning scenarios."""
        scenarios = [
            {
                "name": "Business Trip",
                "origin": "NYC",
                "destination": "Austin",
                "destination_city": "Austin",
                "dates": ("2025-10-01", "2025-10-03"),
                "travelers": 1,
                "interests": ["culture", "food"]
            },
            {
                "name": "Family Vacation",
                "origin": "AUS",
                "destination": "SFO",
                "destination_city": "San Francisco",
                "dates": ("2025-10-15", "2025-10-22"),
                "travelers": 4,
                "interests": ["nature", "food", "culture"]
            },
            {
                "name": "Weekend Getaway",
                "origin": "LAX",
                "destination": "NYC",
                "destination_city": "New York",
                "dates": ("2025-11-01", "2025-11-03"),
                "travelers": 2,
                "interests": ["culture", "entertainment"]
            }
        ]

        for scenario in scenarios:
            # Calculate trip duration
            from datetime import datetime
            start = datetime.strptime(scenario["dates"][0], "%Y-%m-%d")
            end = datetime.strptime(scenario["dates"][1], "%Y-%m-%d")
            days = (end - start).days

            # Plan the trip
            flight_result = await search_flights(
                scenario["origin"],
                scenario["destination"],
                scenario["dates"][0],
                scenario["travelers"]
            )

            hotel_result = await search_hotels(
                scenario["destination_city"],
                scenario["dates"][0],
                scenario["dates"][1],
                scenario["travelers"]
            )

            car_result = await search_cars(
                scenario["destination_city"],
                scenario["dates"][0],
                scenario["dates"][1],
                days
            )

            itinerary_result = await generate_itinerary(
                scenario["destination_city"],
                days,
                scenario["interests"]
            )

            # Verify scenario completion
            assert "flights" in flight_result
            assert "hotels" in hotel_result
            assert "cars" in car_result
            assert "itinerary" in itinerary_result

            # Verify scenario-specific requirements
            assert flight_result["searchCriteria"]["passengers"] == scenario["travelers"]
            assert hotel_result["searchCriteria"]["adults"] == scenario["travelers"]
            assert itinerary_result["summary"]["interests"] == scenario["interests"]

    @pytest.mark.asyncio
    async def test_data_format_consistency(self):
        """Test that all tools return data in consistent formats."""
        # Get results from all tools
        flight_result = await search_flights("AUS", "SFO", "2025-10-01", 2)
        hotel_result = await search_hotels("San Francisco", "2025-10-01", "2025-10-04", 2)
        car_result = await search_cars("San Francisco", "2025-10-01", "2025-10-04", 3)
        train_result = await search_trains("NYC", "Boston", "2025-10-01", 2)
        itinerary_result = await generate_itinerary("San Francisco", 3, ["food"])

        results = [flight_result, hotel_result, car_result, train_result, itinerary_result]

        # All results should be dictionaries
        for result in results:
            assert isinstance(result, dict)

        # All results should have consistent structure patterns
        for result in [flight_result, hotel_result, car_result, train_result]:
            assert "searchCriteria" in result

        # Itinerary has different structure but should be consistent
        assert "summary" in itinerary_result
        assert "itinerary" in itinerary_result

        # Test data type consistency
        assert isinstance(flight_result["resultsFound"], int)
        assert isinstance(hotel_result["resultsFound"], int)
        assert isinstance(car_result["resultsFound"], int)
        assert isinstance(train_result["resultsFound"], int)

    @pytest.mark.asyncio
    async def test_international_travel_support(self):
        """Test system support for international travel scenarios."""
        # Test with international destinations
        international_scenarios = [
            {
                "from": "NYC",
                "to": "LHR",  # London
                "city": "London",
                "currency": "GBP",
                "language": "en-gb"
            },
            {
                "from": "LAX",
                "to": "NRT",  # Tokyo
                "city": "Tokyo",
                "currency": "JPY",
                "language": "ja-jp"
            }
        ]

        for scenario in international_scenarios:
            # Test flight search
            flight_result = await search_flights(
                scenario["from"],
                scenario["to"],
                "2025-10-01",
                2
            )
            assert "flights" in flight_result

            # Test hotel search with currency/language
            hotel_result = await search_hotels(
                location=scenario["city"],
                arrival_date="2025-10-01",
                departure_date="2025-10-04",
                adults=2,
                currency_code=scenario["currency"],
                languagecode=scenario["language"]
            )
            assert "hotels" in hotel_result

            # Test car search
            car_result = await search_cars(
                scenario["city"],
                "2025-10-01",
                "2025-10-04",
                3
            )
            assert "cars" in car_result

            # Test itinerary generation
            itinerary_result = await generate_itinerary(
                scenario["city"],
                3,
                ["culture", "food"]
            )
            assert "itinerary" in itinerary_result

    @pytest.mark.asyncio
    async def test_system_performance_and_reliability(self):
        """Test system performance and reliability under load."""
        # Test multiple concurrent requests
        num_concurrent = 5
        tasks = []

        for i in range(num_concurrent):
            tasks.extend([
                search_flights("AUS", "SFO", "2025-10-01", 2),
                search_hotels("San Francisco", "2025-10-01", "2025-10-04", 2),
                search_cars("San Francisco", "2025-10-01", "2025-10-04", 3)
            ])

        # Execute all tasks concurrently
        import time
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Verify all requests completed
        assert len(results) == num_concurrent * 3

        # Check for reasonable performance (this is a basic check)
        total_time = end_time - start_time
        assert total_time < 60, f"Total time {total_time}s seems too long for {len(tasks)} tasks"

        # Verify most requests succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful_results) / len(results)
        assert success_rate > 0.8, f"Success rate {success_rate} is too low"


class TestAPIIntegration:
    """Test integration with external APIs."""

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_hotel_api_integration(self, mock_get):
        """Test hotel search integration with live API."""
        # Mock successful API responses
        mock_geocoding_response = AsyncMock()
        mock_geocoding_response.status = 200
        mock_geocoding_response.json.return_value = [{
            "lat": "30.2672",
            "lon": "-97.7431",
            "display_name": "Austin, TX, USA"
        }]

        mock_hotel_response = AsyncMock()
        mock_hotel_response.status = 200
        mock_hotel_response.json.return_value = {
            "status": True,
            "data": {
                "hotels": [{
                    "hotel_id": "12345",
                    "hotel_name": "Test Hotel",
                    "address": "123 Main St",
                    "city": "Austin",
                    "country": "US",
                    "rating": 4.5,
                    "price_per_night": 150.0,
                    "total_price": 450.0,
                    "currency": "USD"
                }]
            }
        }

        # Configure mock to return appropriate response based on URL
        def mock_get_side_effect(url, **kwargs):
            if "nominatim" in str(url):
                return MockAsyncContextManager(mock_geocoding_response)
            else:
                return MockAsyncContextManager(mock_hotel_response)

        mock_get.side_effect = mock_get_side_effect

        # Test hotel search
        result = await search_hotels(
            location="Austin",
            arrival_date="2025-10-01",
            departure_date="2025-10-04",
            adults=2
        )

        # Verify API integration worked
        assert mock_get.called
        assert "hotels" in result
        if result["hotels"]:
            assert result["hotels"][0]["hotelName"] == "Test Hotel"

    @pytest.mark.asyncio
    async def test_geocoding_integration(self):
        """Test geocoding service integration."""
        from tools.search_hotels import get_coordinates_from_city

        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock geocoding response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = [{
                "lat": "30.2672",
                "lon": "-97.7431",
                "display_name": "Austin, Travis County, Texas, United States"
            }]

            mock_get.return_value.__aenter__.return_value = mock_response

            coordinates = await get_coordinates_from_city("Austin, TX")

            assert isinstance(coordinates, tuple)
            assert len(coordinates) == 2
            # Note: actual return values depend on mocked response structure


class MockAsyncContextManager:
    """Helper class for mocking async context managers."""

    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass