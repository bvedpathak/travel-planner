"""
Pytest configuration and shared fixtures.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any


@pytest.fixture
def sample_flight_params() -> Dict[str, Any]:
    """Sample flight search parameters."""
    return {
        "from_id": "AUS",
        "to_id": "SFO",
        "depart_date": "2025-10-01",
        "adults": 2
    }


@pytest.fixture
def sample_hotel_params() -> Dict[str, Any]:
    """Sample hotel search parameters."""
    return {
        "location": "Austin",
        "arrival_date": "2025-10-01",
        "departure_date": "2025-10-04",
        "adults": 2
    }


@pytest.fixture
def sample_car_params() -> Dict[str, Any]:
    """Sample car rental parameters."""
    return {
        "city": "Austin",
        "pickup_date": "2025-10-01",
        "return_date": "2025-10-04",
        "days": 3,
        "car_type": "economy"
    }


@pytest.fixture
def sample_train_params() -> Dict[str, Any]:
    """Sample train search parameters."""
    return {
        "from": "NYC",
        "to": "Boston",
        "date": "2025-10-01",
        "passengers": 2
    }


@pytest.fixture
def sample_itinerary_params() -> Dict[str, Any]:
    """Sample itinerary generation parameters."""
    return {
        "city": "Austin",
        "days": 3,
        "interests": ["food", "culture", "nature"]
    }


@pytest.fixture
def future_date() -> str:
    """Return a future date string."""
    return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")


@pytest.fixture
def past_date() -> str:
    """Return a past date string."""
    return (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")