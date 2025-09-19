"""
Itinerary generation tool for the Travel Planner MCP Server.

Generates detailed travel itineraries based on city, duration, and interests.
In a production environment, this could integrate with local APIs, reviews, and real-time data.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Comprehensive city data with attractions, restaurants, and activities
CITY_DATA = {
    "Austin": {
        "attractions": [
            {"name": "Texas State Capitol", "type": "culture", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Lady Bird Lake", "type": "nature", "duration": "Half day", "cost": "Free"},
            {"name": "South Congress Bridge Bats", "type": "nature", "duration": "1 hour", "cost": "Free"},
            {"name": "Zilker Park", "type": "nature", "duration": "Half day", "cost": "Free"},
            {"name": "Blanton Museum of Art", "type": "culture", "duration": "2-3 hours", "cost": "$12"},
            {"name": "Bullock Texas State History Museum", "type": "culture", "duration": "3-4 hours", "cost": "$15"},
            {"name": "Austin City Limits Music Festival", "type": "nightlife", "duration": "Full day", "cost": "$100+"},
            {"name": "South Congress Shopping", "type": "shopping", "duration": "3-4 hours", "cost": "Varies"},
            {"name": "Barton Springs Pool", "type": "nature", "duration": "2-3 hours", "cost": "$5"},
            {"name": "6th Street Entertainment District", "type": "nightlife", "duration": "Evening", "cost": "Varies"}
        ],
        "restaurants": [
            {"name": "Franklin Barbecue", "type": "food", "cuisine": "BBQ", "price": "$$", "note": "Famous BBQ, expect long lines"},
            {"name": "Uchi", "type": "food", "cuisine": "Japanese", "price": "$$$", "note": "Upscale sushi restaurant"},
            {"name": "Torchy's Tacos", "type": "food", "cuisine": "Mexican", "price": "$", "note": "Local taco chain"},
            {"name": "The Salt Lick", "type": "food", "cuisine": "BBQ", "price": "$$", "note": "Hill Country BBQ"},
            {"name": "Amy's Ice Cream", "type": "food", "cuisine": "Dessert", "price": "$", "note": "Local ice cream shop"},
            {"name": "Paperboy", "type": "food", "cuisine": "Breakfast", "price": "$$", "note": "Popular breakfast spot"},
            {"name": "Veracruz All Natural", "type": "food", "cuisine": "Mexican", "price": "$", "note": "Fresh Mexican food"},
            {"name": "Home Slice Pizza", "type": "food", "cuisine": "Italian", "price": "$$", "note": "NY-style pizza"}
        ],
        "activities": [
            {"name": "Kayaking on Lady Bird Lake", "type": "nature", "duration": "2-3 hours", "cost": "$30-50"},
            {"name": "Food truck tours", "type": "food", "duration": "3-4 hours", "cost": "$40-60"},
            {"name": "Live music at The Continental Club", "type": "nightlife", "duration": "Evening", "cost": "$10-20"},
            {"name": "Hiking at Mount Bonnell", "type": "nature", "duration": "1-2 hours", "cost": "Free"},
            {"name": "Shopping at The Domain", "type": "shopping", "duration": "Half day", "cost": "Varies"}
        ]
    },
    "San Francisco": {
        "attractions": [
            {"name": "Golden Gate Bridge", "type": "nature", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Alcatraz Island", "type": "culture", "duration": "Half day", "cost": "$45"},
            {"name": "Fisherman's Wharf", "type": "culture", "duration": "3-4 hours", "cost": "Free"},
            {"name": "Lombard Street", "type": "culture", "duration": "1 hour", "cost": "Free"},
            {"name": "Golden Gate Park", "type": "nature", "duration": "Half day", "cost": "Free"},
            {"name": "Chinatown", "type": "culture", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Mission District Murals", "type": "culture", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Cable Car rides", "type": "culture", "duration": "1-2 hours", "cost": "$8"},
            {"name": "Coit Tower", "type": "culture", "duration": "1-2 hours", "cost": "$10"},
            {"name": "Palace of Fine Arts", "type": "culture", "duration": "1-2 hours", "cost": "Free"}
        ],
        "restaurants": [
            {"name": "Ghirardelli Ice Cream", "type": "food", "cuisine": "Dessert", "price": "$$", "note": "Famous chocolate and ice cream"},
            {"name": "Swan Oyster Depot", "type": "food", "cuisine": "Seafood", "price": "$$$", "note": "Historic seafood counter"},
            {"name": "Mission Chinese Food", "type": "food", "cuisine": "Chinese", "price": "$$", "note": "Modern Chinese cuisine"},
            {"name": "Tartine Bakery", "type": "food", "cuisine": "Bakery", "price": "$$", "note": "Artisanal bakery"},
            {"name": "In-N-Out Burger", "type": "food", "cuisine": "American", "price": "$", "note": "California burger chain"},
            {"name": "Boudin Bakery", "type": "food", "cuisine": "Bakery", "price": "$$", "note": "Famous sourdough bread"},
            {"name": "La Taquería", "type": "food", "cuisine": "Mexican", "price": "$", "note": "Authentic Mission burritos"}
        ],
        "activities": [
            {"name": "Wine tasting in Napa Valley", "type": "food", "duration": "Full day", "cost": "$100-200"},
            {"name": "Bike ride across Golden Gate Bridge", "type": "nature", "duration": "Half day", "cost": "$40-60"},
            {"name": "Food tour in Chinatown", "type": "food", "duration": "3-4 hours", "cost": "$60-80"},
            {"name": "Shopping at Union Square", "type": "shopping", "duration": "Half day", "cost": "Varies"},
            {"name": "Sunset at Baker Beach", "type": "nature", "duration": "2 hours", "cost": "Free"}
        ]
    },
    "New York": {
        "attractions": [
            {"name": "Central Park", "type": "nature", "duration": "Half day", "cost": "Free"},
            {"name": "Statue of Liberty", "type": "culture", "duration": "Half day", "cost": "$25"},
            {"name": "Times Square", "type": "culture", "duration": "2-3 hours", "cost": "Free"},
            {"name": "9/11 Memorial", "type": "culture", "duration": "2-3 hours", "cost": "$26"},
            {"name": "Brooklyn Bridge", "type": "culture", "duration": "1-2 hours", "cost": "Free"},
            {"name": "High Line", "type": "nature", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Empire State Building", "type": "culture", "duration": "2-3 hours", "cost": "$42"},
            {"name": "Metropolitan Museum of Art", "type": "culture", "duration": "Half day", "cost": "$30"},
            {"name": "Broadway Show", "type": "nightlife", "duration": "3 hours", "cost": "$80-300"},
            {"name": "Little Italy", "type": "culture", "duration": "2-3 hours", "cost": "Free"}
        ],
        "restaurants": [
            {"name": "Katz's Delicatessen", "type": "food", "cuisine": "Deli", "price": "$$", "note": "Famous pastrami sandwiches"},
            {"name": "Peter Luger Steak House", "type": "food", "cuisine": "Steakhouse", "price": "$$$$", "note": "Historic Brooklyn steakhouse"},
            {"name": "Di Fara Pizza", "type": "food", "cuisine": "Pizza", "price": "$$", "note": "Artisanal Brooklyn pizza"},
            {"name": "Russ & Daughters", "type": "food", "cuisine": "Jewish", "price": "$$", "note": "Traditional appetizing shop"},
            {"name": "Joe's Pizza", "type": "food", "cuisine": "Pizza", "price": "$", "note": "Classic NY pizza slice"},
            {"name": "Levain Bakery", "type": "food", "cuisine": "Bakery", "price": "$", "note": "Famous cookies"},
            {"name": "Xi'an Famous Foods", "type": "food", "cuisine": "Chinese", "price": "$", "note": "Hand-pulled noodles"}
        ],
        "activities": [
            {"name": "Food tour in Greenwich Village", "type": "food", "duration": "3-4 hours", "cost": "$70-90"},
            {"name": "Shopping in SoHo", "type": "shopping", "duration": "Half day", "cost": "Varies"},
            {"name": "Jazz at Blue Note", "type": "nightlife", "duration": "Evening", "cost": "$30-50"},
            {"name": "Ferry to Staten Island", "type": "nature", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Rooftop bars in Manhattan", "type": "nightlife", "duration": "Evening", "cost": "$15-25/drink"}
        ]
    },
    "Miami": {
        "attractions": [
            {"name": "South Beach", "type": "nature", "duration": "Half day", "cost": "Free"},
            {"name": "Art Deco Historic District", "type": "culture", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Vizcaya Museum & Gardens", "type": "culture", "duration": "3-4 hours", "cost": "$22"},
            {"name": "Wynwood Walls", "type": "culture", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Little Havana", "type": "culture", "duration": "3-4 hours", "cost": "Free"},
            {"name": "Bayside Marketplace", "type": "shopping", "duration": "2-3 hours", "cost": "Free"},
            {"name": "Miami Beach Boardwalk", "type": "nature", "duration": "1-2 hours", "cost": "Free"},
            {"name": "Pérez Art Museum Miami", "type": "culture", "duration": "2-3 hours", "cost": "$16"}
        ],
        "restaurants": [
            {"name": "Joe's Stone Crab", "type": "food", "cuisine": "Seafood", "price": "$$$", "note": "Iconic Miami seafood"},
            {"name": "Versailles Restaurant", "type": "food", "cuisine": "Cuban", "price": "$$", "note": "Famous Cuban restaurant"},
            {"name": "Yardbird Southern Table", "type": "food", "cuisine": "Southern", "price": "$$", "note": "Modern Southern cuisine"},
            {"name": "Puerto Sagua", "type": "food", "cuisine": "Cuban", "price": "$", "note": "Authentic Cuban diner"},
            {"name": "The Bazaar by José Andrés", "type": "food", "cuisine": "Spanish", "price": "$$$$", "note": "Upscale Spanish tapas"}
        ],
        "activities": [
            {"name": "Art Basel Miami Beach", "type": "culture", "duration": "Full day", "cost": "$50+"},
            {"name": "Boat tour of Biscayne Bay", "type": "nature", "duration": "2-3 hours", "cost": "$40-60"},
            {"name": "Salsa dancing in Little Havana", "type": "nightlife", "duration": "Evening", "cost": "$20-30"},
            {"name": "Shopping at Lincoln Road", "type": "shopping", "duration": "Half day", "cost": "Varies"}
        ]
    }
}

async def generate_itinerary(city: str, days: int, interests: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate a detailed travel itinerary for a specified city and duration.

    Args:
        city: Destination city
        days: Number of days (1-7)
        interests: List of interests (food, culture, nature, nightlife, shopping)

    Returns:
        Dictionary containing a detailed day-by-day itinerary
    """

    # Validate city
    if city not in CITY_DATA:
        return {
            "error": f"Itinerary generation not available for: {city}",
            "available_cities": list(CITY_DATA.keys())
        }

    # Validate days
    if days < 1 or days > 7:
        return {"error": "Itinerary generation supports 1-7 days"}

    # Default interests if none provided
    if not interests:
        interests = ["culture", "food", "nature"]

    # Get city data
    city_data = CITY_DATA[city]

    # Filter activities based on interests
    filtered_attractions = [item for item in city_data["attractions"] if item["type"] in interests]
    filtered_restaurants = city_data["restaurants"]
    filtered_activities = [item for item in city_data["activities"] if item["type"] in interests]

    # Generate itinerary
    itinerary = {}
    daily_plans = []

    for day in range(1, days + 1):
        day_key = f"day{day}"

        # Plan structure: Morning, Afternoon, Evening
        morning_activities = []
        afternoon_activities = []
        evening_activities = []

        # Morning (9 AM - 12 PM)
        if filtered_attractions:
            morning_attraction = random.choice(filtered_attractions)
            filtered_attractions.remove(morning_attraction)  # Don't repeat
            morning_activities.append({
                "time": "9:00 AM",
                "activity": morning_attraction["name"],
                "type": morning_attraction["type"],
                "duration": morning_attraction["duration"],
                "cost": morning_attraction["cost"],
                "description": f"Visit {morning_attraction['name']}"
            })

        # Add breakfast
        breakfast_spot = random.choice([r for r in filtered_restaurants if r.get("cuisine") in ["Breakfast", "Bakery", "American"]])
        if not breakfast_spot:
            breakfast_spot = random.choice(filtered_restaurants[:3])  # Fallback to any restaurant

        morning_activities.append({
            "time": "8:00 AM",
            "activity": f"Breakfast at {breakfast_spot['name']}",
            "type": "food",
            "cuisine": breakfast_spot["cuisine"],
            "price": breakfast_spot["price"],
            "note": breakfast_spot.get("note", "")
        })

        # Afternoon (1 PM - 5 PM)
        # Add lunch
        lunch_options = [r for r in filtered_restaurants if r["price"] in ["$", "$$"]]
        if lunch_options:
            lunch_spot = random.choice(lunch_options)
            afternoon_activities.append({
                "time": "1:00 PM",
                "activity": f"Lunch at {lunch_spot['name']}",
                "type": "food",
                "cuisine": lunch_spot["cuisine"],
                "price": lunch_spot["price"],
                "note": lunch_spot.get("note", "")
            })

        # Afternoon attraction or activity
        if filtered_activities:
            afternoon_activity = random.choice(filtered_activities)
            filtered_activities.remove(afternoon_activity)
            afternoon_activities.append({
                "time": "3:00 PM",
                "activity": afternoon_activity["name"],
                "type": afternoon_activity["type"],
                "duration": afternoon_activity["duration"],
                "cost": afternoon_activity["cost"],
                "description": f"Experience {afternoon_activity['name']}"
            })
        elif filtered_attractions:
            afternoon_attraction = random.choice(filtered_attractions)
            filtered_attractions.remove(afternoon_attraction)
            afternoon_activities.append({
                "time": "3:00 PM",
                "activity": afternoon_attraction["name"],
                "type": afternoon_attraction["type"],
                "duration": afternoon_attraction["duration"],
                "cost": afternoon_attraction["cost"],
                "description": f"Explore {afternoon_attraction['name']}"
            })

        # Evening (6 PM - 10 PM)
        # Dinner
        dinner_options = [r for r in filtered_restaurants if r["price"] in ["$$", "$$$", "$$$$"]]
        if dinner_options:
            dinner_spot = random.choice(dinner_options)
            evening_activities.append({
                "time": "7:00 PM",
                "activity": f"Dinner at {dinner_spot['name']}",
                "type": "food",
                "cuisine": dinner_spot["cuisine"],
                "price": dinner_spot["price"],
                "note": dinner_spot.get("note", "")
            })

        # Evening entertainment (if nightlife is an interest)
        if "nightlife" in interests:
            nightlife_options = [item for item in city_data["attractions"] + city_data["activities"] if item["type"] == "nightlife"]
            if nightlife_options:
                evening_spot = random.choice(nightlife_options)
                evening_activities.append({
                    "time": "9:00 PM",
                    "activity": evening_spot["name"],
                    "type": "nightlife",
                    "duration": evening_spot["duration"],
                    "cost": evening_spot["cost"],
                    "description": f"Enjoy {evening_spot['name']}"
                })

        # Compile day's schedule
        day_schedule = {
            "day": day,
            "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
            "morning": morning_activities,
            "afternoon": afternoon_activities,
            "evening": evening_activities,
            "dailyBudget": _estimate_daily_budget(morning_activities + afternoon_activities + evening_activities),
            "transportation": _suggest_transportation(city),
            "tips": _get_daily_tips(city, day, interests)
        }

        itinerary[day_key] = day_schedule
        daily_plans.append(day_schedule)

    # Generate overall trip summary
    total_budget = sum(day["dailyBudget"]["total"] for day in daily_plans)

    trip_summary = {
        "destination": city,
        "duration": f"{days} day{'s' if days > 1 else ''}",
        "interests": interests,
        "totalEstimatedBudget": {
            "perPerson": total_budget,
            "breakdown": {
                "food": sum(day["dailyBudget"]["food"] for day in daily_plans),
                "attractions": sum(day["dailyBudget"]["attractions"] for day in daily_plans),
                "activities": sum(day["dailyBudget"]["activities"] for day in daily_plans),
                "transportation": sum(day["dailyBudget"]["transportation"] for day in daily_plans)
            }
        },
        "bestTimeToVisit": _get_best_time_to_visit(city),
        "packingTips": _get_packing_tips(city),
        "localTips": _get_local_tips(city)
    }

    return {
        "summary": trip_summary,
        "itinerary": itinerary,
        "generatedAt": datetime.now().isoformat(),
        "note": "This is a generated itinerary. Times and availability may vary. Always confirm hours and reservations."
    }

def _estimate_daily_budget(activities: List[Dict]) -> Dict[str, int]:
    """Estimate daily budget breakdown."""
    food_cost = 0
    attraction_cost = 0
    activity_cost = 0

    for activity in activities:
        if activity["type"] == "food":
            price_map = {"$": 15, "$$": 35, "$$$": 65, "$$$$": 120}
            food_cost += price_map.get(activity.get("price", "$$"), 35)
        elif "cost" in activity:
            cost_str = activity["cost"]
            if cost_str == "Free":
                continue
            elif "$" in cost_str:
                # Extract number from cost string
                import re
                numbers = re.findall(r'\d+', cost_str)
                if numbers:
                    if activity["type"] == "nature":
                        activity_cost += int(numbers[0])
                    else:
                        attraction_cost += int(numbers[0])

    transportation = 25  # Daily transport estimate
    total = food_cost + attraction_cost + activity_cost + transportation

    return {
        "food": food_cost,
        "attractions": attraction_cost,
        "activities": activity_cost,
        "transportation": transportation,
        "total": total
    }

def _suggest_transportation(city: str) -> Dict[str, str]:
    """Suggest transportation options for the city."""
    transport_options = {
        "Austin": {"primary": "Car/Rideshare", "alternative": "Capital Metro Bus", "note": "Car recommended for attractions outside downtown"},
        "San Francisco": {"primary": "Public Transit", "alternative": "Walking + Muni", "note": "Excellent public transportation system"},
        "New York": {"primary": "Subway", "alternative": "Walking + Taxi", "note": "Subway is fastest for long distances"},
        "Miami": {"primary": "Car/Rideshare", "alternative": "Metrobus", "note": "Car recommended for beach areas"}
    }

    return transport_options.get(city, {"primary": "Walking/Rideshare", "alternative": "Public Transit", "note": "Check local transportation options"})

def _get_daily_tips(city: str, day: int, interests: List[str]) -> List[str]:
    """Generate daily tips based on city and day number."""
    tips = []

    if day == 1:
        tips.append("Start with major attractions to get oriented")
        tips.append("Download local transportation apps")

    if "food" in interests:
        tips.append("Make dinner reservations in advance")

    if "nature" in interests:
        tips.append("Check weather and dress appropriately")

    city_specific_tips = {
        "Austin": ["Keep Austin Weird!", "Music venues often have cover charges"],
        "San Francisco": ["Bring layers - weather changes quickly", "Book Alcatraz tickets in advance"],
        "New York": ["Subway is fastest but walking shows you more", "Tipping is expected"],
        "Miami": ["UV protection essential", "Many attractions close early on Sundays"]
    }

    tips.extend(city_specific_tips.get(city, ["Enjoy your trip!"]))

    return tips[:3]  # Limit to 3 tips

def _get_best_time_to_visit(city: str) -> str:
    """Suggest best time to visit the city."""
    best_times = {
        "Austin": "March-May and September-November (avoid summer heat)",
        "San Francisco": "September-November (warmest and clearest weather)",
        "New York": "April-June and September-November (mild weather)",
        "Miami": "December-April (dry season, less humid)"
    }

    return best_times.get(city, "Spring and fall generally offer the best weather")

def _get_packing_tips(city: str) -> List[str]:
    """Provide city-specific packing tips."""
    packing_tips = {
        "Austin": ["Light, breathable clothing", "Comfortable walking shoes", "Sunscreen and hat"],
        "San Francisco": ["Layered clothing", "Light jacket", "Comfortable walking shoes"],
        "New York": ["Comfortable walking shoes", "Weather-appropriate clothing", "Small day bag"],
        "Miami": ["Swimwear", "Light clothing", "Sunscreen", "Sandals and comfortable shoes"]
    }

    return packing_tips.get(city, ["Comfortable shoes", "Weather-appropriate clothing", "Camera"])

def _get_local_tips(city: str) -> List[str]:
    """Provide local insider tips."""
    local_tips = {
        "Austin": ["Food trucks are a local institution", "Music is everywhere - embrace it", "Traffic can be heavy during rush hour"],
        "San Francisco": ["Steep hills everywhere - wear good shoes", "Foggy afternoons are common", "Neighborhoods have distinct personalities"],
        "New York": ["Walk fast and stay right", "Street food is safe and delicious", "Each borough has its own character"],
        "Miami": ["Spanish is widely spoken", "Beach culture is relaxed", "Art scene is world-class"]
    }

    return local_tips.get(city, ["Ask locals for recommendations", "Try local specialties", "Be open to new experiences"])