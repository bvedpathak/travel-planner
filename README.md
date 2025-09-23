# Travel Planner MCP Server

A comprehensive **Model Context Protocol (MCP)** server that provides travel planning tools including flight search, hotel booking, car rentals, train routes, and itinerary generation. This project demonstrates key MCP concepts while offering practical travel planning functionality.

## 🌟 What is MCP?

The [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/specification) is an open standard that enables AI assistants to securely connect to external data sources and tools. MCP provides:

- **Standardized Integration**: Consistent way for AI models to interact with external services
- **Security**: Controlled access to resources and capabilities
- **Extensibility**: Easy to add new tools and data sources
- **Interoperability**: Works across different AI platforms and models

## 🎯 What This Project Demonstrates

This Travel Planner server showcases the core MCP concepts:

### 1. **Tools (Capabilities)**
- `searchFlights` - Find flights between cities
- `searchHotels` - Search accommodations
- `searchCars` - Find rental cars
- `searchTrains` - Search train routes
- `generateItinerary` - Create detailed travel plans

### 2. **Resources**
- Static travel guides for major cities (Austin, San Francisco, New York)
- Structured JSON data accessible via the MCP resource system

### 3. **Structured Responses**
- Consistent JSON schemas for all travel data
- Standardized format across different service types
- Rich metadata including pricing, timing, and availability

### 4. **Tool Execution**
- Async tool handlers with proper error handling
- Mock data that simulates real API responses
- Extensible design for real API integration

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/travel-planner.git
   cd travel-planner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   python server.py
   ```

The server will start and listen for MCP client connections via stdio.

### Using with Claude Desktop

1. Add to your Claude Desktop configuration (`~/AppData/Roaming/Claude/claude_desktop_config.json` on Windows or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "travel-planner": {
      "command": "python",
      "args": ["/path/to/travel-planner/server.py"]
    }
  }
}
```

2. Restart Claude Desktop
3. Start planning your travels!

## 📚 API Examples

### Flight Search

**Request:**
```json
{
  "tool": "searchFlights",
  "params": {
    "from": "AUS",
    "to": "SFO",
    "date": "2025-10-01",
    "passengers": 2
  }
}
```

**Response:**
```json
{
  "searchCriteria": {
    "from": "AUS",
    "to": "SFO",
    "date": "2025-10-01",
    "passengers": 2
  },
  "resultsFound": 5,
  "flights": [
    {
      "flightNumber": "UA1234",
      "airline": "United Airlines",
      "departure": {
        "airport": "AUS",
        "airportName": "Austin-Bergstrom International",
        "city": "Austin",
        "time": "07:00",
        "date": "2025-10-01"
      },
      "arrival": {
        "airport": "SFO",
        "airportName": "San Francisco International",
        "city": "San Francisco",
        "time": "09:30",
        "date": "2025-10-01"
      },
      "duration": "4h 30m",
      "price": 500,
      "pricePerPerson": 250,
      "bookingClass": "Economy",
      "passengers": 2,
      "stops": 0,
      "aircraft": "Boeing 737"
    }
  ]
}
```

### Hotel Search

**Request:**
```json
{
  "tool": "searchHotels",
  "params": {
    "city": "Austin",
    "checkIn": "2025-10-01",
    "nights": 3,
    "guests": 2
  }
}
```

**Response:**
```json
{
  "searchCriteria": {
    "city": "Austin",
    "checkIn": "2025-10-01",
    "checkOut": "2025-10-04",
    "nights": 3,
    "guests": 2
  },
  "resultsFound": 8,
  "hotels": [
    {
      "hotelName": "Austin Downtown Suites",
      "location": "Downtown",
      "city": "Austin",
      "rating": 4.5,
      "category": "Luxury",
      "checkIn": "2025-10-01",
      "checkOut": "2025-10-04",
      "nights": 3,
      "guests": 2,
      "roomTypes": [
        {
          "type": "Standard Room",
          "pricePerNight": 180,
          "totalPrice": 540,
          "bedsDescription": "1 Queen Bed",
          "maxOccupancy": 2,
          "roomSize": "300 sq ft"
        }
      ],
      "amenities": ["Free WiFi", "Swimming Pool", "Fitness Center", "Restaurant"],
      "policies": {
        "checkInTime": "3:00 PM",
        "checkOutTime": "11:00 AM",
        "cancellation": "Free cancellation until 24 hours before check-in"
      }
    }
  ]
}
```

### Car Rental Search

**Request:**
```json
{
  "tool": "searchCars",
  "params": {
    "city": "Austin",
    "pickupDate": "2025-10-01",
    "days": 3,
    "carType": "suv"
  }
}
```

**Response:**
```json
{
  "searchCriteria": {
    "city": "Austin",
    "pickupDate": "2025-10-01",
    "returnDate": "2025-10-04",
    "days": 3,
    "carType": "suv"
  },
  "resultsFound": 6,
  "cars": [
    {
      "company": "Hertz",
      "carType": "Suv",
      "model": "Toyota RAV4",
      "pickupLocation": "Austin Airport",
      "city": "Austin",
      "pickupDate": "2025-10-01",
      "returnDate": "2025-10-04",
      "rentalDays": 3,
      "pricing": {
        "dailyRate": 75,
        "subtotal": 225,
        "taxesAndFees": 45,
        "totalCost": 270
      },
      "specifications": {
        "passengers": "7-8",
        "luggage": "4-6 bags",
        "doors": "4",
        "transmission": "Automatic",
        "fuelType": "Gasoline",
        "mpg": "22-28"
      },
      "features": ["Air Conditioning", "GPS Navigation", "Bluetooth", "Backup Camera"],
      "policies": {
        "minimumAge": 25,
        "mileage": "Unlimited mileage",
        "fuelPolicy": "Full to Full"
      }
    }
  ]
}
```

### Train Search

**Request:**
```json
{
  "tool": "searchTrains",
  "params": {
    "from": "NYC",
    "to": "Boston",
    "date": "2025-10-01",
    "passengers": 2
  }
}
```

**Response:**
```json
{
  "searchCriteria": {
    "from": "NYC",
    "to": "Boston",
    "date": "2025-10-01",
    "passengers": 2
  },
  "route": {
    "operator": "Amtrak Northeast Regional",
    "distance": "230 miles",
    "averageDuration": "4h 0m"
  },
  "resultsFound": 6,
  "trains": [
    {
      "trainNumber": "NE101",
      "operator": "Amtrak Northeast Regional",
      "departure": {
        "city": "NYC",
        "time": "08:00",
        "date": "2025-10-01",
        "station": "NYC Union Station"
      },
      "arrival": {
        "city": "Boston",
        "time": "11:45",
        "date": "2025-10-01",
        "station": "Boston Union Station"
      },
      "duration": "3h45m",
      "distance": "230 miles",
      "passengers": 2,
      "classes": [
        {
          "className": "Coach",
          "pricePerPerson": 120,
          "totalPrice": 240,
          "amenities": ["Comfortable seating", "WiFi", "Power outlets"]
        },
        {
          "className": "Business Class",
          "pricePerPerson": 192,
          "totalPrice": 384,
          "amenities": ["Extra legroom", "WiFi", "Complimentary drinks"]
        }
      ]
    }
  ]
}
```

### Itinerary Generation

**Request:**
```json
{
  "tool": "generateItinerary",
  "params": {
    "city": "Austin",
    "days": 3,
    "interests": ["food", "culture", "nature"]
  }
}
```

**Response:**
```json
{
  "summary": {
    "destination": "Austin",
    "duration": "3 days",
    "interests": ["food", "culture", "nature"],
    "totalEstimatedBudget": {
      "perPerson": 375,
      "breakdown": {
        "food": 180,
        "attractions": 45,
        "activities": 75,
        "transportation": 75
      }
    },
    "bestTimeToVisit": "March-May and September-November (avoid summer heat)",
    "packingTips": ["Light, breathable clothing", "Comfortable walking shoes", "Sunscreen and hat"]
  },
  "itinerary": {
    "day1": {
      "day": 1,
      "date": "2025-10-01",
      "morning": [
        {
          "time": "8:00 AM",
          "activity": "Breakfast at Paperboy",
          "type": "food",
          "cuisine": "Breakfast",
          "price": "$$"
        },
        {
          "time": "9:00 AM",
          "activity": "Texas State Capitol",
          "type": "culture",
          "duration": "2-3 hours",
          "cost": "Free"
        }
      ],
      "afternoon": [
        {
          "time": "1:00 PM",
          "activity": "Lunch at Franklin Barbecue",
          "type": "food",
          "cuisine": "BBQ",
          "price": "$$",
          "note": "Famous BBQ, expect long lines"
        },
        {
          "time": "3:00 PM",
          "activity": "Lady Bird Lake",
          "type": "nature",
          "duration": "Half day",
          "cost": "Free"
        }
      ],
      "evening": [
        {
          "time": "7:00 PM",
          "activity": "Dinner at Uchi",
          "type": "food",
          "cuisine": "Japanese",
          "price": "$$$"
        }
      ],
      "dailyBudget": {
        "food": 85,
        "attractions": 0,
        "activities": 30,
        "transportation": 25,
        "total": 140
      },
      "tips": ["Start with major attractions to get oriented", "Make dinner reservations in advance"]
    }
  }
}
```

## 🏗️ Architecture

### Project Structure

```
travel-planner/
├── server.py                 # Main MCP server implementation
├── tools/                    # Tool implementations
│   ├── __init__.py
│   ├── search_flights.py     # Flight search logic
│   ├── search_hotels.py      # Hotel search logic
│   ├── search_cars.py        # Car rental logic
│   ├── search_trains.py      # Train search logic
│   └── generate_itinerary.py # Itinerary generation
├── resources/                # Static resources
│   └── travel_guides/        # City travel guides
│       ├── austin.json
│       ├── san_francisco.json
│       └── new_york.json
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── examples/                # Usage examples
    └── sample_interactions.py
```

### Core Components

#### 1. **MCP Server (`server.py`)**
- Handles tool registration and execution
- Manages resource access
- Provides proper error handling and logging
- Implements async patterns for scalability

#### 2. **Tool Modules**
Each tool module provides:
- Input validation and sanitization
- Mock data generation (production would use real APIs)
- Structured response formatting
- Error handling with helpful messages

#### 3. **Resource System**
- Static travel guides in JSON format
- Accessible via MCP resource protocol
- Rich city information including attractions, restaurants, tips

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set log level
export LOG_LEVEL=INFO

# Optional: Set data directory for resources
export TRAVEL_DATA_DIR=/path/to/travel/data
```

### Customization

The server is designed to be easily customizable:

1. **Add New Cities**: Create new JSON files in `resources/travel_guides/`
2. **Add New Tools**: Implement new tool modules in `tools/` directory
3. **Integrate Real APIs**: Replace mock data with actual API calls
4. **Extend Resources**: Add new resource types (maps, weather, etc.)

## 🌍 Real API Integration

This project uses mock data for demonstration, but it's designed for easy real API integration:

### Flight APIs
- **Amadeus Travel API**: Global flight data
- **Skyscanner API**: Flight comparison
- **Google Flights API**: Comprehensive flight search

### Hotel APIs
- **Booking.com API**: Global hotel inventory
- **Expedia API**: Travel booking platform
- **Hotels.com API**: Hotel search and booking

### Car Rental APIs
- **Hertz API**: Car rental bookings
- **Enterprise API**: Fleet management
- **Kayak API**: Car rental comparison

### Train APIs
- **Amtrak API**: US train schedules and booking
- **Eurail API**: European train travel
- **National Rail API**: UK train information

### Implementation Example

```python
# Example: Replace mock flight data with real API
async def search_flights(from_city: str, to_city: str, date: str, passengers: int):
    # Instead of generating mock data:
    amadeus_client = AmadeusClient(api_key=os.getenv('AMADEUS_API_KEY'))

    response = await amadeus_client.shopping.flight_offers_search.get(
        originLocationCode=from_city,
        destinationLocationCode=to_city,
        departureDate=date,
        adults=passengers
    )

    # Transform API response to standard format
    return transform_amadeus_response(response.data)
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=tools tests/
```

### Test Examples

```python
import pytest
from tools.search_flights import search_flights

@pytest.mark.asyncio
async def test_flight_search():
    result = await search_flights("AUS", "SFO", "2025-10-01", 1)

    assert result["searchCriteria"]["from"] == "AUS"
    assert result["searchCriteria"]["to"] == "SFO"
    assert "flights" in result
    assert len(result["flights"]) > 0
```

## 🚀 Extensions & Ideas

### Immediate Extensions
1. **Real API Integration**: Replace mock data with actual travel APIs
2. **User Preferences**: Save and use traveler preferences
3. **Budget Constraints**: Filter results by budget limits
4. **Multi-City Support**: Plan complex itineraries with multiple destinations

### Advanced Features
1. **AI-Powered Recommendations**: Use ML to suggest personalized activities
2. **Real-Time Updates**: Live flight delays, hotel availability
3. **Social Integration**: Share itineraries and get recommendations
4. **Weather Integration**: Factor weather into planning decisions
5. **Currency Conversion**: Handle multiple currencies automatically
6. **Accessibility Options**: Filter for accessibility requirements

### Enterprise Features
1. **Team Travel**: Coordinate group bookings and shared itineraries
2. **Expense Management**: Integration with corporate expense systems
3. **Policy Compliance**: Ensure bookings meet company travel policies
4. **Analytics Dashboard**: Track travel patterns and spending

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Add new tools, improve existing ones, or enhance documentation
4. **Write tests**: Ensure your changes are well-tested
5. **Submit a pull request**: Describe your changes and their benefits

### Contribution Ideas
- Add new cities to the travel guides
- Implement additional transportation types (buses, ferries)
- Create specialized tools (restaurant reservations, event tickets)
- Improve error handling and validation
- Add internationalization support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Model Context Protocol**: For providing the standard that makes this possible
- **Travel APIs**: Inspiration from various travel booking platforms
- **Open Source Community**: For tools and libraries that made development easier

## 📚 Documentation

- **[API Documentation](docs/API.md)**: Complete API reference with examples
- **[Development Guide](docs/DEVELOPMENT.md)**: Setup, testing, and contribution guide
- **[README](README.md)**: This file - overview and quick start

## 📞 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/bvedpathak/travel-planner/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/bvedpathak/travel-planner/discussions)
- **Documentation**: Full documentation available in the `/docs` directory

---

**Happy Travels! ✈️🏨🚗🚂**

*Built with ❤️ to demonstrate the power of the Model Context Protocol*