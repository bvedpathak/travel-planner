"""
Core interfaces for the Travel Planner application following SOLID principles.

This module defines the abstractions that concrete implementations must follow,
enabling dependency inversion and loose coupling.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import mcp.types as types


@dataclass
class SearchCriteria:
    """Base class for search criteria."""
    pass


@dataclass
class SearchResult:
    """Base class for search results."""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    timestamp: Optional[str] = None
    source: Optional[str] = None


# ISP: Interface Segregation - Separate interfaces for different capabilities
class IConfigurationLoader(ABC):
    """Interface for loading configuration data."""

    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from source."""
        pass


class IGeocoder(ABC):
    """Interface for geocoding services."""

    @abstractmethod
    async def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get latitude and longitude for a location."""
        pass


class IApiClient(ABC):
    """Interface for API clients."""

    @abstractmethod
    async def make_request(self, url: str, params: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        """Make an HTTP request to an API."""
        pass


class IDataFormatter(ABC):
    """Interface for formatting API response data."""

    @abstractmethod
    def format_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw API response to standardized structure."""
        pass


class ISearchService(ABC):
    """Base interface for search services."""

    @abstractmethod
    async def search(self, criteria: SearchCriteria) -> SearchResult:
        """Perform a search based on criteria."""
        pass


class ITravelTool(ABC):
    """Interface for travel tools following SRP."""

    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """Get the MCP tool definition."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> SearchResult:
        """Execute the tool with given arguments."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the tool name."""
        pass


class IToolRegistry(ABC):
    """Interface for tool registry following OCP."""

    @abstractmethod
    def register_tool(self, tool: ITravelTool) -> None:
        """Register a new tool."""
        pass

    @abstractmethod
    def get_all_tools(self) -> List[ITravelTool]:
        """Get all registered tools."""
        pass

    @abstractmethod
    def get_tool_by_name(self, name: str) -> Optional[ITravelTool]:
        """Get a tool by its name."""
        pass


class IParameterMapper(ABC):
    """Interface for parameter mapping and validation."""

    @abstractmethod
    def map_parameters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Map and validate parameters."""
        pass


class IValidator(ABC):
    """Interface for data validation."""

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate data and return success status with optional error message."""
        pass


# Specific search criteria classes
@dataclass
class HotelSearchCriteria(SearchCriteria):
    """Hotel search criteria."""
    location: str
    arrival_date: str
    departure_date: str
    adults: int = 1
    children_age: str = ""
    room_qty: int = 1
    currency_code: str = "USD"
    languagecode: str = "en-us"


@dataclass
class FlightSearchCriteria(SearchCriteria):
    """Flight search criteria."""
    from_id: str
    to_id: str
    depart_date: str
    return_date: Optional[str] = None
    adults: int = 1
    children: int = 0
    stops: str = "none"
    cabin_class: str = "ECONOMY"
    currency_code: str = "USD"