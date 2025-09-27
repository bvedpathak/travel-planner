#!/usr/bin/env python3
"""
SOLID-compliant Travel Planner MCP Server.

This server demonstrates proper application of SOLID principles:
- Single Responsibility: Each class has one reason to change
- Open-Closed: Can be extended without modification
- Liskov Substitution: Implementations can be substituted
- Interface Segregation: Clients depend only on interfaces they use
- Dependency Inversion: Depends on abstractions, not concretions
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl

# Import SOLID-compliant modules
from core.interfaces import IToolRegistry
from core.registry import ToolRegistryBuilder
from core.services import (
    DateValidator,
    HotelParameterMapper,
    HotelResponseFormatter,
    HttpApiClient,
    NominatimGeocoder,
    YamlConfigurationLoader,
)
from services.hotel_service import HotelSearchService
from tools_solid.hotel_tool import HotelToolFactory


class TravelPlannerServer:
    """
    Main server class following Single Responsibility Principle.

    This class is responsible only for:
    1. Server lifecycle management
    2. MCP protocol handling
    3. Delegating tool operations to the registry
    """

    def __init__(self, tool_registry: IToolRegistry):
        """
        Initialize server with tool registry (Dependency Inversion).

        Args:
            tool_registry: Registry containing all available tools
        """
        self.tool_registry = tool_registry
        self.server = Server("travel-planner-solid")
        self.logger = self._setup_logging()
        self._setup_handlers()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("travel-planner-solid")

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """
            List available tools from registry.

            This handler delegates to the tool registry, demonstrating
            Single Responsibility and Dependency Inversion principles.
            """
            tools = self.tool_registry.get_all_tools()
            return [tool.get_tool_definition() for tool in tools]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """
            Handle tool execution requests.

            This handler:
            1. Finds the appropriate tool in the registry
            2. Delegates execution to the tool
            3. Formats the response

            Following Open-Closed Principle: new tools can be added
            without modifying this handler.
            """
            try:
                # Find tool in registry
                tool = self.tool_registry.get_tool_by_name(name)
                if not tool:
                    raise ValueError(f"Unknown tool: {name}")

                # Execute tool (Liskov Substitution: any ITravelTool implementation works)
                result = await tool.execute(arguments)

                # Format response based on result success
                if result.success:
                    response_data = {
                        **result.data,
                        "searchTimestamp": result.timestamp,
                        "source": result.source,
                    }
                else:
                    response_data = {"error": result.error, "timestamp": result.timestamp}

                return [types.TextContent(type="text", text=json.dumps(response_data, indent=2))]

            except Exception as e:
                self.logger.error(f"Error executing tool {name}: {str(e)}")
                error_response = {
                    "error": f"Tool execution failed: {str(e)}",
                    "timestamp": result.timestamp if "result" in locals() else None,
                }
                return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]

        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """List available resources."""
            # This would be extended to support resources if needed
            return []

        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """Read resource content."""
            # This would be implemented if resources are needed
            raise ValueError(f"Resource not found: {uri}")

    async def run(self) -> None:
        """Run the MCP server."""
        self.logger.info("Starting SOLID-compliant Travel Planner MCP Server")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="travel-planner-solid",
                    server_version="2.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None, experimental_capabilities={}
                    ),
                ),
            )


class DependencyContainer:
    """
    Dependency injection container following Dependency Inversion Principle.

    This class creates and wires all dependencies, ensuring that
    high-level modules don't depend on low-level modules.
    """

    @staticmethod
    def create_hotel_search_service() -> HotelSearchService:
        """Create hotel search service with all dependencies."""
        # Create low-level dependencies
        config_loader = YamlConfigurationLoader()
        api_client = HttpApiClient()
        geocoder = NominatimGeocoder(api_client)
        formatter = HotelResponseFormatter()
        validator = DateValidator()

        # Create high-level service with injected dependencies
        return HotelSearchService(
            config_loader=config_loader,
            geocoder=geocoder,
            api_client=api_client,
            formatter=formatter,
            validator=validator,
        )

    @staticmethod
    def create_tool_registry() -> IToolRegistry:
        """Create and configure tool registry."""
        # Create services
        hotel_service = DependencyContainer.create_hotel_search_service()
        parameter_mapper = HotelParameterMapper()

        # Create tools using factories
        hotel_tool = HotelToolFactory.create_hotel_tool(hotel_service, parameter_mapper)

        # Build registry (Open-Closed Principle: easy to add new tools)
        registry = ToolRegistryBuilder().add_tool(hotel_tool).build()

        return registry


async def main():
    """Main entry point demonstrating SOLID principles."""
    try:
        # Create dependencies using dependency injection container
        tool_registry = DependencyContainer.create_tool_registry()

        # Create server with injected dependencies
        server = TravelPlannerServer(tool_registry)

        # Run server
        await server.run()

    except Exception as e:
        logging.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
