# 🌐 AroundMe System - Web App Integration Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Current Features](#current-features)
3. [Architecture](#architecture)
4. [API Reference](#api-reference)
5. [Integration Steps](#integration-steps)
6. [Key Functionalities](#key-functionalities)
7. [File Structure](#file-structure)
8. [Dependencies](#dependencies)

---

## 🎯 System Overview

**AroundMe** is a location-based recommendation system that helps users discover restaurants, utilities, and malls near their current location with intelligent filtering and real-time GPS tracking.

### What It Does:
- **Auto-detects user location** via browser GPS or manual input
- **Searches 3 categories**: Meals (10 cuisines), Utilities (11 types), Malls (4 types)
- **Filters by**: Rating, reviews, price, distance, category, opening hours
- **Displays**: Interactive map with live GPS tracking + detailed list view
- **Integrates**: Google Places API for real data, shuttle route awareness

### Current Status:
✅ Fully functional Python desktop application  
✅ Browser-based GPS detection with local web server  
✅ Live location tracking on interactive maps  
✅ Multi-category search (25 total search types)  
🔄 Ready for web app integration

---

## ✨ Current Features

### 1. **Automatic GPS Location Detection**
- **Method 1**: Browser-based GPS using Geolocation API
  - Opens local web server (localhost:8765)
  - Captures precise GPS coordinates automatically
  - No manual copy-paste needed
  - Works on phones and laptops

- **Method 2**: Manual coordinate entry
  - Fallback option if GPS fails
  - Supports Google Maps coordinate format
  - Validates Pune area boundaries

### 2. **Multi-Category Search**

#### 🍴 Meals (10 Cuisines):
- Italian, Indian, Asian, Mexican, American
- Continental, Street Food, Healthy, Desserts, Cafe

#### 🛒 Utilities (11 Types):
- Grocery Store, Supermarket, Convenience Store
- Pharmacy, ATM/Bank, Gas Station, Laundry
- Hardware Store, Car Repair, Car Wash, Tailor

#### 🏬 Malls (4 Types):
- Shopping Mall, Department Store
- Shopping Center, Outlet Mall

### 3. **Dynamic Filtering System**
- **Rating**: 0+ / 3.5+ / 4.0+ / 4.5+ stars
- **Reviews**: 0+ / 50+ / 100+ / 200+ reviews
- **Price**: ₹ / ₹₹ / ₹₹₹ / ₹₹₹₹
- **Distance**: 100m to search radius (dynamic)
- **Category**: Multi-select cuisines/utilities/malls

### 4. **Opening Hours Integration**
- **Open/Closed status**: Real-time indicator
- **Today's hours**: Shows current day's operating hours
- **Format**: "Monday: 9:00 AM – 10:00 PM"

### 5. **Interactive Map with Live Tracking**
- **Base layers**: OpenStreetMap tiles
- **Shuttle route**: Blue line with start/end/waypoint markers
- **Current location**: Blue pulsing marker
- **Places**: Color-coded by rating (green/orange/red)
- **Live GPS button**: Start/stop real-time position tracking
- **Features**:
  - Pulsing animation on live location
  - Accuracy radius circle
  - Nearest shuttle stop calculation
  - Google Maps & Search links in popups
  - Opening hours in popups

### 6. **Smart Search Strategy**
- **Keyword-based**: Searches by cuisine/utility-specific keywords
- **Efficient API usage**: 1-2 calls per category vs 36+ for generic
- **Example**: "Italian" → searches for "italian restaurant", "pizza", "pasta"

### 7. **Shuttle Route Integration**
- **Pre-defined routes**: FLAME to FC Road, FC Road to FLAME
- **Waypoint**: FLAME Bus Point (Bavdhan)
- **Nearest stop finder**: Calculates closest shuttle stop for each place
- **Display format**: "🚌 Stop #X (500m walk from stop)"

---

## 🏗️ Architecture

### System Components:

```
┌─────────────────────────────────────────────────────┐
│                   User Interface                    │
│            (launch_aroundme.py - Terminal)          │
│         [To be replaced with Web App UI]            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            Core System Logic                         │
│      (integrated_aroundme_system.py)                │
│                                                      │
│  • fetch_places_near_location()                     │
│  • fetch_restaurants_near_location()                │
│  • fetch_utilities_near_location()                  │
│  • fetch_malls_near_location()                      │
│  • get_route_coordinates()                          │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Google  │  │   Map    │  │   GPS    │
│  Places  │  │  Viewer  │  │ Handler  │
│   API    │  │(Folium)  │  │(Browser) │
└──────────┘  └──────────┘  └──────────┘
```

### Data Flow:

```
1. User Input → Location (GPS/Manual) + Search Radius + Category + Filters
2. System → Google Places API (Nearby Search with keywords)
3. API Response → Places with details (name, rating, hours, location)
4. Processing → Filter by user criteria + Calculate distances
5. Map Generation → Folium HTML with JavaScript for live tracking
6. Display → Interactive map + Filtered list with details
```

---

## 🔌 API Reference

### Core Functions (integrated_aroundme_system.py)

#### 1. **fetch_places_near_location()**
```python
def fetch_places_near_location(
    location: Tuple[float, float],  # (lat, lng)
    radius: int = 1000,              # meters
    categories: list = None,         # ['Italian', 'Indian'] or ['Pharmacy']
    place_type: str = 'meals'        # 'meals', 'utilities', or 'malls'
) -> pd.DataFrame
```
**Returns**: DataFrame with columns:
- `place_id`, `name`, `lat`, `lng`
- `rating`, `user_ratings_total`, `price_level`
- `categories`, `types`, `neighborhood`
- `open_now`, `weekday_text` (opening hours)
- `cuisine` (tagged category)

**Example**:
```python
places = system.fetch_places_near_location(
    location=(18.5089, 73.7654),
    radius=2000,
    categories=['Italian', 'Cafe'],
    place_type='meals'
)
```

#### 2. **fetch_restaurants_near_location()**
```python
def fetch_restaurants_near_location(
    location: Tuple[float, float],
    radius: int = 1000,
    cuisines: list = None  # ['Italian', 'Indian', 'Asian']
) -> pd.DataFrame
```
**Keyword Mapping**:
- `Italian` → ['italian restaurant', 'pizza', 'pasta']
- `Indian` → ['indian restaurant', 'biryani', 'curry']
- `Asian` → ['chinese restaurant', 'japanese restaurant', 'thai restaurant', 'sushi']

#### 3. **fetch_utilities_near_location()**
```python
def fetch_utilities_near_location(
    location: Tuple[float, float],
    radius: int = 1000,
    utility_types: list = None
) -> pd.DataFrame
```
**Keyword Mapping**:
- `Grocery Store` → ['grocery store', 'grocery']
- `Pharmacy` → ['pharmacy', 'medical store', 'chemist']
- `Car Repair` → ['car repair', 'auto repair', 'mechanic', 'car service']

#### 4. **fetch_malls_near_location()**
```python
def fetch_malls_near_location(
    location: Tuple[float, float],
    radius: int = 1000,
    mall_types: list = None
) -> pd.DataFrame
```

#### 5. **get_route_coordinates()**
```python
def get_route_coordinates(
    route_name: str  # 'flame_to_fc_road' or 'fc_road_to_flame'
) -> List[Tuple[float, float]]
```
**Returns**: List of (lat, lng) tuples along the route

---

### GPS Location Functions (map_viewer.py)

#### **get_current_gps_location()**
```python
def get_current_gps_location() -> Tuple[float, float]
```
**Process**:
1. Prompts: Auto-detect vs Manual
2. If Auto-detect:
   - Starts local HTTP server on port 8765
   - Opens browser with GPS detection page
   - Browser sends coordinates back to server
   - Automatically captured (no user action needed after "Allow")
3. If Manual: Prompts for lat/lng input

**Returns**: `(latitude, longitude)` or `None` if cancelled

---

### Map Viewer Functions (map_viewer.py)

#### **AroundMeMapViewer Class**

##### **create_interactive_map()**
```python
def create_interactive_map(
    route_name: str,
    current_location: Tuple[float, float],
    restaurants: List[Dict],
    session_preferences: Dict
)
```
**Creates**: Folium map with:
- Shuttle route polyline
- Current location marker
- Restaurant markers (color-coded by rating)
- Popups with: name, rating, price, distance, hours, shuttle stop, Google links

##### **save_and_open_map()**
```python
def save_and_open_map(
    filename: str = "aroundme_live_map.html"
) -> str
```
**Process**:
1. Saves Folium map to HTML
2. Injects JavaScript for live GPS tracking
3. Adds "Start Live Tracking" button
4. Opens in default browser

**Live Tracking Features**:
- Uses `navigator.geolocation.watchPosition()`
- Updates every 5 seconds
- Pulsing blue marker with accuracy circle
- Auto-pans to location on first update

---

## 🚀 Integration Steps

### Phase 1: Backend API Setup

#### Step 1: Create Flask/FastAPI Backend
```python
# Example Flask endpoint structure
from flask import Flask, request, jsonify
from integrated_aroundme_system import IntegratedAroundMeSystem

app = Flask(__name__)
system = IntegratedAroundMeSystem(
    google_api_key="YOUR_API_KEY",
    use_synthetic_data=False
)

@app.route('/api/search', methods=['POST'])
def search_places():
    data = request.json
    location = (data['lat'], data['lng'])
    radius = data['radius']
    category = data['category']  # 'meals', 'utilities', 'malls'
    categories = data.get('categories', [])
    
    # Fetch places
    places_df = system.fetch_places_near_location(
        location, radius, categories, category
    )
    
    # Convert to JSON
    places = places_df.to_dict('records')
    
    return jsonify({
        'status': 'success',
        'count': len(places),
        'places': places
    })

@app.route('/api/route', methods=['GET'])
def get_route():
    route_name = request.args.get('name', 'flame_to_fc_road')
    coords = system.get_route_coordinates(route_name)
    
    return jsonify({
        'route_name': route_name,
        'coordinates': coords
    })
```

#### Step 2: Convert GPS Detection to Web-Based
Instead of local server, use frontend JavaScript:
```javascript
// GPS detection function
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                error => reject(error),
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            reject(new Error('Geolocation not supported'));
        }
    });
}

// Usage
async function detectLocation() {
    try {
        const location = await getCurrentLocation();
        console.log('Location:', location);
        // Send to backend API
        searchPlaces(location.lat, location.lng);
    } catch (error) {
        console.error('GPS error:', error);
        // Show manual input form
    }
}
```

#### Step 3: Map Integration
Use Leaflet.js (Folium's underlying library) in React/Vue:

**React Example**:
```javascript
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';

function AroundMeMap({ currentLocation, places, route }) {
    const [liveLocation, setLiveLocation] = useState(null);
    
    // Live tracking
    useEffect(() => {
        const watchId = navigator.geolocation.watchPosition(
            position => {
                setLiveLocation({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
            },
            null,
            { enableHighAccuracy: true, maximumAge: 0 }
        );
        
        return () => navigator.geolocation.clearWatch(watchId);
    }, []);
    
    return (
        <MapContainer center={currentLocation} zoom={14}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            
            {/* Route line */}
            <Polyline positions={route} color="blue" weight={5} />
            
            {/* Current location */}
            <Marker position={currentLocation} icon={userIcon}>
                <Popup>You are here</Popup>
            </Marker>
            
            {/* Live location with pulsing effect */}
            {liveLocation && (
                <>
                    <Circle 
                        center={liveLocation} 
                        radius={liveLocation.accuracy}
                        color="#4285F4"
                        fillOpacity={0.1}
                    />
                    <Marker position={liveLocation} icon={liveLocationIcon}>
                        <Popup>Live Location</Popup>
                    </Marker>
                </>
            )}
            
            {/* Place markers */}
            {places.map(place => (
                <Marker 
                    key={place.place_id} 
                    position={[place.lat, place.lng]}
                    icon={getRatingIcon(place.rating)}
                >
                    <Popup>
                        <h4>{place.name}</h4>
                        <p>Rating: {place.rating} ⭐</p>
                        <p>Price: {'₹'.repeat(place.price_level)}</p>
                        <p>{place.open_now ? '🟢 Open' : '🔴 Closed'}</p>
                        {place.weekday_text && <p>📅 {place.weekday_text[0]}</p>}
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
}
```

---

### Phase 2: Frontend UI Components

#### Component Structure:
```
src/
├── components/
│   ├── LocationInput/
│   │   ├── AutoDetect.jsx        # GPS detection component
│   │   └── ManualInput.jsx       # Manual coordinate input
│   ├── Search/
│   │   ├── CategorySelector.jsx  # Meals/Utilities/Malls tabs
│   │   ├── RadiusSlider.jsx      # Distance slider
│   │   └── TypeSelector.jsx      # Cuisine/utility checkboxes
│   ├── Filters/
│   │   ├── RatingFilter.jsx
│   │   ├── PriceFilter.jsx
│   │   ├── ReviewFilter.jsx
│   │   └── DistanceFilter.jsx
│   ├── Results/
│   │   ├── PlaceList.jsx         # List view of places
│   │   ├── PlaceCard.jsx         # Individual place card
│   │   └── MapView.jsx           # Interactive map
│   └── Map/
│       ├── AroundMeMap.jsx       # Main map component
│       ├── LiveTracker.jsx       # GPS tracking toggle
│       └── PlaceMarker.jsx       # Custom marker component
├── services/
│   ├── api.js                    # Backend API calls
│   └── gps.js                    # GPS utilities
└── utils/
    ├── filters.js                # Filtering logic
    └── distance.js               # Distance calculations
```

---

### Phase 3: API Endpoints Needed

#### 1. **Search Places**
```
POST /api/search
Body: {
    "lat": 18.5089,
    "lng": 73.7654,
    "radius": 2000,
    "category": "meals",
    "categories": ["Italian", "Indian"],
    "filters": {
        "min_rating": 4.0,
        "min_reviews": 50,
        "max_price": 3
    }
}

Response: {
    "status": "success",
    "count": 25,
    "places": [
        {
            "place_id": "ChIJ...",
            "name": "Pizza Corner",
            "lat": 18.5123,
            "lng": 73.7689,
            "rating": 4.5,
            "user_ratings_total": 234,
            "price_level": 2,
            "categories": "Italian",
            "open_now": true,
            "weekday_text": [
                "Monday: 11:00 AM – 11:00 PM",
                ...
            ],
            "distance_from_current": 456
        },
        ...
    ]
}
```

#### 2. **Get Route Coordinates**
```
GET /api/route?name=flame_to_fc_road

Response: {
    "route_name": "flame_to_fc_road",
    "origin": "FLAME University, Pune",
    "destination": "FC Road, Pune",
    "waypoints": ["FLAME Bus Point, Bavdhan, Pune"],
    "coordinates": [
        [18.5089, 73.7654],
        [18.5058, 73.7687],
        ...
    ]
}
```

#### 3. **Find Nearest Shuttle Stop**
```
POST /api/nearest-stop
Body: {
    "route_name": "flame_to_fc_road",
    "place_location": {"lat": 18.5100, "lng": 73.7700}
}

Response: {
    "stop_name": "FLAME Bus Point (Bavdhan)",
    "distance": 523,
    "location": {"lat": 18.5058, "lng": 73.7687},
    "index": 15
}
```

---

## 🔑 Key Functionalities

### 1. **Location Detection**

**Current Python Implementation**:
```python
# Starts local web server, opens browser, captures GPS
coords = get_current_gps_location()
```

**Web App Implementation**:
```javascript
// Direct browser API call
async function getLocation() {
    const pos = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 10000
        });
    });
    
    return {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude
    };
}
```

### 2. **Category-Based Search**

**Python**:
```python
# Router function
places = system.fetch_places_near_location(
    location=(lat, lng),
    radius=2000,
    categories=['Italian', 'Cafe'],
    place_type='meals'
)
```

**Web API**:
```javascript
// POST to /api/search
const response = await fetch('/api/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        lat: location.lat,
        lng: location.lng,
        radius: 2000,
        category: 'meals',
        categories: ['Italian', 'Cafe']
    })
});
const data = await response.json();
```

### 3. **Dynamic Filtering**

**Python (current)**:
```python
def apply_filters(places_list, filters):
    filtered = places_list.copy()
    
    # Category filter
    if filters['cuisines']:
        filtered = [p for p in filtered 
                   if any(c.lower() in p.get('name', '').lower() 
                         for c in filters['cuisines'])]
    
    # Rating filter
    if filters['min_rating'] > 0:
        filtered = [p for p in filtered 
                   if p.get('rating', 0) >= filters['min_rating']]
    
    # Price filter
    if filters['max_price'] > 0:
        filtered = [p for p in filtered 
                   if p.get('price_level', 2) <= filters['max_price']]
    
    return filtered
```

**JavaScript (web app)**:
```javascript
function applyFilters(places, filters) {
    return places.filter(place => {
        // Category filter
        if (filters.categories.length > 0) {
            if (!filters.categories.some(c => 
                place.categories.toLowerCase().includes(c.toLowerCase())
            )) return false;
        }
        
        // Rating filter
        if (place.rating < filters.minRating) return false;
        
        // Review filter
        if (place.user_ratings_total < filters.minReviews) return false;
        
        // Price filter
        if (filters.maxPrice > 0 && place.price_level > filters.maxPrice) 
            return false;
        
        // Distance filter
        if (place.distance_from_current > filters.maxDistance) 
            return false;
        
        return true;
    });
}
```

### 4. **Live GPS Tracking**

**Current (embedded in HTML)**:
```javascript
// In map HTML file
var watchId = navigator.geolocation.watchPosition(
    position => {
        updateMarker(position.coords.latitude, position.coords.longitude);
    },
    null,
    { enableHighAccuracy: true, maximumAge: 0 }
);
```

**Web App (React Hook)**:
```javascript
function useLiveLocation() {
    const [location, setLocation] = useState(null);
    
    useEffect(() => {
        const watchId = navigator.geolocation.watchPosition(
            position => {
                setLocation({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: position.timestamp
                });
            },
            error => console.error('GPS error:', error),
            { enableHighAccuracy: true, maximumAge: 0 }
        );
        
        return () => navigator.geolocation.clearWatch(watchId);
    }, []);
    
    return location;
}

// Usage in component
function MapWithTracking() {
    const liveLocation = useLiveLocation();
    
    return (
        <AroundMeMap currentLocation={liveLocation} />
    );
}
```

---

## 📂 File Structure

### Current System Files:

```
aroundme/
├── integrated_aroundme_system.py   # Core system (305 lines)
│   ├── IntegratedAroundMeSystem class
│   ├── fetch_places_near_location()
│   ├── fetch_restaurants_near_location()
│   ├── fetch_utilities_near_location()
│   ├── fetch_malls_near_location()
│   ├── get_route_coordinates()
│   └── _convert_google_place_to_internal()
│
├── launch_aroundme.py              # Terminal UI (1021 lines)
│   ├── main()
│   ├── launch_live_map_mode()
│   ├── apply_filters()
│   ├── display_filtered_restaurants()
│   └── show_map_view()
│
├── map_viewer.py                   # Map generation (1065 lines)
│   ├── AroundMeMapViewer class
│   ├── create_interactive_map()
│   ├── save_and_open_map() [with live tracking JS]
│   ├── get_current_gps_location()
│   ├── _add_restaurant_markers()
│   └── _find_nearest_shuttle_stop()
│
└── aroundme_synth/                 # Synthetic data (optional)
    ├── places.csv
    ├── users.csv
    └── interactions.csv
```

### Files to Port to Web App:

| Python File | Web Component | Priority |
|------------|---------------|----------|
| `integrated_aroundme_system.py` | Backend API | **HIGH** |
| `map_viewer.get_current_gps_location()` | Frontend GPS service | **HIGH** |
| `map_viewer.AroundMeMapViewer` | React/Vue Map component | **HIGH** |
| `launch_aroundme.apply_filters()` | Frontend filter utilities | MEDIUM |
| `launch_aroundme.display_filtered_restaurants()` | PlaceList component | MEDIUM |

---

## 📦 Dependencies

### Python (Backend):
```bash
pip install pandas numpy requests geopy folium
```

**Package Versions**:
- `pandas` >= 1.3.0 - Data manipulation
- `numpy` >= 1.21.0 - Numerical operations
- `requests` >= 2.26.0 - Google Places API calls
- `geopy` >= 2.2.0 - Distance calculations
- `folium` >= 0.12.0 - Map generation (not needed for web)

### JavaScript (Frontend):
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-leaflet": "^4.0.0",
    "leaflet": "^1.9.0",
    "axios": "^1.0.0"
  }
}
```

**For Map**:
- `react-leaflet` - React bindings for Leaflet
- `leaflet` - Interactive maps
- Custom icons and styling for markers

---

## 🔐 Environment Variables

```env
# .env file
GOOGLE_PLACES_API_KEY=AIzaSyA5Bra70R6GRitr_Biv3QY_Cmre8wQJpmo
FLASK_ENV=development
PORT=5000
```

**Security Notes**:
- ⚠️ Never expose API key in frontend code
- ✅ All API calls go through backend
- ✅ Implement rate limiting
- ✅ Add CORS configuration

---

## 🎨 UI/UX Recommendations

### Flow:
1. **Landing** → "Find places near you"
2. **Location** → Auto-detect (1 click) or Manual
3. **Category** → Tabs: Meals | Utilities | Malls
4. **Type Selection** → Multi-select checkboxes
5. **Radius** → Slider: 500m - 10km
6. **Filters** → Collapsible panel (Rating/Price/Reviews)
7. **Results** → Split view: Map (left) + List (right)
8. **Live Tracking** → Toggle button on map

### Key UI Elements:
- **GPS Button**: "📍 Detect My Location" (primary CTA)
- **Category Pills**: Clickable, active state
- **Filter Chips**: Show active filters, removable
- **Place Cards**: Image, name, rating, price, distance, hours
- **Map Markers**: Color-coded by rating, clustered when zoomed out
- **Live Tracker**: Pulsing blue dot, "Following" indicator

---

## 🧪 Testing Checklist

### Backend API:
- [ ] Search endpoint returns valid places
- [ ] Filters work correctly (rating/price/distance)
- [ ] Route coordinates are accurate
- [ ] Nearest shuttle stop calculation works
- [ ] Opening hours are parsed correctly
- [ ] Error handling for invalid coordinates
- [ ] Rate limiting on API calls

### Frontend:
- [ ] GPS detection works on mobile/desktop
- [ ] Manual input validates coordinates
- [ ] Category switching updates search
- [ ] Filters update results in real-time
- [ ] Map renders correctly
- [ ] Live tracking starts/stops properly
- [ ] Markers show correct information
- [ ] Popups display opening hours
- [ ] Google Maps links work
- [ ] Responsive design on all screens

### Integration:
- [ ] Frontend → Backend API calls work
- [ ] CORS configured correctly
- [ ] Error messages display properly
- [ ] Loading states during API calls
- [ ] No API key exposure in frontend

---

## 📞 Support & Contact

For questions about integration:
- Review existing Python code in `aroundme/` folder
- Test desktop app: `python launch_aroundme.py`
- Check API responses in browser DevTools
- Refer to Google Places API docs: https://developers.google.com/maps/documentation/places/web-service

---

## 🚀 Quick Start for Developers

1. **Clone and setup**:
```bash
cd "aroundme"
pip install -r requirements.txt
```

2. **Test current system**:
```bash
python launch_aroundme.py
# Select option 2 (Production Mode)
# Choose auto-detect or manual location
# Try searching for Italian restaurants
```

3. **Review core functions**:
```bash
# Main search function
python -c "from integrated_aroundme_system import IntegratedAroundMeSystem; print(IntegratedAroundMeSystem.__doc__)"

# Check available methods
python -c "from integrated_aroundme_system import IntegratedAroundMeSystem; import inspect; print([m for m in dir(IntegratedAroundMeSystem) if not m.startswith('_')])"
```

4. **Extract data schema**:
```bash
# Run one search and save result
python -c "
from integrated_aroundme_system import IntegratedAroundMeSystem
system = IntegratedAroundMeSystem('YOUR_API_KEY', False)
places = system.fetch_places_near_location((18.5089, 73.7654), 1000, [], 'meals')
print(places.head().to_json(orient='records', indent=2))
" > sample_places.json
```

---

## ✅ Summary

**What Works Now**:
- ✅ Auto GPS detection via browser
- ✅ 25 search types across 3 categories
- ✅ Real-time filtering (5 criteria)
- ✅ Interactive maps with live tracking
- ✅ Opening hours integration
- ✅ Shuttle route awareness
- ✅ Google Places API integration

**What Needs Porting**:
1. Backend API endpoints (Flask/FastAPI)
2. Frontend GPS service (JavaScript)
3. Map component (React-Leaflet)
4. Search UI (React components)
5. Filter system (JavaScript)
6. Live tracking toggle (React Hook)

**Estimated Effort**:
- Backend API: 2-3 days
- Frontend Components: 3-4 days
- Map Integration: 2-3 days
- Testing & Polish: 2-3 days
- **Total**: ~10-14 days

---

*Last Updated: December 2, 2024*  
*Version: 3.0 (Live GPS Tracking + Multi-Category)*
