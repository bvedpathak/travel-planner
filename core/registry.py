"""
Tool registry implementation following Open-Closed Principle.

This module provides a registry system that allows adding new tools
without modifying existing code, demonstrating the Open-Closed Principle.
"""

from typing import Dict, List, Optional

from core.interfaces import IToolRegistry, ITravelTool


class TravelToolRegistry(IToolRegistry):
    """
    Tool registry following Open-Closed Principle.

    This registry allows adding new tools without modifying existing code.
    New tools can be registered at runtime, making the system extensible
    without modification.
    """

    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, ITravelTool] = {}

    def register_tool(self, tool: ITravelTool) -> None:
        """
        Register a new tool.

        This method allows extending the system with new tools
        without modifying existing code (Open-Closed Principle).

        Args:
            tool: Tool implementing ITravelTool interface
        """
        if not isinstance(tool, ITravelTool):
            raise TypeError("Tool must implement ITravelTool interface")

        tool_name = tool.get_name()
        if tool_name in self._tools:
            raise ValueError(f"Tool '{tool_name}' is already registered")

        self._tools[tool_name] = tool

    def get_all_tools(self) -> List[ITravelTool]:
        """
        Get all registered tools.

        Returns:
            List of all registered tools
        """
        return list(self._tools.values())

    def get_tool_by_name(self, name: str) -> Optional[ITravelTool]:
        """
        Get a tool by its name.

        Args:
            name: Name of the tool to retrieve

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool by name.

        Args:
            name: Name of the tool to unregister

        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get_tool_names(self) -> List[str]:
        """
        Get names of all registered tools.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def tool_exists(self, name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            name: Name of the tool to check

        Returns:
            True if tool exists, False otherwise
        """
        return name in self._tools


class ToolRegistryBuilder:
    """
    Builder for creating and configuring tool registries.

    This class helps create tool registries with proper dependency injection,
    following the Builder pattern and making it easy to set up complex
    tool configurations.
    """

    def __init__(self):
        """Initialize empty registry builder."""
        self.registry = TravelToolRegistry()

    def add_tool(self, tool: ITravelTool) -> "ToolRegistryBuilder":
        """
        Add a tool to the registry.

        Args:
            tool: Tool to add

        Returns:
            Self for method chaining
        """
        self.registry.register_tool(tool)
        return self

    def build(self) -> IToolRegistry:
        """
        Build and return the configured registry.

        Returns:
            Configured tool registry
        """
        return self.registry
