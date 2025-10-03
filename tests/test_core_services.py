"""
Unit tests for SOLID-compliant core services.
"""

import pytest
from datetime import datetime, timedelta
from core.services import (
    DateValidator,
    HotelParameterMapper,
    HotelResponseFormatter
)
from core.interfaces import IDateValidator, IParameterMapper, IDataFormatter


class TestDateValidator:
    """Test cases for DateValidator service."""

    def test_date_validator_implements_interface(self):
        """Test that DateValidator implements IDateValidator interface."""
        validator = DateValidator()
        assert isinstance(validator, IDateValidator)

    def test_validate_date_valid_formats(self):
        """Test date validation with valid date formats."""
        validator = DateValidator()

        valid_dates = [
            "2025-01-01",
            "2025-12-31",
            "2026-06-15",
            datetime.now().strftime("%Y-%m-%d")
        ]

        for date_str in valid_dates:
            assert validator.validate_date(date_str) is True

    def test_validate_date_invalid_formats(self):
        """Test date validation with invalid date formats."""
        validator = DateValidator()

        invalid_dates = [
            "2025/01/01",   # Wrong separator
            "01-01-2025",   # Wrong order
            "2025-13-01",   # Invalid month
            "2025-01-32",   # Invalid day
            "invalid-date", # Not a date
            "",             # Empty string
            "2025-1-1",     # Single digit month/day
        ]

        for date_str in invalid_dates:
            assert validator.validate_date(date_str) is False

    def test_validate_date_past_dates(self):
        """Test date validation with past dates."""
        validator = DateValidator()

        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert validator.validate_date(past_date) is False

    def test_validate_date_future_dates(self):
        """Test date validation with future dates."""
        validator = DateValidator()

        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        assert validator.validate_date(future_date) is True

    def test_format_date(self):
        """Test date formatting functionality."""
        validator = DateValidator()

        # Test with valid date
        formatted = validator.format_date("2025-01-01")
        assert formatted == "2025-01-01"

        # Test with datetime object
        date_obj = datetime(2025, 1, 1)
        formatted = validator.format_date(date_obj.strftime("%Y-%m-%d"))
        assert formatted == "2025-01-01"


class TestHotelParameterMapper:
    """Test cases for HotelParameterMapper service."""

    def test_parameter_mapper_implements_interface(self):
        """Test that HotelParameterMapper implements IParameterMapper interface."""
        mapper = HotelParameterMapper()
        assert isinstance(mapper, IParameterMapper)

    def test_map_search_parameters_basic(self):
        """Test basic parameter mapping."""
        mapper = HotelParameterMapper()

        input_params = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2
        }

        mapped = mapper.map_parameters(input_params)

        assert "location" in mapped
        assert "arrival_date" in mapped
        assert "departure_date" in mapped
        assert "adults" in mapped

    def test_map_search_parameters_with_optional(self):
        """Test parameter mapping with optional parameters."""
        mapper = HotelParameterMapper()

        input_params = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2,
            "children_age": "5,8",
            "room_qty": 2,
            "currency_code": "EUR",
            "languagecode": "fr-fr"
        }

        mapped = mapper.map_parameters(input_params)

        assert mapped["children_age"] == "5,8"
        assert mapped["room_qty"] == 2
        assert mapped["currency_code"] == "EUR"
        assert mapped["languagecode"] == "fr-fr"

    def test_map_search_parameters_defaults(self):
        """Test parameter mapping with default values."""
        mapper = HotelParameterMapper()

        input_params = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2
        }

        mapped = mapper.map_parameters(input_params)

        # Should have defaults
        assert mapped.get("currency_code", "USD") == "USD"
        assert mapped.get("languagecode", "en-us") == "en-us"

    def test_map_search_parameters_validation(self):
        """Test parameter validation during mapping."""
        mapper = HotelParameterMapper()

        # Test with missing required parameters
        invalid_params = {
            "location": "Austin"
            # Missing dates and adults
        }

        with pytest.raises((KeyError, ValueError)):
            mapper.map_parameters(invalid_params)


class TestHotelResponseFormatter:
    """Test cases for HotelResponseFormatter service."""

    def test_response_formatter_implements_interface(self):
        """Test that HotelResponseFormatter implements IResponseFormatter interface."""
        formatter = HotelResponseFormatter()
        assert isinstance(formatter, IDataFormatter)

    def test_format_response_basic(self):
        """Test basic response formatting."""
        formatter = HotelResponseFormatter()

        raw_data = {
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
        }

        search_criteria = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2
        }

        formatted = formatter.format_response(raw_data, search_criteria)

        assert "searchCriteria" in formatted
        assert "resultsFound" in formatted
        assert "hotels" in formatted
        assert len(formatted["hotels"]) == 1

        hotel = formatted["hotels"][0]
        assert hotel["hotelId"] == "12345"
        assert hotel["hotelName"] == "Test Hotel"
        assert hotel["pricePerNight"] == 150.0
        assert hotel["totalPrice"] == 450.0

    def test_format_response_empty_data(self):
        """Test response formatting with empty data."""
        formatter = HotelResponseFormatter()

        raw_data = {
            "status": True,
            "message": "Success",
            "data": {"hotels": []}
        }

        search_criteria = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2
        }

        formatted = formatter.format_response(raw_data, search_criteria)

        assert formatted["resultsFound"] == 0
        assert len(formatted["hotels"]) == 0

    def test_format_response_error_handling(self):
        """Test response formatting with API errors."""
        formatter = HotelResponseFormatter()

        raw_data = {
            "status": False,
            "message": "API Error",
            "data": None
        }

        search_criteria = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2
        }

        # Should not raise exception, should return fallback
        formatted = formatter.format_response(raw_data, search_criteria)

        assert "searchCriteria" in formatted
        assert "resultsFound" in formatted
        assert "hotels" in formatted


# Commented out until FlightSearchService and HotelSearchService are implemented
# class TestFlightSearchService:
#     """Test cases for FlightSearchService."""
#     pass

# class TestHotelSearchService:
#     """Test cases for HotelSearchService."""
#     pass


class TestServiceIntegration:
    """Integration tests for core services."""

    @pytest.mark.asyncio
    async def test_services_work_together(self):
        """Test that all services can work together."""
        # Test date validation
        validator = DateValidator()
        assert validator.validate_date("2025-10-01") is True

        # Test parameter mapping
        mapper = HotelParameterMapper()
        params = {
            "location": "Austin",
            "arrival_date": "2025-10-01",
            "departure_date": "2025-10-04",
            "adults": 2
        }
        mapped = mapper.map_parameters(params)
        assert mapped["location"] == "Austin"

        # Test response formatting
        formatter = HotelResponseFormatter()
        raw_data = {
            "status": True,
            "data": {"hotels": []}
        }
        formatted = formatter.format_response(raw_data, params)
        assert "searchCriteria" in formatted

        # Test that components work together
        # (Full service integration will be tested when HotelSearchService is implemented)
        assert validator.validate_date(params["arrival_date"]) is True
        assert mapped["location"] == "Austin"
        assert "searchCriteria" in formatted

    def test_solid_principles_adherence(self):
        """Test that services adhere to SOLID principles."""
        # Single Responsibility: Each service has one responsibility
        validator = DateValidator()  # Only validates dates
        mapper = HotelParameterMapper()  # Only maps parameters
        formatter = HotelResponseFormatter()  # Only formats responses

        # Interface Segregation: Services depend only on interfaces they need
        # (Will be tested when service classes are implemented)

        # Dependency Inversion: Depends on abstractions
        assert isinstance(validator, IDateValidator)
        assert isinstance(mapper, IParameterMapper)
        assert isinstance(formatter, IDataFormatter)

    def test_service_substitutability(self):
        """Test that services can be substituted (Liskov Substitution)."""
        # Any IDateValidator implementation should work
        validator1 = DateValidator()

        # Different implementations should be substitutable
        # (Will be tested when service classes are implemented)
        assert isinstance(validator1, IDateValidator)

    def test_open_closed_principle(self):
        """Test that services are open for extension but closed for modification."""
        # We can extend functionality by creating new implementations
        class CustomDateValidator(DateValidator):
            def validate_date(self, date_str: str) -> bool:
                # Extended validation logic
                return super().validate_date(date_str) and len(date_str) == 10

        custom_validator = CustomDateValidator()

        # Extended validator should still implement the interface
        assert isinstance(custom_validator, IDateValidator)
        assert isinstance(custom_validator, CustomDateValidator)