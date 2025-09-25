#!/usr/bin/env python3
"""
Travel Planner MCP Server

An MCP (Model Context Protocol) server that provides travel planning tools including:
- Flight search
- Hotel search
- Car rental search
- Train search
- Itinerary generation

This server demonstrates key MCP concepts:
- Tools (capabilities)
- Resources (static data)
- Structured responses
- Tool execution
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

import mcp.types as types
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from mcp.server import Server
from pydantic import AnyUrl

from tools.search_flights import search_flights
from tools.search_hotels import search_hotels
from tools.search_cars import search_cars
from tools.search_trains import search_trains
from tools.generate_itinerary import generate_itinerary

# Configure logging for development and production monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("travel-planner")

# Initialize the MCP server with travel-planner identifier
server = Server("travel-planner")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools that clients can call.

    Returns all travel planning tools with their schemas.
    """
    return [
        types.Tool(
            name="searchFlights",
            description="Search for flights between two cities using live Booking.com API",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_id": {
                        "type": "string",
                        "description": "Departure airport ID (e.g., 'BOM.AIRPORT', 'LON.AIRPORT')"
                    },
                    "to_id": {
                        "type": "string",
                        "description": "Arrival airport ID (e.g., 'DEL.AIRPORT', 'NYC.AIRPORT')"
                    },
                    "depart_date": {
                        "type": "string",
                        "description": "Departure date in YYYY-MM-DD format"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "Return date in YYYY-MM-DD format (optional for round trip)"
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adult passengers (default: 1)",
                        "default": 1
                    },
                    "children": {
                        "type": "integer",
                        "description": "Number of child passengers (default: 0)",
                        "default": 0
                    },
                    "stops": {
                        "type": "string",
                        "description": "Number of stops: 'none', 'one', 'any' (default: 'none')",
                        "enum": ["none", "one", "any"],
                        "default": "none"
                    },
                    "cabin_class": {
                        "type": "string",
                        "description": "Cabin class (default: 'ECONOMY')",
                        "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
                        "default": "ECONOMY"
                    },
                    "currency_code": {
                        "type": "string",
                        "description": "Currency code (default: 'USD')",
                        "default": "USD"
                    }
                },
                "required": ["from_id", "to_id", "depart_date"]
            }
        ),
        types.Tool(
            name="searchHotels",
            description="Search for hotels in a location using live Booking.com API",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or location name (e.g., 'Austin', 'San Francisco', 'New York')"
                    },
                    "arrival_date": {
                        "type": "string",
                        "description": "Check-in date in YYYY-MM-DD format"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "Check-out date in YYYY-MM-DD format"
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adult guests (default: 1)",
                        "default": 1
                    },
                    "children_age": {
                        "type": "string",
                        "description": "Ages of children separated by comma (e.g., '0,17')",
                        "default": ""
                    },
                    "room_qty": {
                        "type": "integer",
                        "description": "Number of rooms required (default: 1)",
                        "default": 1
                    },
                    "currency_code": {
                        "type": "string",
                        "description": "Currency code (default: 'USD')",
                        "default": "USD"
                    },
                    "languagecode": {
                        "type": "string",
                        "description": "Language code (default: 'en-us')",
                        "default": "en-us"
                    }
                },
                "required": ["location", "arrival_date", "departure_date"]
            }
        ),
        types.Tool(
            name="searchCars",
            description="Search for rental cars using coordinates and dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "pick_up_latitude": {
                        "type": "number",
                        "description": "Latitude for pickup location"
                    },
                    "pick_up_longitude": {
                        "type": "number",
                        "description": "Longitude for pickup location"
                    },
                    "drop_off_latitude": {
                        "type": "number",
                        "description": "Latitude for drop-off location"
                    },
                    "drop_off_longitude": {
                        "type": "number",
                        "description": "Longitude for drop-off location"
                    },
                    "pick_up_date": {
                        "type": "string",
                        "description": "Pickup date in YYYY-MM-DD format"
                    },
                    "drop_off_date": {
                        "type": "string",
                        "description": "Drop-off date in YYYY-MM-DD format"
                    },
                    "pick_up_time": {
                        "type": "string",
                        "description": "Pickup time in HH:MM format (default: 10:00)",
                        "default": "10:00"
                    },
                    "drop_off_time": {
                        "type": "string",
                        "description": "Drop-off time in HH:MM format (default: 10:00)",
                        "default": "10:00"
                    },
                    "driver_age": {
                        "type": "integer",
                        "description": "Driver age (default: 30)",
                        "default": 30
                    },
                    "currency_code": {
                        "type": "string",
                        "description": "Currency code (default: USD)",
                        "default": "USD"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location code (default: US)",
                        "default": "US"
                    }
                },
                "required": ["pick_up_latitude", "pick_up_longitude", "drop_off_latitude", "drop_off_longitude", "pick_up_date", "drop_off_date"]
            }
        ),
        types.Tool(
            name="searchTrains",
            description="Search for train routes between two cities",
            inputSchema={
                "type": "object",
                "properties": {
                    "from": {
                        "type": "string",
                        "description": "Departure city (e.g., 'NYC', 'Boston')"
                    },
                    "to": {
                        "type": "string",
                        "description": "Arrival city"
                    },
                    "date": {
                        "type": "string",
                        "description": "Travel date in YYYY-MM-DD format"
                    },
                    "passengers": {
                        "type": "integer",
                        "description": "Number of passengers (default: 1)",
                        "default": 1
                    }
                },
                "required": ["from", "to", "date"]
            }
        ),
        types.Tool(
            name="generateItinerary",
            description="Generate a detailed travel itinerary for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Destination city"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days (1-7)",
                        "minimum": 1,
                        "maximum": 7
                    },
                    "interests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas of interest (food, culture, nature, nightlife, shopping)"
                    }
                },
                "required": ["city", "days"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle tool execution requests.

    Routes tool calls to appropriate handler functions and returns structured responses.
    """
    try:
        if name == "searchFlights":
            result = await search_flights(
                from_id=arguments["from_id"],
                to_id=arguments["to_id"],
                depart_date=arguments["depart_date"],
                return_date=arguments.get("return_date"),
                adults=arguments.get("adults", 1),
                children=arguments.get("children", 0),
                stops=arguments.get("stops", "none"),
                cabin_class=arguments.get("cabin_class", "ECONOMY"),
                currency_code=arguments.get("currency_code", "USD")
            )
        elif name == "searchHotels":
            result = await search_hotels(
                city=arguments["city"],
                check_in=arguments["checkIn"],
                nights=arguments["nights"],
                guests=arguments.get("guests", 2)
            )
        elif name == "searchCars":
            result = await search_cars(
                pick_up_latitude=arguments["pick_up_latitude"],
                pick_up_longitude=arguments["pick_up_longitude"],
                drop_off_latitude=arguments["drop_off_latitude"],
                drop_off_longitude=arguments["drop_off_longitude"],
                pick_up_date=arguments["pick_up_date"],
                drop_off_date=arguments["drop_off_date"],
                pick_up_time=arguments.get("pick_up_time", "10:00"),
                drop_off_time=arguments.get("drop_off_time", "10:00"),
                driver_age=arguments.get("driver_age", 30),
                currency_code=arguments.get("currency_code", "USD"),
                location=arguments.get("location", "US")
            )
        elif name == "searchTrains":
            result = await search_trains(
                from_city=arguments["from"],
                to_city=arguments["to"],
                date=arguments["date"],
                passengers=arguments.get("passengers", 1)
            )
        elif name == "generateItinerary":
            result = await generate_itinerary(
                city=arguments["city"],
                days=arguments["days"],
                interests=arguments.get("interests", [])
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    List available resources (static travel guides).

    Resources demonstrate MCP's capability to expose static data.
    """
    return [
        types.Resource(
            uri=AnyUrl("file://resources/travel_guides/austin.json"),
            name="Austin Travel Guide",
            description="Comprehensive travel guide for Austin, Texas",
            mimeType="application/json"
        ),
        types.Resource(
            uri=AnyUrl("file://resources/travel_guides/san_francisco.json"),
            name="San Francisco Travel Guide",
            description="Comprehensive travel guide for San Francisco, California",
            mimeType="application/json"
        ),
        types.Resource(
            uri=AnyUrl("file://resources/travel_guides/new_york.json"),
            name="New York Travel Guide",
            description="Comprehensive travel guide for New York City",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read and return resource content.

    Loads travel guide JSON files from the resources directory.
    """
    try:
        # Extract filename from URI
        filename = str(uri).replace("file://resources/travel_guides/", "")
        filepath = f"resources/travel_guides/{filename}"

        with open(filepath, 'r') as f:
            return f.read()

    except FileNotFoundError:
        raise ValueError(f"Resource not found: {uri}")
    except Exception as e:
        raise ValueError(f"Error reading resource: {str(e)}")

async def main():
    """
    Main entry point for the MCP server.
    """
    logger.info("Starting Travel Planner MCP Server...")

    # Server configuration
    options = InitializationOptions(
        server_name="travel-planner",
        server_version="1.0.0",
        capabilities=types.ServerCapabilities(
            tools={},
            resources={}
        )
    )

    # Start the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    asyncio.run(main())