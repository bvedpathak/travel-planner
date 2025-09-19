#!/usr/bin/env python3
"""
Sample interactions with the Travel Planner MCP Server.

This script demonstrates how to interact with the travel planning tools
programmatically. It can be used for testing or as example code.
"""

import asyncio
import json
from typing import Dict, Any

# Import the tool functions directly for demonstration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.search_flights import search_flights
from tools.search_hotels import search_hotels
from tools.search_cars import search_cars
from tools.search_trains import search_trains
from tools.generate_itinerary import generate_itinerary

async def demo_flight_search():
    """Demonstrate flight search functionality."""
    print("🛫 Flight Search Demo")
    print("=" * 50)

    result = await search_flights(
        from_city="AUS",
        to_city="SFO",
        date="2025-10-01",
        passengers=2
    )

    print(f"Found {result['resultsFound']} flights:")
    for i, flight in enumerate(result['flights'][:3], 1):  # Show top 3
        print(f"\n{i}. {flight['airline']} {flight['flightNumber']}")
        print(f"   Departure: {flight['departure']['time']} from {flight['departure']['city']}")
        print(f"   Arrival: {flight['arrival']['time']} in {flight['arrival']['city']}")
        print(f"   Duration: {flight['duration']}")
        print(f"   Price: ${flight['price']} for {flight['passengers']} passengers")

    return result

async def demo_hotel_search():
    """Demonstrate hotel search functionality."""
    print("\n\n🏨 Hotel Search Demo")
    print("=" * 50)

    result = await search_hotels(
        city="Austin",
        check_in="2025-10-01",
        nights=3,
        guests=2
    )

    print(f"Found {result['resultsFound']} hotels:")
    for i, hotel in enumerate(result['hotels'][:3], 1):  # Show top 3
        print(f"\n{i}. {hotel['hotelName']} - {hotel['category']}")
        print(f"   Location: {hotel['location']}, {hotel['city']}")
        print(f"   Rating: {hotel['rating']}/5.0")
        print(f"   Check-in: {hotel['checkIn']} - Check-out: {hotel['checkOut']}")

        # Show cheapest room option
        cheapest_room = min(hotel['roomTypes'], key=lambda x: x['pricePerNight'])
        print(f"   Cheapest room: {cheapest_room['type']} - ${cheapest_room['totalPrice']} total")
        print(f"   Amenities: {', '.join(hotel['amenities'][:4])}...")

    return result

async def demo_car_search():
    """Demonstrate car rental search functionality."""
    print("\n\n🚗 Car Rental Search Demo")
    print("=" * 50)

    result = await search_cars(
        city="Austin",
        pickup_date="2025-10-01",
        days=3,
        car_type="suv"
    )

    print(f"Found {result['resultsFound']} car rentals:")
    for i, car in enumerate(result['cars'][:3], 1):  # Show top 3
        print(f"\n{i}. {car['company']} - {car['model']}")
        print(f"   Type: {car['carType']}")
        print(f"   Pickup: {car['pickupLocation']}")
        print(f"   Dates: {car['pickupDate']} to {car['returnDate']}")
        print(f"   Price: ${car['pricing']['totalCost']} total (${car['pricing']['dailyRate']}/day)")
        print(f"   Passengers: {car['specifications']['passengers']}")

    return result

async def demo_train_search():
    """Demonstrate train search functionality."""
    print("\n\n🚂 Train Search Demo")
    print("=" * 50)

    result = await search_trains(
        from_city="NYC",
        to_city="Boston",
        date="2025-10-01",
        passengers=2
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        if "available_routes" in result:
            print("Available routes:")
            for route in result['available_routes'][:5]:
                print(f"  - {route}")
        return result

    print(f"Found {result['resultsFound']} trains on the {result['route']['operator']} route:")
    for i, train in enumerate(result['trains'][:3], 1):  # Show top 3
        print(f"\n{i}. {train['trainNumber']} - {train['operator']}")
        print(f"   Departure: {train['departure']['time']} from {train['departure']['city']}")
        print(f"   Arrival: {train['arrival']['time']} in {train['arrival']['city']}")
        print(f"   Duration: {train['duration']} ({train['distance']})")

        # Show class options
        for train_class in train['classes']:
            print(f"   {train_class['className']}: ${train_class['totalPrice']} for {train['passengers']} passengers")

    return result

async def demo_itinerary_generation():
    """Demonstrate itinerary generation functionality."""
    print("\n\n📅 Itinerary Generation Demo")
    print("=" * 50)

    result = await generate_itinerary(
        city="Austin",
        days=3,
        interests=["food", "culture", "nature"]
    )

    summary = result['summary']
    print(f"Generated itinerary for {summary['destination']}")
    print(f"Duration: {summary['duration']}")
    print(f"Interests: {', '.join(summary['interests'])}")
    print(f"Estimated budget: ${summary['totalEstimatedBudget']['perPerson']} per person")

    # Show each day's plan
    for day_key, day_data in result['itinerary'].items():
        print(f"\n--- Day {day_data['day']} ({day_data['date']}) ---")
        print(f"Daily budget: ${day_data['dailyBudget']['total']}")

        if day_data['morning']:
            print("\nMorning:")
            for activity in day_data['morning']:
                print(f"  {activity['time']} - {activity['activity']}")

        if day_data['afternoon']:
            print("\nAfternoon:")
            for activity in day_data['afternoon']:
                print(f"  {activity['time']} - {activity['activity']}")

        if day_data['evening']:
            print("\nEvening:")
            for activity in day_data['evening']:
                print(f"  {activity['time']} - {activity['activity']}")

        # Show tips for the day
        if day_data['tips']:
            print(f"\nTips: {', '.join(day_data['tips'])}")

    return result

async def demo_comprehensive_trip():
    """Demonstrate a comprehensive trip planning scenario."""
    print("\n\n🌟 Comprehensive Trip Planning Demo")
    print("=" * 60)

    print("Planning a 3-day trip from Austin to San Francisco...")

    # Step 1: Search for flights
    print("\n1. Searching for flights...")
    flights = await search_flights("AUS", "SFO", "2025-10-01", 2)
    best_flight = min(flights['flights'], key=lambda x: x['price'])
    print(f"   Best flight: {best_flight['airline']} {best_flight['flightNumber']} - ${best_flight['price']}")

    # Step 2: Search for hotels
    print("\n2. Searching for hotels...")
    hotels = await search_hotels("San Francisco", "2025-10-01", 3, 2)
    best_hotel = min(hotels['hotels'], key=lambda x: min(room['pricePerNight'] for room in x['roomTypes']))
    cheapest_room = min(best_hotel['roomTypes'], key=lambda x: x['pricePerNight'])
    print(f"   Best hotel: {best_hotel['hotelName']} - ${cheapest_room['totalPrice']} for 3 nights")

    # Step 3: Search for car rental
    print("\n3. Searching for car rental...")
    cars = await search_cars("San Francisco", "2025-10-01", 3)
    best_car = min(cars['cars'], key=lambda x: x['pricing']['totalCost'])
    print(f"   Best car: {best_car['company']} {best_car['model']} - ${best_car['pricing']['totalCost']}")

    # Step 4: Generate itinerary
    print("\n4. Generating itinerary...")
    itinerary = await generate_itinerary("San Francisco", 3, ["food", "culture", "nature"])
    total_budget = itinerary['summary']['totalEstimatedBudget']['perPerson']
    print(f"   Itinerary created with estimated budget: ${total_budget} per person")

    # Calculate total trip cost
    total_trip_cost = (
        best_flight['pricePerPerson'] +  # Flight per person
        cheapest_room['totalPrice'] / 2 +  # Hotel cost split between 2 people
        best_car['pricing']['totalCost'] / 2 +  # Car cost split between 2 people
        total_budget  # Activities and food per person
    )

    print(f"\n💰 Total estimated trip cost per person: ${total_trip_cost:.2f}")
    print("\nBreakdown:")
    print(f"  Flight: ${best_flight['pricePerPerson']}")
    print(f"  Hotel (3 nights): ${cheapest_room['totalPrice'] / 2:.2f}")
    print(f"  Car rental (3 days): ${best_car['pricing']['totalCost'] / 2:.2f}")
    print(f"  Activities & food: ${total_budget}")

    return {
        "flight": best_flight,
        "hotel": best_hotel,
        "car": best_car,
        "itinerary": itinerary,
        "total_cost": total_trip_cost
    }

async def main():
    """Run all demonstrations."""
    print("🧳 Travel Planner MCP Server - Sample Interactions")
    print("="*60)

    try:
        # Run individual demos
        await demo_flight_search()
        await demo_hotel_search()
        await demo_car_search()
        await demo_train_search()
        await demo_itinerary_generation()

        # Run comprehensive demo
        await demo_comprehensive_trip()

        print("\n\n✅ All demonstrations completed successfully!")
        print("\nNext steps:")
        print("1. Run the MCP server: python server.py")
        print("2. Connect with an MCP client (like Claude Desktop)")
        print("3. Start planning your travels!")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())