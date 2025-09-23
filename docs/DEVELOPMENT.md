# Development Guide

## Setting Up the Development Environment

### Prerequisites

- **Python**: 3.10 or higher
- **pip**: Latest version
- **Git**: For version control
- **Claude Desktop**: For MCP client testing

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/bvedpathak/travel-planner.git
cd travel-planner

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"

# Verify installation
python server.py --help
```

### Configuration

1. **Create config.yaml** (required for live APIs):
```yaml
flight_api:
  rapidapi:
    key: "your-rapidapi-key-here"
    host: "booking-com.p.rapidapi.com"
    base_url: "https://booking-com.p.rapidapi.com/v1/flights"

car_api:
  rapidapi:
    key: "your-rapidapi-key-here"
    host: "booking-com.p.rapidapi.com"
    base_url: "https://booking-com.p.rapidapi.com/v1/car-rentals"
```

2. **Get RapidAPI Keys**:
   - Sign up at [RapidAPI](https://rapidapi.com/)
   - Subscribe to [Booking.com API](https://rapidapi.com/DataCrawler/api/booking-com)
   - Copy your API key to config.yaml

3. **Environment Variables** (optional):
```bash
export LOG_LEVEL=DEBUG
export TRAVEL_DATA_DIR=/path/to/custom/data
```

## Project Structure

```
travel-planner/
├── server.py                 # Main MCP server
├── server_simple.py          # Simplified version
├── config.yaml              # API configuration
├── tools/                   # Tool implementations
│   ├── __init__.py
│   ├── search_flights.py    # Live flight search
│   ├── search_cars.py       # Live car rental search
│   ├── search_hotels.py     # Mock hotel search
│   ├── search_trains.py     # Mock train search
│   └── generate_itinerary.py # Mock itinerary generation
├── resources/               # Static resources
│   └── travel_guides/       # City travel guides
├── docs/                    # Documentation
│   ├── API.md              # API documentation
│   └── DEVELOPMENT.md      # This file
├── tests/                   # Test files
├── examples/                # Usage examples
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md              # Main documentation
```

## Development Workflow

### Running the Server

```bash
# Development mode
python server.py

# With debug logging
LOG_LEVEL=DEBUG python server.py

# Simple version (fewer features)
python server_simple.py
```

### Testing with Claude Desktop

1. **Configure Claude Desktop**:
```json
{
  "mcpServers": {
    "travel-planner": {
      "command": "python",
      "args": ["/absolute/path/to/travel-planner/server.py"]
    }
  }
}
```

2. **Test Commands**:
```
Search for flights from Mumbai to Delhi on October 1st
Find hotels in Austin for 3 nights starting October 1st
Generate a 3-day itinerary for Austin focusing on food and culture
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=tools --cov=server

# Run specific test file
pytest tests/test_flights.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Install code quality tools
pip install black isort flake8 mypy

# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .

# All quality checks
black . && isort . && flake8 . && mypy .
```

## Adding New Features

### Adding a New Tool

1. **Create tool module** in `tools/`:
```python
# tools/search_activities.py
async def search_activities(city: str, activity_type: str) -> dict:
    """Search for activities in a city."""
    # Implementation here
    pass
```

2. **Register tool** in `server.py`:
```python
from tools.search_activities import search_activities

# Add to handle_list_tools()
types.Tool(
    name="searchActivities",
    description="Search for activities in a city",
    inputSchema={
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "activity_type": {"type": "string"}
        },
        "required": ["city"]
    }
)

# Add to handle_call_tool()
elif name == "searchActivities":
    result = await search_activities(**arguments)
```

3. **Write tests**:
```python
# tests/test_activities.py
import pytest
from tools.search_activities import search_activities

@pytest.mark.asyncio
async def test_search_activities():
    result = await search_activities("Austin", "outdoor")
    assert "activities" in result
```

### Adding a New City

1. **Add to hotel data** in `tools/search_hotels.py`:
```python
HOTELS_BY_CITY["Portland"] = [
    {"name": "Portland Downtown Hotel", "category": "business", "rating": 4.2}
]

LOCATIONS["Portland"] = ["Downtown", "Pearl District", "Hawthorne"]
```

2. **Create travel guide** in `resources/travel_guides/portland.json`:
```json
{
  "city": "Portland",
  "state": "Oregon",
  "description": "Keep Portland weird...",
  "attractions": [...]
}
```

3. **Update itinerary data** in `tools/generate_itinerary.py`:
```python
CITY_DATA["Portland"] = {
    "attractions": [...],
    "restaurants": [...],
    "activities": [...]
}
```

### Integrating Real APIs

Replace mock functions with real API calls:

```python
# Before (mock)
def generate_mock_hotels():
    return {...}

# After (real API)
async def search_hotels_api(city: str) -> dict:
    async with aiohttp.ClientSession() as session:
        url = f"https://api.example.com/hotels"
        params = {"city": city}
        async with session.get(url, params=params) as response:
            return await response.json()
```

## Debugging

### Common Issues

1. **Import Errors**:
   - Ensure virtual environment is activated
   - Check Python path: `python -c "import sys; print(sys.path)"`

2. **API Errors**:
   - Verify config.yaml exists and has valid keys
   - Check API quotas and rate limits
   - Enable debug logging: `LOG_LEVEL=DEBUG`

3. **MCP Connection Issues**:
   - Use absolute paths in Claude Desktop config
   - Check server starts without errors: `python server.py`
   - Restart Claude Desktop after config changes

### Debug Logging

```python
import logging
logger = logging.getLogger(__name__)

# Add debug statements
logger.debug(f"Searching for flights: {from_id} -> {to_id}")
logger.info(f"Found {len(results)} flight results")
logger.warning(f"API rate limit approaching")
logger.error(f"API request failed: {error}")
```

### Testing Individual Tools

```python
# Test flight search directly
import asyncio
from tools.search_flights import search_flights

async def test():
    result = await search_flights("BOM.AIRPORT", "DEL.AIRPORT", "2025-10-01")
    print(result)

asyncio.run(test())
```

## Performance Optimization

### API Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_flights(from_id, to_id, date):
    # Cache flight results for 1 hour
    pass
```

### Async Best Practices

```python
# Good: Use aiohttp for HTTP requests
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()

# Good: Concurrent API calls
flight_task = search_flights(...)
hotel_task = search_hotels(...)
flights, hotels = await asyncio.gather(flight_task, hotel_task)
```

## Deployment

### Production Configuration

```yaml
# config.prod.yaml
flight_api:
  rapidapi:
    key: "${RAPIDAPI_KEY}"  # Use environment variable
    timeout: 30
    retry_attempts: 3

logging:
  level: "INFO"
  file: "/var/log/travel-planner.log"
```

### Environment Variables

```bash
export RAPIDAPI_KEY="your-production-key"
export LOG_LEVEL="INFO"
export ENVIRONMENT="production"
```

### Health Checks

```python
# Add health check endpoint
@server.list_tools()
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

## Contributing

### Code Style

- **Formatting**: Black with 100 character line length
- **Imports**: isort with black profile
- **Docstrings**: Google style with type hints
- **Type Hints**: Required for all public functions

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run quality checks: `black . && isort . && flake8 . && pytest`
5. Commit with descriptive message
6. Push and create pull request

### Documentation

- Update API.md for new endpoints
- Add docstrings for all functions
- Include examples in README
- Update this development guide for new setup steps

## Troubleshooting

### Common Development Issues

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Activate virtual environment, install dependencies |
| API key errors | Check config.yaml format and valid keys |
| MCP connection fails | Use absolute paths, restart Claude Desktop |
| Tests fail | Check test data, ensure async/await patterns |
| Type errors | Add proper type hints, run mypy |

### Getting Help

- **GitHub Issues**: Report bugs and ask questions
- **Documentation**: Check API.md and README.md
- **Code Examples**: See examples/ directory
- **Logs**: Enable debug logging for detailed output

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.