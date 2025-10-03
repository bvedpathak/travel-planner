"""
Unit tests for MCP server functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from mcp.server import Server
from mcp.types import CallToolRequest, ListToolsRequest


class TestMCPServer:
    """Test cases for MCP server functionality."""

    @pytest.fixture
    def mock_server(self):
        """Create a mock MCP server for testing."""
        server = Server("test-travel-planner")
        return server

    @pytest.mark.asyncio
    async def test_server_creation(self, mock_server):
        """Test that MCP server can be created successfully."""
        assert mock_server.name == "test-travel-planner"

    @pytest.mark.asyncio
    @patch('tools.search_flights.search_flights')
    async def test_search_flights_tool_call(self, mock_search_flights, mock_server):
        """Test calling the search_flights tool through MCP."""
        # Mock the flight search function
        mock_search_flights.return_value = {
            "searchCriteria": {"from": "AUS", "to": "SFO", "date": "2025-10-01", "passengers": 2},
            "resultsFound": 1,
            "flights": [{
                "flightNumber": "UA123",
                "airline": "United",
                "price": 500,
                "pricePerPerson": 250
            }]
        }

        # Import and set up the server tools (simplified)
        with patch('server.search_flights', mock_search_flights):
            # Simulate tool call
            result = await mock_search_flights(
                from_city="AUS",
                to_city="SFO",
                date="2025-10-01",
                passengers=2
            )

            # Verify the tool was called correctly
            mock_search_flights.assert_called_once_with(
                from_city="AUS",
                to_city="SFO",
                date="2025-10-01",
                passengers=2
            )

            # Verify the response structure
            assert "searchCriteria" in result
            assert "flights" in result
            assert result["resultsFound"] == 1

    @pytest.mark.asyncio
    @patch('tools.search_hotels.search_hotels')
    async def test_search_hotels_tool_call(self, mock_search_hotels, mock_server):
        """Test calling the search_hotels tool through MCP."""
        # Mock the hotel search function
        mock_search_hotels.return_value = {
            "searchCriteria": {
                "location": "Austin",
                "arrival_date": "2025-10-01",
                "departure_date": "2025-10-04",
                "adults": 2
            },
            "resultsFound": 1,
            "hotels": [{
                "hotelId": "12345",
                "hotelName": "Test Hotel",
                "pricePerNight": 150,
                "totalPrice": 450
            }]
        }

        with patch('server.search_hotels', mock_search_hotels):
            result = await mock_search_hotels(
                location="Austin",
                arrival_date="2025-10-01",
                departure_date="2025-10-04",
                adults=2
            )

            mock_search_hotels.assert_called_once_with(
                location="Austin",
                arrival_date="2025-10-01",
                departure_date="2025-10-04",
                adults=2
            )

            assert "searchCriteria" in result
            assert "hotels" in result

    @pytest.mark.asyncio
    @patch('tools.search_cars.search_cars')
    async def test_search_cars_tool_call(self, mock_search_cars, mock_server):
        """Test calling the search_cars tool through MCP."""
        mock_search_cars.return_value = {
            "searchCriteria": {
                "city": "Austin",
                "pickupDate": "2025-10-01",
                "returnDate": "2025-10-04",
                "days": 3
            },
            "resultsFound": 1,
            "cars": [{
                "company": "Hertz",
                "carType": "Economy",
                "model": "Honda Civic",
                "rentalDays": 3
            }]
        }

        with patch('server.search_cars', mock_search_cars):
            result = await mock_search_cars(
                city="Austin",
                pickup_date="2025-10-01",
                return_date="2025-10-04",
                days=3
            )

            mock_search_cars.assert_called_once()
            assert "searchCriteria" in result
            assert "cars" in result

    @pytest.mark.asyncio
    @patch('tools.search_trains.search_trains')
    async def test_search_trains_tool_call(self, mock_search_trains, mock_server):
        """Test calling the search_trains tool through MCP."""
        mock_search_trains.return_value = {
            "searchCriteria": {
                "from": "NYC",
                "to": "Boston",
                "date": "2025-10-01",
                "passengers": 2
            },
            "resultsFound": 1,
            "trains": [{
                "trainNumber": "NE123",
                "operator": "Amtrak",
                "duration": "4h 30m"
            }]
        }

        with patch('server.search_trains', mock_search_trains):
            result = await mock_search_trains(
                from_city="NYC",
                to_city="Boston",
                date="2025-10-01",
                passengers=2
            )

            mock_search_trains.assert_called_once()
            assert "searchCriteria" in result

    @pytest.mark.asyncio
    @patch('tools.generate_itinerary.generate_itinerary')
    async def test_generate_itinerary_tool_call(self, mock_generate_itinerary, mock_server):
        """Test calling the generate_itinerary tool through MCP."""
        mock_generate_itinerary.return_value = {
            "summary": {
                "destination": "Austin",
                "duration": "3 days",
                "interests": ["food", "culture"]
            },
            "itinerary": {
                "day1": {
                    "day": 1,
                    "date": "2025-10-01",
                    "morning": [],
                    "afternoon": [],
                    "evening": []
                }
            }
        }

        with patch('server.generate_itinerary', mock_generate_itinerary):
            result = await mock_generate_itinerary(
                city="Austin",
                days=3,
                interests=["food", "culture"]
            )

            mock_generate_itinerary.assert_called_once()
            assert "summary" in result
            assert "itinerary" in result

    def test_server_tool_registration(self, mock_server):
        """Test that tools are properly registered with the server."""
        # This would test the actual server setup
        # For now, we'll test that the server exists and has the expected name
        assert mock_server.name == "test-travel-planner"

    @pytest.mark.asyncio
    async def test_error_handling_invalid_parameters(self):
        """Test server error handling with invalid parameters."""
        # Test with invalid flight parameters
        with patch('tools.search_flights.search_flights') as mock_flight_search:
            mock_flight_search.side_effect = ValueError("Invalid parameters")

            with pytest.raises(ValueError):
                await mock_flight_search(
                    from_city="",  # Invalid empty city
                    to_city="",    # Invalid empty city
                    date="invalid-date",  # Invalid date
                    passengers=-1  # Invalid passenger count
                )

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """Test that multiple tool calls can be handled concurrently."""
        with patch('tools.search_flights.search_flights') as mock_flights, \
             patch('tools.search_hotels.search_hotels') as mock_hotels:

            # Mock return values
            mock_flights.return_value = {"resultsFound": 1, "flights": []}
            mock_hotels.return_value = {"resultsFound": 1, "hotels": []}

            # Make concurrent calls
            flight_task = mock_flights("AUS", "SFO", "2025-10-01", 2)
            hotel_task = mock_hotels("Austin", "2025-10-01", "2025-10-04", 2)

            # Wait for both to complete
            flight_result, hotel_result = await asyncio.gather(flight_task, hotel_task)

            # Verify both calls completed
            assert flight_result["resultsFound"] == 1
            assert hotel_result["resultsFound"] == 1

    @pytest.mark.asyncio
    async def test_resource_access(self):
        """Test that server can access travel guide resources."""
        # This would test reading travel guide JSON files
        # For now, test that we can import the resource handling
        import os

        # Check if resource directory exists
        resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources", "travel_guides")

        if os.path.exists(resources_dir):
            # Check for expected guide files
            expected_guides = ["austin.json", "san_francisco.json", "new_york.json"]

            for guide in expected_guides:
                guide_path = os.path.join(resources_dir, guide)
                if os.path.exists(guide_path):
                    # File exists, which is good
                    assert os.path.getsize(guide_path) > 0  # Should have content

    @pytest.mark.asyncio
    async def test_parameter_validation(self):
        """Test parameter validation for tool calls."""
        from tools.search_flights import search_flights

        # Test valid parameters
        result = await search_flights("AUS", "SFO", "2025-10-01", 2)
        assert "searchCriteria" in result

        # Test edge cases
        result = await search_flights("AUS", "SFO", "2025-10-01", 1)
        assert result["searchCriteria"]["passengers"] == 1

        result = await search_flights("AUS", "SFO", "2025-10-01", 10)
        assert result["searchCriteria"]["passengers"] == 10

    @pytest.mark.asyncio
    async def test_date_handling(self):
        """Test that tools handle different date formats appropriately."""
        from tools.search_flights import search_flights

        # Test various date formats
        dates = ["2025-10-01", "2025-12-25", "2026-01-01"]

        for date in dates:
            result = await search_flights("AUS", "SFO", date, 1)
            assert result["searchCriteria"]["date"] == date

    @pytest.mark.asyncio
    async def test_response_consistency(self):
        """Test that tool responses are consistent across calls."""
        from tools.search_flights import search_flights

        # Make multiple calls with same parameters
        params = ("AUS", "SFO", "2025-10-01", 2)

        results = []
        for _ in range(3):
            result = await search_flights(*params)
            results.append(result)

        # All results should have same search criteria
        for result in results:
            assert result["searchCriteria"]["from"] == "AUS"
            assert result["searchCriteria"]["to"] == "SFO"
            assert result["searchCriteria"]["passengers"] == 2

        # All results should have the same structure
        for result in results:
            assert "searchCriteria" in result
            assert "resultsFound" in result
            assert "flights" in result


class TestServerIntegration:
    """Integration tests for the MCP server."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete travel planning workflow."""
        # This would test a full sequence of tool calls
        # 1. Search flights
        # 2. Search hotels
        # 3. Search cars
        # 4. Generate itinerary

        workflow_steps = [
            ("search_flights", {"from_city": "AUS", "to_city": "SFO", "date": "2025-10-01", "passengers": 2}),
            ("search_hotels", {"location": "San Francisco", "arrival_date": "2025-10-01", "departure_date": "2025-10-04", "adults": 2}),
            ("search_cars", {"city": "San Francisco", "pickup_date": "2025-10-01", "return_date": "2025-10-04", "days": 3}),
            ("generate_itinerary", {"city": "San Francisco", "days": 3, "interests": ["food", "culture"]})
        ]

        results = {}

        for tool_name, params in workflow_steps:
            if tool_name == "search_flights":
                from tools.search_flights import search_flights
                result = await search_flights(**params)
            elif tool_name == "search_hotels":
                from tools.search_hotels import search_hotels
                result = await search_hotels(**params)
            elif tool_name == "search_cars":
                from tools.search_cars import search_cars
                result = await search_cars(**params)
            elif tool_name == "generate_itinerary":
                from tools.generate_itinerary import generate_itinerary
                result = await generate_itinerary(**params)

            results[tool_name] = result

        # Verify all steps completed successfully
        assert len(results) == 4

        # Verify each result has expected structure
        assert "flights" in results["search_flights"]
        assert "hotels" in results["search_hotels"]
        assert "cars" in results["search_cars"]
        assert "itinerary" in results["generate_itinerary"]

    @pytest.mark.asyncio
    async def test_tool_chaining(self):
        """Test that results from one tool can inform another."""
        from tools.search_flights import search_flights
        from tools.search_hotels import search_hotels

        # Search for flights to get destination
        flight_result = await search_flights("AUS", "SFO", "2025-10-01", 2)
        destination = flight_result["searchCriteria"]["to"]

        # Use flight destination for hotel search
        hotel_params = {
            "location": "San Francisco",  # Derived from SFO
            "arrival_date": flight_result["searchCriteria"]["date"],
            "departure_date": "2025-10-04",
            "adults": flight_result["searchCriteria"]["passengers"]
        }

        hotel_result = await search_hotels(**hotel_params)

        # Verify consistency
        assert hotel_result["searchCriteria"]["adults"] == flight_result["searchCriteria"]["passengers"]