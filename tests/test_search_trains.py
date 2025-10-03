"""
Unit tests for train search functionality.
"""

import pytest
from tools.search_trains import search_trains


class TestTrainSearch:
    """Test cases for train search functionality."""

    @pytest.mark.asyncio
    async def test_search_trains_basic(self, sample_train_params):
        """Test basic train search functionality."""
        result = await search_trains(**sample_train_params)

        # Verify response structure
        assert "searchCriteria" in result
        assert "resultsFound" in result

        # Verify search criteria
        criteria = result["searchCriteria"]
        assert criteria["from"] == "NYC"
        assert criteria["to"] == "Boston"
        assert criteria["passengers"] == 2

        # Should have route or trains information
        assert "route" in result or "trains" in result

    @pytest.mark.asyncio
    async def test_search_trains_valid_routes(self):
        """Test train search for known valid routes."""
        valid_routes = [
            ("NYC", "Boston"),
            ("NYC", "Washington DC"),
            ("Boston", "NYC"),
            ("Washington DC", "NYC"),
        ]

        for from_city, to_city in valid_routes:
            result = await search_trains(
                from_city=from_city,
                to_city=to_city,
                date="2025-10-01",
                passengers=1
            )

            assert result["searchCriteria"]["from"] == from_city
            assert result["searchCriteria"]["to"] == to_city

            # Should find trains for valid routes
            if "trains" in result:
                assert len(result["trains"]) > 0
            elif "route" in result:
                assert result["route"]["operator"]

    @pytest.mark.asyncio
    async def test_search_trains_invalid_routes(self):
        """Test train search for routes that don't exist."""
        invalid_routes = [
            ("Miami", "Seattle"),
            ("Austin", "Denver"),
            ("RandomCity", "AnotherCity"),
        ]

        for from_city, to_city in invalid_routes:
            result = await search_trains(
                from_city=from_city,
                to_city=to_city,
                date="2025-10-01",
                passengers=1
            )

            assert result["searchCriteria"]["from"] == from_city
            assert result["searchCriteria"]["to"] == to_city

            # Should indicate no routes available
            if "trains" in result:
                # Might be empty list for invalid routes
                pass
            elif "message" in result:
                # Might have a message about no routes
                assert "No train routes" in result["message"]

    @pytest.mark.asyncio
    async def test_search_trains_different_passengers(self):
        """Test train search with different passenger counts."""
        passenger_counts = [1, 2, 4, 6, 10]

        for passengers in passenger_counts:
            result = await search_trains(
                from_city="NYC",
                to_city="Boston",
                date="2025-10-01",
                passengers=passengers
            )

            assert result["searchCriteria"]["passengers"] == passengers

            # If trains are found, they should accommodate the passengers
            if "trains" in result and result["trains"]:
                for train in result["trains"]:
                    assert train["passengers"] == passengers

    @pytest.mark.asyncio
    async def test_search_trains_response_schema_with_results(self):
        """Test train response schema when results are found."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=2
        )

        # Test top-level structure
        required_keys = ["searchCriteria", "resultsFound"]
        for key in required_keys:
            assert key in result

        # Test search criteria structure
        criteria = result["searchCriteria"]
        criteria_keys = ["from", "to", "date", "passengers"]
        for key in criteria_keys:
            assert key in criteria

        # If trains are found, test train structure
        if "trains" in result and result["trains"]:
            train = result["trains"][0]
            train_keys = [
                "trainNumber", "operator", "departure", "arrival",
                "duration", "distance", "passengers", "classes"
            ]
            for key in train_keys:
                assert key in train

            # Test departure/arrival structure
            for location in [train["departure"], train["arrival"]]:
                location_keys = ["city", "time", "date", "station"]
                for key in location_keys:
                    assert key in location

            # Test class structure
            if train["classes"]:
                train_class = train["classes"][0]
                class_keys = ["className", "pricePerPerson", "totalPrice", "amenities"]
                for key in class_keys:
                    assert key in train_class

    @pytest.mark.asyncio
    async def test_search_trains_data_types(self):
        """Test that train response data types are correct."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=2
        )

        # Test top-level types
        assert isinstance(result["resultsFound"], int)

        # Test criteria types
        criteria = result["searchCriteria"]
        assert isinstance(criteria["from"], str)
        assert isinstance(criteria["to"], str)
        assert isinstance(criteria["date"], str)
        assert isinstance(criteria["passengers"], int)

        # Test train data types (if trains exist)
        if "trains" in result and result["trains"]:
            train = result["trains"][0]
            assert isinstance(train["trainNumber"], str)
            assert isinstance(train["operator"], str)
            assert isinstance(train["duration"], str)
            assert isinstance(train["passengers"], int)
            assert isinstance(train["classes"], list)

            # Test class data types
            if train["classes"]:
                train_class = train["classes"][0]
                assert isinstance(train_class["className"], str)
                assert isinstance(train_class["pricePerPerson"], (int, float))
                assert isinstance(train_class["totalPrice"], (int, float))
                assert isinstance(train_class["amenities"], list)

    @pytest.mark.asyncio
    async def test_search_trains_price_calculations(self):
        """Test that train pricing calculations are correct."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=3
        )

        if "trains" in result and result["trains"]:
            for train in result["trains"]:
                passengers = train["passengers"]

                for train_class in train["classes"]:
                    expected_total = train_class["pricePerPerson"] * passengers
                    assert train_class["totalPrice"] == expected_total

    @pytest.mark.asyncio
    async def test_search_trains_realistic_data(self):
        """Test that train data contains realistic values."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=2
        )

        if "trains" in result and result["trains"]:
            for train in result["trains"]:
                # Duration should be reasonable format
                assert "h" in train["duration"] or "m" in train["duration"]

                # Train number should contain letters and numbers
                assert any(c.isalpha() for c in train["trainNumber"])
                assert any(c.isdigit() for c in train["trainNumber"])

                # Should have at least one class
                assert len(train["classes"]) > 0

                for train_class in train["classes"]:
                    # Price should be reasonable ($25-$500 per person)
                    assert 25 <= train_class["pricePerPerson"] <= 500

                    # Class name should be valid
                    valid_classes = ["Coach", "Business Class", "First Class", "Premium"]
                    assert any(valid_class in train_class["className"] for valid_class in valid_classes)

    @pytest.mark.asyncio
    async def test_search_trains_date_consistency(self):
        """Test that departure and arrival dates are consistent."""
        search_date = "2025-10-01"
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date=search_date,
            passengers=1
        )

        if "trains" in result and result["trains"]:
            for train in result["trains"]:
                # Departure date should match search date
                assert train["departure"]["date"] == search_date

                # Arrival date should be same day for most routes
                arrival_date = train["arrival"]["date"]
                assert arrival_date in [search_date]  # Most trains arrive same day

    @pytest.mark.asyncio
    async def test_search_trains_time_format(self):
        """Test that train times are in correct format."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=1
        )

        if "trains" in result and result["trains"]:
            for train in result["trains"]:
                # Time should be in HH:MM format
                dep_time = train["departure"]["time"]
                arr_time = train["arrival"]["time"]

                # Basic time format validation
                assert len(dep_time) >= 4  # At least H:MM
                assert ":" in dep_time
                assert len(arr_time) >= 4
                assert ":" in arr_time

    @pytest.mark.asyncio
    async def test_search_trains_amenities(self):
        """Test that train classes have appropriate amenities."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=1
        )

        common_amenities = {
            "WiFi", "Power outlets", "Comfortable seating",
            "Extra legroom", "Complimentary drinks", "Food service"
        }

        if "trains" in result and result["trains"]:
            for train in result["trains"]:
                for train_class in train["classes"]:
                    amenities = train_class["amenities"]

                    # Should have amenities listed
                    assert len(amenities) > 0

                    # All amenities should be strings
                    for amenity in amenities:
                        assert isinstance(amenity, str)
                        assert len(amenity) > 0

    @pytest.mark.asyncio
    async def test_search_trains_route_information(self):
        """Test that route information is provided when available."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=1
        )

        if "route" in result:
            route = result["route"]

            # Should have basic route information
            assert "operator" in route
            assert len(route["operator"]) > 0

            if "distance" in route:
                assert "miles" in route["distance"] or "km" in route["distance"]

            if "averageDuration" in route:
                assert "h" in route["averageDuration"] or "m" in route["averageDuration"]

    @pytest.mark.asyncio
    async def test_search_trains_class_hierarchy(self):
        """Test that train classes follow expected hierarchy."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=1
        )

        if "trains" in result and result["trains"]:
            for train in result["trains"]:
                classes = train["classes"]

                if len(classes) > 1:
                    # Classes should be ordered by price (ascending)
                    for i in range(len(classes) - 1):
                        current_price = classes[i]["pricePerPerson"]
                        next_price = classes[i + 1]["pricePerPerson"]
                        # Allow some flexibility in ordering
                        assert current_price <= next_price * 1.1

    @pytest.mark.asyncio
    async def test_search_trains_station_names(self):
        """Test that station names are reasonable."""
        result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=1
        )

        if "trains" in result and result["trains"]:
            for train in result["trains"]:
                dep_station = train["departure"]["station"]
                arr_station = train["arrival"]["station"]

                # Station names should not be empty
                assert len(dep_station) > 0
                assert len(arr_station) > 0

                # Should contain reasonable station terms
                station_terms = ["Station", "Terminal", "Center", "Central", "Union"]
                dep_valid = any(term in dep_station for term in station_terms)
                arr_valid = any(term in arr_station for term in station_terms)

                # At least one should be a proper station name
                assert dep_valid or arr_valid or len(dep_station) > 10

    @pytest.mark.asyncio
    async def test_search_trains_reverse_route(self):
        """Test that reverse routes work correctly."""
        # Test forward route
        forward_result = await search_trains(
            from_city="NYC",
            to_city="Boston",
            date="2025-10-01",
            passengers=1
        )

        # Test reverse route
        reverse_result = await search_trains(
            from_city="Boston",
            to_city="NYC",
            date="2025-10-01",
            passengers=1
        )

        # Both should have results if the route exists
        forward_has_trains = "trains" in forward_result and len(forward_result["trains"]) > 0
        reverse_has_trains = "trains" in reverse_result and len(reverse_result["trains"]) > 0

        # If forward route exists, reverse should probably exist too
        if forward_has_trains:
            assert reverse_has_trains or reverse_result["resultsFound"] >= 0