#!/usr/bin/env python3
"""
Simplified Travel Planner MCP Server for better compatibility with Claude AI
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

import mcp.types as types
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from mcp.server import Server

from tools.search_flights import search_flights
from tools.search_hotels import search_hotels
from tools.search_cars import search_cars
from tools.search_trains import search_trains
from tools.generate_itinerary import generate_itinerary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("travel-planner")

# Initialize the MCP server
server = Server("travel-planner")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools that clients can call."""
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
            description="Search for hotels in a city for specific dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'Austin', 'San Francisco')"
                    },
                    "checkIn": {
                        "type": "string",
                        "description": "Check-in date in YYYY-MM-DD format"
                    },
                    "nights": {
                        "type": "integer",
                        "description": "Number of nights to stay"
                    },
                    "guests": {
                        "type": "integer",
                        "description": "Number of guests (default: 2)",
                        "default": 2
                    }
                },
                "required": ["city", "checkIn", "nights"]
            }
        ),
        types.Tool(
            name="searchCars",
            description="Search for rental cars in a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name for car pickup"
                    },
                    "pickupDate": {
                        "type": "string",
                        "description": "Pickup date in YYYY-MM-DD format"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of rental days"
                    },
                    "carType": {
                        "type": "string",
                        "description": "Preferred car type (economy, compact, midsize, suv)",
                        "enum": ["economy", "compact", "midsize", "suv"]
                    }
                },
                "required": ["city", "pickupDate", "days"]
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
    """Handle tool execution requests."""
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
                city=arguments["city"],
                pickup_date=arguments["pickupDate"],
                days=arguments["days"],
                car_type=arguments.get("carType")
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

async def main():
    """Main entry point for the MCP server."""
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