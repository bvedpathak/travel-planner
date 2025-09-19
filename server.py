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
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl

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
    """
    List available tools that clients can call.

    Returns all travel planning tools with their schemas.
    """
    return [
        types.Tool(
            name="searchFlights",
            description="Search for flights between two cities on a specific date",
            inputSchema={
                "type": "object",
                "properties": {
                    "from": {
                        "type": "string",
                        "description": "Departure airport code (e.g., 'AUS', 'SFO')"
                    },
                    "to": {
                        "type": "string",
                        "description": "Arrival airport code (e.g., 'SFO', 'NYC')"
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
    """
    Handle tool execution requests.

    Routes tool calls to appropriate handler functions and returns structured responses.
    """
    try:
        if name == "searchFlights":
            result = await search_flights(
                from_city=arguments["from"],
                to_city=arguments["to"],
                date=arguments["date"],
                passengers=arguments.get("passengers", 1)
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