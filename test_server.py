#!/usr/bin/env python3
"""
Quick test script to verify the MCP server can start and import correctly.
"""

import sys
import importlib.util

def test_imports():
    """Test that all required modules can be imported."""
    try:
        # Test MCP imports
        import mcp.types
        import mcp.server.stdio
        from mcp.server.models import InitializationOptions
        from mcp.server import Server
        print("✅ MCP imports successful")

        # Test pydantic
        from pydantic import AnyUrl
        print("✅ Pydantic imports successful")

        # Test tool imports
        from tools.search_flights import search_flights
        from tools.search_hotels import search_hotels
        from tools.search_cars import search_cars
        from tools.search_trains import search_trains
        from tools.generate_itinerary import generate_itinerary
        print("✅ Tool imports successful")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_server_creation():
    """Test that the server can be created."""
    try:
        from mcp.server import Server
        server = Server("test-travel-planner")
        print("✅ Server creation successful")
        return True
    except Exception as e:
        print(f"❌ Server creation error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Travel Planner MCP Server Setup")
    print("=" * 50)

    success = True

    success &= test_imports()
    success &= test_server_creation()

    if success:
        print("\n🎉 All tests passed! The server is ready to run.")
        print("\nTo start the server, run: python server.py")
    else:
        print("\n❌ Some tests failed. Please check your installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()