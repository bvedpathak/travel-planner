"""
Unit tests for car rental search functionality.
"""

import pytest
from tools.search_cars import search_cars


class TestCarSearch:
    """Test cases for car rental search functionality."""

    @pytest.mark.asyncio
    async def test_search_cars_basic(self, sample_car_params):
        """Test basic car rental search functionality."""
        result = await search_cars(**sample_car_params)

        # Verify response structure
        assert "searchCriteria" in result
        assert "resultsFound" in result
        assert "cars" in result

        # Verify search criteria
        criteria = result["searchCriteria"]
        assert criteria["city"] == "Austin"
        assert criteria["pickupDate"] == "2025-10-01"
        assert criteria["returnDate"] == "2025-10-04"
        assert criteria["days"] == 3

        # Verify cars data
        assert isinstance(result["cars"], list)
        assert result["resultsFound"] == len(result["cars"])

    @pytest.mark.asyncio
    async def test_search_cars_different_cities(self):
        """Test car rental search for different cities."""
        cities = ["Austin", "San Francisco", "New York", "Miami", "Chicago"]

        for city in cities:
            result = await search_cars(
                city=city,
                pickup_date="2025-10-01",
                return_date="2025-10-04",
                days=3
            )

            assert result["searchCriteria"]["city"] == city
            assert len(result["cars"]) > 0

    @pytest.mark.asyncio
    async def test_search_cars_different_durations(self):
        """Test car rental search for different rental periods."""
        durations = [
            ("2025-10-01", "2025-10-02", 1),  # 1 day
            ("2025-10-01", "2025-10-08", 7),  # 1 week
            ("2025-10-01", "2025-10-15", 14), # 2 weeks
        ]

        for pickup, return_date, days in durations:
            result = await search_cars(
                city="Austin",
                pickup_date=pickup,
                return_date=return_date,
                days=days
            )

            assert result["searchCriteria"]["days"] == days
            assert result["searchCriteria"]["pickupDate"] == pickup
            assert result["searchCriteria"]["returnDate"] == return_date

    @pytest.mark.asyncio
    async def test_search_cars_different_types(self):
        """Test car rental search for different car types."""
        car_types = ["economy", "compact", "suv", "luxury", "premium"]

        for car_type in car_types:
            result = await search_cars(
                city="Austin",
                pickup_date="2025-10-01",
                return_date="2025-10-04",
                days=3,
                car_type=car_type
            )

            assert result["searchCriteria"]["carType"] == car_type
            # Should return cars of the requested type
            for car in result["cars"]:
                assert car_type.lower() in car["carType"].lower()

    @pytest.mark.asyncio
    async def test_search_cars_response_schema(self, sample_car_params):
        """Test that car rental response matches expected schema."""
        result = await search_cars(**sample_car_params)

        # Test top-level structure
        required_keys = ["searchCriteria", "resultsFound", "cars"]
        for key in required_keys:
            assert key in result

        # Test search criteria structure
        criteria = result["searchCriteria"]
        criteria_keys = ["city", "pickupDate", "returnDate", "days"]
        for key in criteria_keys:
            assert key in criteria

        # Test car structure
        if result["cars"]:
            car = result["cars"][0]
            car_keys = [
                "company", "carType", "model", "pickupLocation", "city",
                "pickupDate", "returnDate", "rentalDays", "pricing",
                "specifications", "features", "policies"
            ]
            for key in car_keys:
                assert key in car

            # Test pricing structure
            pricing = car["pricing"]
            pricing_keys = ["dailyRate", "subtotal", "taxesAndFees", "totalCost"]
            for key in pricing_keys:
                assert key in pricing

            # Test specifications structure
            specs = car["specifications"]
            spec_keys = ["passengers", "luggage", "doors", "transmission", "fuelType"]
            for key in spec_keys:
                assert key in specs

    @pytest.mark.asyncio
    async def test_search_cars_data_types(self, sample_car_params):
        """Test that car rental response data types are correct."""
        result = await search_cars(**sample_car_params)

        # Test top-level types
        assert isinstance(result["resultsFound"], int)
        assert isinstance(result["cars"], list)

        # Test criteria types
        criteria = result["searchCriteria"]
        assert isinstance(criteria["city"], str)
        assert isinstance(criteria["pickupDate"], str)
        assert isinstance(criteria["returnDate"], str)
        assert isinstance(criteria["days"], int)

        # Test car data types
        if result["cars"]:
            car = result["cars"][0]
            assert isinstance(car["company"], str)
            assert isinstance(car["carType"], str)
            assert isinstance(car["model"], str)
            assert isinstance(car["rentalDays"], int)

            # Test pricing types
            pricing = car["pricing"]
            assert isinstance(pricing["dailyRate"], (int, float))
            assert isinstance(pricing["subtotal"], (int, float))
            assert isinstance(pricing["taxesAndFees"], (int, float))
            assert isinstance(pricing["totalCost"], (int, float))

    @pytest.mark.asyncio
    async def test_search_cars_price_calculations(self, sample_car_params):
        """Test that car rental pricing calculations are correct."""
        result = await search_cars(**sample_car_params)

        for car in result["cars"]:
            pricing = car["pricing"]
            rental_days = car["rentalDays"]

            # Subtotal should equal daily rate * days
            expected_subtotal = pricing["dailyRate"] * rental_days
            assert abs(pricing["subtotal"] - expected_subtotal) < 0.01

            # Total cost should equal subtotal + taxes and fees
            expected_total = pricing["subtotal"] + pricing["taxesAndFees"]
            assert abs(pricing["totalCost"] - expected_total) < 0.01

    @pytest.mark.asyncio
    async def test_search_cars_realistic_data(self, sample_car_params):
        """Test that car rental data contains realistic values."""
        result = await search_cars(**sample_car_params)

        for car in result["cars"]:
            # Daily rate should be reasonable ($15-$300 per day)
            assert 15 <= car["pricing"]["dailyRate"] <= 300

            # Rental days should match search criteria
            assert car["rentalDays"] == sample_car_params["days"]

            # Company should not be empty
            assert len(car["company"]) > 0

            # Model should not be empty
            assert len(car["model"]) > 0

            # Features should be a list
            assert isinstance(car["features"], list)

    @pytest.mark.asyncio
    async def test_search_cars_date_consistency(self, sample_car_params):
        """Test that pickup and return dates are consistent."""
        result = await search_cars(**sample_car_params)

        search_pickup = sample_car_params["pickup_date"]
        search_return = sample_car_params["return_date"]

        for car in result["cars"]:
            assert car["pickupDate"] == search_pickup
            assert car["returnDate"] == search_return
            assert car["city"] == sample_car_params["city"]

    @pytest.mark.asyncio
    async def test_search_cars_company_variety(self, sample_car_params):
        """Test that results include multiple rental companies."""
        result = await search_cars(**sample_car_params)

        if len(result["cars"]) > 1:
            companies = {car["company"] for car in result["cars"]}
            # Should have multiple companies represented
            assert len(companies) > 1

    @pytest.mark.asyncio
    async def test_search_cars_specifications_validity(self, sample_car_params):
        """Test that car specifications are valid."""
        result = await search_cars(**sample_car_params)

        for car in result["cars"]:
            specs = car["specifications"]

            # Passenger count should be reasonable
            passengers = specs["passengers"]
            if "-" in passengers:
                min_pass, max_pass = map(int, passengers.split("-"))
                assert 1 <= min_pass <= max_pass <= 15
            else:
                assert 1 <= int(passengers) <= 15

            # Doors should be reasonable
            doors = specs["doors"]
            assert doors in ["2", "3", "4", "5", "2-4", "4-5"]

            # Transmission should be valid
            transmission = specs["transmission"]
            assert transmission in ["Manual", "Automatic", "CVT"]

    @pytest.mark.asyncio
    async def test_search_cars_features_content(self, sample_car_params):
        """Test that car features are reasonable."""
        result = await search_cars(**sample_car_params)

        common_features = {
            "Air Conditioning", "GPS Navigation", "Bluetooth",
            "Backup Camera", "Cruise Control", "Power Windows",
            "Power Steering", "AM/FM Radio", "USB Ports"
        }

        for car in result["cars"]:
            features = car["features"]

            # Should have some common features
            assert len(features) > 0

            # All features should be strings
            for feature in features:
                assert isinstance(feature, str)
                assert len(feature) > 0

    @pytest.mark.asyncio
    async def test_search_cars_policies_content(self, sample_car_params):
        """Test that car rental policies are included."""
        result = await search_cars(**sample_car_params)

        for car in result["cars"]:
            policies = car["policies"]

            # Should have basic policy information
            assert "minimumAge" in policies
            assert "mileage" in policies
            assert "fuelPolicy" in policies

            # Minimum age should be reasonable
            min_age = policies["minimumAge"]
            assert 18 <= min_age <= 25

    @pytest.mark.asyncio
    async def test_search_cars_long_term_rental(self):
        """Test car rental search for long-term rentals."""
        result = await search_cars(
            city="Austin",
            pickup_date="2025-10-01",
            return_date="2025-10-31",
            days=30
        )

        assert result["searchCriteria"]["days"] == 30

        for car in result["cars"]:
            # Long-term rentals might have discounted daily rates
            assert car["rentalDays"] == 30
            assert car["pricing"]["totalCost"] > 0

    @pytest.mark.asyncio
    async def test_search_cars_short_term_rental(self):
        """Test car rental search for short-term rentals."""
        result = await search_cars(
            city="Austin",
            pickup_date="2025-10-01",
            return_date="2025-10-01",
            days=1
        )

        assert result["searchCriteria"]["days"] == 1

        for car in result["cars"]:
            assert car["rentalDays"] == 1
            # Short-term rentals might have higher daily rates
            assert car["pricing"]["dailyRate"] > 0

    @pytest.mark.asyncio
    async def test_search_cars_pickup_locations(self, sample_car_params):
        """Test that pickup locations are appropriate for the city."""
        result = await search_cars(**sample_car_params)

        city = sample_car_params["city"]

        for car in result["cars"]:
            pickup_location = car["pickupLocation"]
            # Pickup location should mention the city or be an airport/station
            location_terms = ["Airport", "Downtown", "Station", city]
            assert any(term in pickup_location for term in location_terms)