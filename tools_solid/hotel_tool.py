"""
Hotel search tool implementation following SOLID principles.

This tool implementation follows:
- Single Responsibility: Only handles hotel search tool operations
- Open-Closed: Can be extended without modification
- Dependency Inversion: Depends on abstractions, not concretions
"""

import json
from typing import Dict, Any
import mcp.types as types
from core.interfaces import ITravelTool, ISearchService, IParameterMapper, SearchResult, HotelSearchCriteria


class HotelSearchTool(ITravelTool):
    """
    Hotel search tool following SOLID principles.

    This tool is responsible only for:
    1. Defining the MCP tool schema
    2. Mapping parameters
    3. Delegating search to the service
    4. Formatting the final response
    """

    def __init__(self, search_service: ISearchService, parameter_mapper: IParameterMapper):
        """Initialize with injected dependencies."""
        self.search_service = search_service
        self.parameter_mapper = parameter_mapper
        self._name = "searchHotels"

    def get_name(self) -> str:
        """Get the tool name."""
        return self._name

    def get_tool_definition(self) -> types.Tool:
        """
        Get the MCP tool definition.

        This method defines the tool schema that clients will see.
        Following Interface Segregation Principle by providing only
        the necessary interface for this specific tool.
        """
        return types.Tool(
            name=self._name,
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
                    },
                    # Backward compatibility fields
                    "city": {
                        "type": "string",
                        "description": "City name (legacy parameter, use 'location' instead)"
                    },
                    "checkIn": {
                        "type": "string",
                        "description": "Check-in date (legacy parameter, use 'arrival_date' instead)"
                    },
                    "nights": {
                        "type": "integer",
                        "description": "Number of nights (legacy parameter, use 'departure_date' instead)"
                    },
                    "guests": {
                        "type": "integer",
                        "description": "Number of guests (legacy parameter, use 'adults' instead)"
                    }
                },
                "required": ["location", "arrival_date", "departure_date"],
                "anyOf": [
                    {"required": ["location", "arrival_date", "departure_date"]},
                    {"required": ["city", "checkIn", "nights"]}
                ]
            }
        )

    async def execute(self, arguments: Dict[str, Any]) -> SearchResult:
        """
        Execute the hotel search tool.

        This method:
        1. Maps input parameters (supporting backward compatibility)
        2. Creates search criteria
        3. Delegates to the search service
        4. Returns the result
        """
        try:
            # Step 1: Map parameters (handles backward compatibility)
            mapped_params = self.parameter_mapper.map_parameters(arguments)

            # Step 2: Validate required parameters
            if not mapped_params.get("location"):
                return SearchResult(
                    success=False,
                    data={},
                    error="Missing required parameter: location"
                )

            if not mapped_params.get("arrival_date") or not mapped_params.get("departure_date"):
                return SearchResult(
                    success=False,
                    data={},
                    error="Missing required parameters: arrival_date and departure_date"
                )

            # Step 3: Create search criteria
            criteria = HotelSearchCriteria(
                location=mapped_params["location"],
                arrival_date=mapped_params["arrival_date"],
                departure_date=mapped_params["departure_date"],
                adults=mapped_params.get("adults", 1),
                children_age=mapped_params.get("children_age", ""),
                room_qty=mapped_params.get("room_qty", 1),
                currency_code=mapped_params.get("currency_code", "USD"),
                languagecode=mapped_params.get("languagecode", "en-us")
            )

            # Step 4: Delegate to search service
            result = await self.search_service.search(criteria)

            return result

        except Exception as e:
            return SearchResult(
                success=False,
                data={},
                error=f"Tool execution error: {str(e)}"
            )


class HotelToolFactory:
    """
    Factory for creating hotel tools with proper dependency injection.

    This follows the Factory pattern and Dependency Inversion Principle
    by creating tools with all their required dependencies.
    """

    @staticmethod
    def create_hotel_tool(
        search_service: ISearchService,
        parameter_mapper: IParameterMapper
    ) -> ITravelTool:
        """Create a hotel search tool with injected dependencies."""
        return HotelSearchTool(search_service, parameter_mapper)