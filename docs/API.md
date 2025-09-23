# Travel Planner MCP Server API Documentation

## Overview

The Travel Planner MCP Server provides a comprehensive set of tools for travel planning through the Model Context Protocol (MCP). This document details the API endpoints, data structures, and integration patterns.

## Base Configuration

### Server Information
- **Server Name**: `travel-planner`
- **Protocol**: Model Context Protocol (MCP)
- **Communication**: stdio (standard input/output)
- **Response Format**: JSON

### Authentication
API integrations require configuration in `config.yaml`:

```yaml
flight_api:
  rapidapi:
    key: "your-rapidapi-key"
    host: "booking-com.p.rapidapi.com"
    base_url: "https://booking-com.p.rapidapi.com/v1/flights"
```

## Tools

### 1. Flight Search (`searchFlights`)

Search for flights between two cities using live Booking.com API.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `from_id` | string | Yes | - | Departure airport ID (e.g., 'BOM.AIRPORT') |
| `to_id` | string | Yes | - | Arrival airport ID (e.g., 'DEL.AIRPORT') |
| `depart_date` | string | Yes | - | Departure date in YYYY-MM-DD format |
| `return_date` | string | No | - | Return date for round trip |
| `adults` | integer | No | 1 | Number of adult passengers |
| `children` | integer | No | 0 | Number of child passengers |
| `stops` | string | No | "none" | Number of stops: "none", "one", "any" |
| `cabin_class` | string | No | "ECONOMY" | Cabin class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST |
| `currency_code` | string | No | "USD" | Currency code |

#### Response Structure

```json
{
  "searchCriteria": {
    "from": "BOM.AIRPORT",
    "to": "DEL.AIRPORT",
    "departDate": "2025-10-01",
    "returnDate": null,
    "adults": 1,
    "children": 0,
    "cabinClass": "ECONOMY",
    "stops": "none"
  },
  "resultsFound": 15,
  "resultsDisplayed": 10,
  "summary": {
    "totalFlights": 15,
    "minPrice": "USD 125.50",
    "priceRange": "USD 125.50 - USD 890.00",
    "airlines": 5,
    "directFlights": 8
  },
  "flights": [
    {
      "segments": [
        {
          "departure": {
            "airport": "BOM",
            "airportName": "Chhatrapati Shivaji International",
            "city": "Mumbai",
            "time": "14:30",
            "date": "2025-10-01"
          },
          "arrival": {
            "airport": "DEL",
            "airportName": "Indira Gandhi International",
            "city": "New Delhi",
            "time": "16:45",
            "date": "2025-10-01"
          },
          "duration": "2h 15m",
          "flightNumber": "AI101",
          "airline": "Air India",
          "stops": 0,
          "cabinClass": "ECONOMY"
        }
      ],
      "totalPrice": "USD 145.75",
      "priceBreakdown": {
        "baseFare": "USD 120.00",
        "taxes": "USD 25.75",
        "total": "USD 145.75"
      },
      "tripType": "ONE_WAY",
      "bookingToken": "abc123...",
      "isRoundTrip": false
    }
  ],
  "searchTimestamp": "2025-09-23T10:30:00Z",
  "source": "Booking.com RapidAPI"
}
```

#### Error Response

```json
{
  "error": "API Error: Invalid airport code",
  "requestId": "req_123456",
  "searchCriteria": { /* original search criteria */ }
}
```

### 2. Hotel Search (`searchHotels`)

Search for hotels in a specified city using mock data.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `city` | string | Yes | - | City name for hotel search |
| `check_in` | string | Yes | - | Check-in date in YYYY-MM-DD format |
| `nights` | integer | Yes | - | Number of nights to stay |
| `guests` | integer | No | 2 | Number of guests |

#### Response Structure

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
      "amenities": ["Free WiFi", "Swimming Pool", "Fitness Center"],
      "distance": {
        "downtown": "0.5 miles",
        "airport": "12.3 miles"
      },
      "policies": {
        "checkInTime": "3:00 PM",
        "checkOutTime": "11:00 AM",
        "cancellation": "Free cancellation until 24 hours before check-in",
        "petPolicy": "No pets allowed"
      }
    }
  ],
  "searchTimestamp": "2025-09-23T10:30:00Z",
  "note": "This is mock data. In production, this would integrate with real hotel booking APIs."
}
```

### 3. Car Rental Search (`searchCars`)

Search for rental cars using Booking.com API.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `city` | string | Yes | - | City for car rental |
| `pickup_date` | string | Yes | - | Pickup date in YYYY-MM-DD format |
| `days` | integer | Yes | - | Number of rental days |
| `car_type` | string | No | "any" | Car type: economy, compact, intermediate, suv, luxury |

### 4. Train Search (`searchTrains`)

Search for train routes using mock data.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `from_city` | string | Yes | - | Departure city code |
| `to_city` | string | Yes | - | Arrival city code |
| `date` | string | Yes | - | Travel date in YYYY-MM-DD format |
| `passengers` | integer | No | 1 | Number of passengers |

### 5. Itinerary Generation (`generateItinerary`)

Generate detailed travel itineraries based on preferences.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `city` | string | Yes | - | Destination city |
| `days` | integer | Yes | - | Number of days |
| `interests` | array | No | [] | Interest categories: food, culture, nature, shopping, nightlife |

## Resources

### Travel Guides

Access static travel guide data for major cities.

#### Available Resources

- `travel-guide://austin` - Austin, Texas travel guide
- `travel-guide://san_francisco` - San Francisco, California travel guide
- `travel-guide://new_york` - New York City travel guide

#### Resource Structure

```json
{
  "city": "Austin",
  "state": "Texas",
  "country": "USA",
  "description": "Live music capital of the world...",
  "bestTimeToVisit": "March-May and September-November",
  "attractions": [
    {
      "name": "South by Southwest (SXSW)",
      "type": "event",
      "description": "Annual music, film, and interactive festival",
      "season": "March"
    }
  ],
  "foodScene": {
    "specialties": ["BBQ", "Tex-Mex", "Food Trucks"],
    "famousEats": ["Franklin Barbecue", "Torchy's Tacos"]
  },
  "transportation": {
    "airport": "AUS (Austin-Bergstrom International)",
    "publicTransit": "CapMetro buses and MetroRail",
    "bikeShare": "B-Cycle bike sharing"
  }
}
```

## Error Handling

### Common Error Types

1. **Validation Errors**
   - Invalid date formats
   - Missing required parameters
   - Out-of-range values

2. **API Errors**
   - Authentication failures
   - Rate limiting
   - Service unavailable

3. **Data Errors**
   - City not found
   - No results available
   - Invalid airport codes

### Error Response Format

```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": "Additional error details",
  "requestId": "unique_request_id",
  "timestamp": "2025-09-23T10:30:00Z"
}
```

## Rate Limiting

- **Flight API**: 100 requests per hour
- **Car Rental API**: 50 requests per hour
- **Mock Data Tools**: No limits

## Development Notes

### Mock vs Live Data

| Tool | Data Source | Production Ready |
|------|-------------|------------------|
| searchFlights | Live Booking.com API | Yes |
| searchCars | Live Booking.com API | Yes |
| searchHotels | Mock data | No |
| searchTrains | Mock data | No |
| generateItinerary | Mock data | No |

### Extending the API

1. **Adding New Cities**: Update `HOTELS_BY_CITY` and create new travel guide resources
2. **Real API Integration**: Replace mock functions with actual API calls
3. **New Tools**: Follow the MCP tool schema pattern in `server.py`

## Examples

### Basic Flight Search

```bash
# Using MCP client
{
  "tool": "searchFlights",
  "params": {
    "from_id": "BOM.AIRPORT",
    "to_id": "DEL.AIRPORT",
    "depart_date": "2025-10-01",
    "adults": 1
  }
}
```

### Multi-city Itinerary

```bash
# Generate Austin itinerary
{
  "tool": "generateItinerary",
  "params": {
    "city": "Austin",
    "days": 3,
    "interests": ["food", "culture", "nature"]
  }
}
```

## Support

For API issues, integration questions, or feature requests:

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the main README for setup instructions
- **Configuration**: Ensure `config.yaml` is properly configured for live APIs