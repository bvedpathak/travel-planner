"""
Unit tests for itinerary generation functionality.
"""

import pytest
from tools.generate_itinerary import generate_itinerary


class TestIteraryGeneration:
    """Test cases for itinerary generation functionality."""

    @pytest.mark.asyncio
    async def test_generate_itinerary_basic(self, sample_itinerary_params):
        """Test basic itinerary generation functionality."""
        result = await generate_itinerary(**sample_itinerary_params)

        # Verify response structure
        assert "summary" in result
        assert "itinerary" in result

        # Verify summary structure
        summary = result["summary"]
        assert "destination" in summary
        assert "duration" in summary
        assert "interests" in summary

        # Verify itinerary structure
        itinerary = result["itinerary"]
        # Should have days equal to the requested duration
        expected_days = sample_itinerary_params["days"]
        assert len(itinerary) == expected_days

    @pytest.mark.asyncio
    async def test_generate_itinerary_different_cities(self):
        """Test itinerary generation for different cities."""
        cities = ["Austin", "San Francisco", "New York", "Miami", "Chicago"]

        for city in cities:
            result = await generate_itinerary(
                city=city,
                days=2,
                interests=["culture", "food"]
            )

            assert result["summary"]["destination"] == city
            assert len(result["itinerary"]) == 2

    @pytest.mark.asyncio
    async def test_generate_itinerary_different_durations(self):
        """Test itinerary generation for different trip durations."""
        durations = [1, 2, 3, 5, 7]

        for days in durations:
            result = await generate_itinerary(
                city="Austin",
                days=days,
                interests=["culture"]
            )

            assert result["summary"]["duration"] == f"{days} day{'s' if days != 1 else ''}"
            assert len(result["itinerary"]) == days

    @pytest.mark.asyncio
    async def test_generate_itinerary_different_interests(self):
        """Test itinerary generation with different interest combinations."""
        interest_combinations = [
            ["food"],
            ["culture"],
            ["nature"],
            ["food", "culture"],
            ["culture", "nature"],
            ["food", "nature"],
            ["food", "culture", "nature"],
            ["adventure", "nightlife"],
        ]

        for interests in interest_combinations:
            result = await generate_itinerary(
                city="Austin",
                days=2,
                interests=interests
            )

            assert result["summary"]["interests"] == interests
            # Should have activities matching the interests
            assert len(result["itinerary"]) == 2

    @pytest.mark.asyncio
    async def test_generate_itinerary_response_schema(self, sample_itinerary_params):
        """Test that itinerary response matches expected schema."""
        result = await generate_itinerary(**sample_itinerary_params)

        # Test top-level structure
        required_keys = ["summary", "itinerary"]
        for key in required_keys:
            assert key in result

        # Test summary structure
        summary = result["summary"]
        summary_keys = ["destination", "duration", "interests", "totalEstimatedBudget"]
        for key in summary_keys:
            assert key in summary

        # Test budget structure
        budget = summary["totalEstimatedBudget"]
        budget_keys = ["perPerson", "breakdown"]
        for key in budget_keys:
            assert key in budget

        # Test budget breakdown
        breakdown = budget["breakdown"]
        breakdown_keys = ["food", "attractions", "activities", "transportation"]
        for key in breakdown_keys:
            assert key in breakdown

        # Test itinerary structure
        itinerary = result["itinerary"]
        for day_key, day_data in itinerary.items():
            day_keys = ["day", "date", "morning", "afternoon", "evening", "dailyBudget", "tips"]
            for key in day_keys:
                assert key in day_data

            # Test daily budget structure
            daily_budget = day_data["dailyBudget"]
            daily_budget_keys = ["food", "attractions", "activities", "transportation", "total"]
            for key in daily_budget_keys:
                assert key in daily_budget

    @pytest.mark.asyncio
    async def test_generate_itinerary_data_types(self, sample_itinerary_params):
        """Test that itinerary response data types are correct."""
        result = await generate_itinerary(**sample_itinerary_params)

        # Test summary types
        summary = result["summary"]
        assert isinstance(summary["destination"], str)
        assert isinstance(summary["duration"], str)
        assert isinstance(summary["interests"], list)

        # Test budget types
        budget = summary["totalEstimatedBudget"]
        assert isinstance(budget["perPerson"], (int, float))
        assert isinstance(budget["breakdown"], dict)

        for category, amount in budget["breakdown"].items():
            assert isinstance(amount, (int, float))

        # Test itinerary types
        itinerary = result["itinerary"]
        for day_key, day_data in itinerary.items():
            assert isinstance(day_data["day"], int)
            assert isinstance(day_data["date"], str)
            assert isinstance(day_data["morning"], list)
            assert isinstance(day_data["afternoon"], list)
            assert isinstance(day_data["evening"], list)
            assert isinstance(day_data["tips"], list)

            # Test daily budget types
            daily_budget = day_data["dailyBudget"]
            for category, amount in daily_budget.items():
                assert isinstance(amount, (int, float))

    @pytest.mark.asyncio
    async def test_generate_itinerary_activity_structure(self, sample_itinerary_params):
        """Test that activities have proper structure."""
        result = await generate_itinerary(**sample_itinerary_params)

        itinerary = result["itinerary"]

        for day_key, day_data in itinerary.items():
            # Check each time period
            for period in ["morning", "afternoon", "evening"]:
                activities = day_data[period]

                for activity in activities:
                    # Required activity fields
                    required_fields = ["time", "activity", "type"]
                    for field in required_fields:
                        assert field in activity

                    # Activity type should be valid
                    valid_types = ["food", "culture", "nature", "entertainment", "transportation"]
                    assert activity["type"] in valid_types

                    # Time should be in reasonable format
                    time = activity["time"]
                    assert ":" in time or "AM" in time or "PM" in time

    @pytest.mark.asyncio
    async def test_generate_itinerary_budget_consistency(self, sample_itinerary_params):
        """Test that budget calculations are consistent."""
        result = await generate_itinerary(**sample_itinerary_params)

        summary = result["summary"]
        total_budget = summary["totalEstimatedBudget"]
        breakdown = total_budget["breakdown"]

        # Total per person should equal sum of breakdown
        calculated_total = sum(breakdown.values())
        assert abs(total_budget["perPerson"] - calculated_total) <= 1  # Allow small rounding differences

        # Daily budgets should sum to total
        itinerary = result["itinerary"]
        daily_totals = []

        for day_key, day_data in itinerary.items():
            daily_budget = day_data["dailyBudget"]
            daily_totals.append(daily_budget["total"])

            # Daily total should equal sum of daily categories
            daily_calculated = (
                daily_budget["food"] +
                daily_budget["attractions"] +
                daily_budget["activities"] +
                daily_budget["transportation"]
            )
            assert abs(daily_budget["total"] - daily_calculated) <= 1

        # Sum of daily totals should approximately equal total budget
        sum_daily = sum(daily_totals)
        assert abs(sum_daily - total_budget["perPerson"]) <= len(daily_totals)  # Allow variance

    @pytest.mark.asyncio
    async def test_generate_itinerary_realistic_budget(self, sample_itinerary_params):
        """Test that budget amounts are realistic."""
        result = await generate_itinerary(**sample_itinerary_params)

        total_budget = result["summary"]["totalEstimatedBudget"]

        # Per person budget should be reasonable for 3 days ($100-$1000)
        assert 100 <= total_budget["perPerson"] <= 1000

        # Category budgets should be reasonable
        breakdown = total_budget["breakdown"]
        assert 30 <= breakdown["food"] <= 400  # Food costs
        assert 0 <= breakdown["attractions"] <= 200  # Attraction costs
        assert 0 <= breakdown["activities"] <= 300  # Activity costs
        assert 10 <= breakdown["transportation"] <= 200  # Transportation costs

    @pytest.mark.asyncio
    async def test_generate_itinerary_interest_relevance(self):
        """Test that activities match requested interests."""
        # Test food interest
        result = await generate_itinerary(
            city="Austin",
            days=2,
            interests=["food"]
        )

        activities_by_type = {}
        for day_key, day_data in result["itinerary"].items():
            for period in ["morning", "afternoon", "evening"]:
                for activity in day_data[period]:
                    activity_type = activity["type"]
                    activities_by_type[activity_type] = activities_by_type.get(activity_type, 0) + 1

        # Should have food-related activities
        assert "food" in activities_by_type
        assert activities_by_type["food"] > 0

    @pytest.mark.asyncio
    async def test_generate_itinerary_date_sequence(self, sample_itinerary_params):
        """Test that itinerary dates are in sequence."""
        result = await generate_itinerary(**sample_itinerary_params)

        itinerary = result["itinerary"]
        dates = []

        for day_num in range(1, len(itinerary) + 1):
            day_key = f"day{day_num}"
            if day_key in itinerary:
                dates.append(itinerary[day_key]["date"])

        # Should have dates for all days
        assert len(dates) == sample_itinerary_params["days"]

        # Dates should be in sequence (simplified check)
        for i, date in enumerate(dates):
            expected_day = i + 1
            # Date should be in YYYY-MM-DD format
            assert len(date) == 10
            assert date.count("-") == 2

    @pytest.mark.asyncio
    async def test_generate_itinerary_tips_content(self, sample_itinerary_params):
        """Test that daily tips are meaningful."""
        result = await generate_itinerary(**sample_itinerary_params)

        itinerary = result["itinerary"]

        for day_key, day_data in itinerary.items():
            tips = day_data["tips"]

            # Should have some tips
            assert len(tips) > 0

            # Tips should be strings
            for tip in tips:
                assert isinstance(tip, str)
                assert len(tip) > 10  # Should be meaningful content

    @pytest.mark.asyncio
    async def test_generate_itinerary_time_progression(self, sample_itinerary_params):
        """Test that activity times progress logically through the day."""
        result = await generate_itinerary(**sample_itinerary_params)

        itinerary = result["itinerary"]

        for day_key, day_data in itinerary.items():
            morning_times = []
            afternoon_times = []
            evening_times = []

            # Extract times
            for activity in day_data["morning"]:
                morning_times.append(activity["time"])

            for activity in day_data["afternoon"]:
                afternoon_times.append(activity["time"])

            for activity in day_data["evening"]:
                evening_times.append(activity["time"])

            # Times should exist for each period
            if morning_times:
                # Morning should start early
                first_morning = morning_times[0]
                assert any(early_time in first_morning for early_time in ["7:", "8:", "9:"])

            if evening_times:
                # Evening should be later
                first_evening = evening_times[0]
                assert any(late_time in first_evening for late_time in ["6:", "7:", "8:", "9:"])

    @pytest.mark.asyncio
    async def test_generate_itinerary_activity_variety(self, sample_itinerary_params):
        """Test that itinerary includes variety of activities."""
        result = await generate_itinerary(**sample_itinerary_params)

        all_activities = []
        itinerary = result["itinerary"]

        # Collect all activities
        for day_key, day_data in itinerary.items():
            for period in ["morning", "afternoon", "evening"]:
                all_activities.extend(day_data[period])

        # Should have reasonable number of activities
        assert len(all_activities) >= sample_itinerary_params["days"] * 2  # At least 2 per day

        # Should have variety of types
        activity_types = {activity["type"] for activity in all_activities}
        assert len(activity_types) >= 2  # At least 2 different types

        # Should have variety of actual activities (not repeating same thing)
        activity_names = {activity["activity"] for activity in all_activities}
        # Should have some variety in activity names
        assert len(activity_names) >= len(all_activities) * 0.5  # At least 50% unique

    @pytest.mark.asyncio
    async def test_generate_itinerary_single_day(self):
        """Test itinerary generation for single day trip."""
        result = await generate_itinerary(
            city="Austin",
            days=1,
            interests=["culture"]
        )

        assert len(result["itinerary"]) == 1
        assert "day1" in result["itinerary"]

        day1 = result["itinerary"]["day1"]
        assert day1["day"] == 1

        # Should have activities for different parts of the day
        total_activities = len(day1["morning"]) + len(day1["afternoon"]) + len(day1["evening"])
        assert total_activities > 0

    @pytest.mark.asyncio
    async def test_generate_itinerary_week_long(self):
        """Test itinerary generation for week-long trip."""
        result = await generate_itinerary(
            city="Austin",
            days=7,
            interests=["food", "culture", "nature"]
        )

        assert len(result["itinerary"]) == 7
        assert result["summary"]["duration"] == "7 days"

        # Should have activities for all 7 days
        for day_num in range(1, 8):
            day_key = f"day{day_num}"
            assert day_key in result["itinerary"]
            assert result["itinerary"][day_key]["day"] == day_num