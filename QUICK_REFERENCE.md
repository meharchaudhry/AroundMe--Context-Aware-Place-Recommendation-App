# 🚀 AroundMe - Quick Reference Sheet

## 📌 Essential Info at a Glance

### System Capabilities
- **Location Detection**: Auto GPS (browser-based) or manual input
- **Search Categories**: Meals (10), Utilities (11), Malls (4) = 25 types
- **Filters**: Rating, Reviews, Price (₹-₹₹₹₹), Distance, Category, Hours
- **Map Features**: Live GPS tracking, shuttle routes, nearest stops
- **Data Source**: Google Places API (real-time data)

---

## 🔑 Core Functions

### 1. Search Places
```python
system.fetch_places_near_location(
    location=(18.5089, 73.7654),  # (lat, lng)
    radius=2000,                   # meters
    categories=['Italian', 'Cafe'], # optional filter
    place_type='meals'             # 'meals'/'utilities'/'malls'
)
```

### 2. Get GPS Location
```python
location = get_current_gps_location()
# Returns: (latitude, longitude)
# Method: Local server → Browser GPS → Auto-capture
```

### 3. Create Map
```python
map_viewer.create_interactive_map(
    route_name='flame_to_fc_road',
    current_location=(lat, lng),
    restaurants=places_list,
    session_preferences=filters
)
map_viewer.save_and_open_map('map.html')
```

---

## 📊 Data Structure

### Place Object
```json
{
    "place_id": "ChIJxxx",
    "name": "Pizza Corner",
    "lat": 18.5123,
    "lng": 73.7689,
    "rating": 4.5,
    "user_ratings_total": 234,
    "price_level": 2,
    "categories": "Italian",
    "cuisine": "Italian",
    "types": ["restaurant", "food"],
    "open_now": true,
    "weekday_text": [
        "Monday: 11:00 AM – 11:00 PM",
        "Tuesday: 11:00 AM – 11:00 PM",
        ...
    ],
    "distance_from_current": 456,
    "neighborhood": "FC Road"
}
```

---

## 🎯 Category Mappings

### Meals (10 Cuisines)
```javascript
const cuisineKeywords = {
    'Italian': ['italian restaurant', 'pizza', 'pasta'],
    'Indian': ['indian restaurant', 'biryani', 'curry'],
    'Asian': ['chinese restaurant', 'japanese', 'thai', 'sushi'],
    'Mexican': ['mexican restaurant', 'taco'],
    'American': ['burger', 'bbq restaurant', 'steakhouse'],
    'Continental': ['continental', 'european', 'mediterranean'],
    'Street Food': ['street food', 'fast food'],
    'Healthy': ['healthy restaurant', 'salad bar', 'vegan'],
    'Desserts': ['dessert', 'bakery', 'ice cream'],
    'Cafe': ['cafe', 'coffee shop']
}
```

### Utilities (11 Types)
```javascript
const utilityKeywords = {
    'Grocery Store': ['grocery store', 'grocery'],
    'Supermarket': ['supermarket', 'super market'],
    'Convenience Store': ['convenience store', '7-eleven'],
    'Pharmacy': ['pharmacy', 'medical store', 'chemist'],
    'ATM/Bank': ['atm', 'bank'],
    'Gas Station': ['gas station', 'petrol pump', 'fuel station'],
    'Laundry': ['laundry', 'dry cleaning'],
    'Hardware Store': ['hardware store', 'hardware shop'],
    'Car Repair': ['car repair', 'auto repair', 'mechanic'],
    'Car Wash': ['car wash', 'car cleaning'],
    'Tailor': ['tailor', 'tailoring', 'alteration']
}
```

### Malls (4 Types)
```javascript
const mallKeywords = {
    'Shopping Mall': ['shopping mall', 'mall'],
    'Department Store': ['department store'],
    'Shopping Center': ['shopping center', 'shopping centre'],
    'Outlet Mall': ['outlet mall', 'outlet store']
}
```

---

## 🌐 API Endpoints (To Implement)

### POST /api/search
```javascript
{
    "lat": 18.5089,
    "lng": 73.7654,
    "radius": 2000,
    "category": "meals",
    "categories": ["Italian", "Cafe"],
    "filters": {
        "min_rating": 4.0,
        "min_reviews": 50,
        "max_price": 3,
        "max_distance": 1500
    }
}
```

### GET /api/route?name=flame_to_fc_road
```javascript
{
    "route_name": "flame_to_fc_road",
    "coordinates": [[18.5089, 73.7654], ...]
}
```

### POST /api/nearest-stop
```javascript
{
    "route_name": "flame_to_fc_road",
    "place_location": {"lat": 18.51, "lng": 73.77}
}
```

---

## 💻 Frontend Code Snippets

### GPS Detection
```javascript
async function detectGPS() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            pos => resolve({
                lat: pos.coords.latitude,
                lng: pos.coords.longitude,
                accuracy: pos.coords.accuracy
            }),
            error => reject(error),
            { enableHighAccuracy: true, timeout: 10000 }
        );
    });
}
```

### Live Tracking Hook (React)
```javascript
function useLiveLocation() {
    const [location, setLocation] = useState(null);
    
    useEffect(() => {
        const watchId = navigator.geolocation.watchPosition(
            pos => setLocation({
                lat: pos.coords.latitude,
                lng: pos.coords.longitude
            }),
            null,
            { enableHighAccuracy: true, maximumAge: 0 }
        );
        
        return () => navigator.geolocation.clearWatch(watchId);
    }, []);
    
    return location;
}
```

### Filter Function
```javascript
function applyFilters(places, filters) {
    return places.filter(p => {
        if (p.rating < filters.minRating) return false;
        if (p.user_ratings_total < filters.minReviews) return false;
        if (filters.maxPrice > 0 && p.price_level > filters.maxPrice) return false;
        if (p.distance_from_current > filters.maxDistance) return false;
        if (filters.categories.length > 0 && 
            !filters.categories.includes(p.cuisine)) return false;
        return true;
    });
}
```

---

## 🗺️ Map Integration (React-Leaflet)

```javascript
import { MapContainer, TileLayer, Marker, Polyline, Circle } from 'react-leaflet';

function AroundMeMap({ center, places, route, liveLocation }) {
    return (
        <MapContainer center={center} zoom={14}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            
            {/* Route */}
            <Polyline positions={route} color="blue" weight={5} />
            
            {/* Places */}
            {places.map(p => (
                <Marker key={p.place_id} position={[p.lat, p.lng]}>
                    <Popup>
                        <h4>{p.name}</h4>
                        <p>⭐ {p.rating} ({p.user_ratings_total} reviews)</p>
                        <p>{'₹'.repeat(p.price_level)}</p>
                        <p>{p.open_now ? '🟢 Open' : '🔴 Closed'}</p>
                    </Popup>
                </Marker>
            ))}
            
            {/* Live Location */}
            {liveLocation && (
                <>
                    <Circle 
                        center={liveLocation} 
                        radius={liveLocation.accuracy}
                        fillOpacity={0.1}
                    />
                    <Marker position={liveLocation} />
                </>
            )}
        </MapContainer>
    );
}
```

---

## 🎨 Filter UI States

### Rating Filter
```javascript
const ratingOptions = [
    { value: 0, label: 'Any rating' },
    { value: 3.5, label: '3.5+ ⭐' },
    { value: 4.0, label: '4.0+ ⭐⭐' },
    { value: 4.5, label: '4.5+ ⭐⭐⭐' }
];
```

### Price Filter
```javascript
const priceOptions = [
    { value: 0, label: 'Any price' },
    { value: 1, label: '₹ Budget' },
    { value: 2, label: '₹₹ Moderate' },
    { value: 3, label: '₹₹₹ Mid-range' },
    { value: 4, label: '₹₹₹₹ Premium' }
];
```

### Review Filter
```javascript
const reviewOptions = [
    { value: 0, label: 'Any reviews' },
    { value: 50, label: '50+ reviews' },
    { value: 100, label: '100+ reviews' },
    { value: 200, label: '200+ reviews' }
];
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
.search-container { width: 100%; }

/* Tablet */
@media (min-width: 768px) {
    .search-container { width: 50%; }
    .map-container { width: 50%; }
}

/* Desktop */
@media (min-width: 1024px) {
    .results-grid { 
        grid-template-columns: 1fr 2fr; 
        /* List | Map */
    }
}
```

---

## ⚡ Performance Tips

1. **Debounce filter changes** (300ms delay)
2. **Cluster markers** when zoomed out (>100 places)
3. **Lazy load place details** (on card click)
4. **Cache API responses** (5 min TTL)
5. **Paginate list view** (20 items per page)
6. **Throttle live tracking** (5 sec updates)

---

## 🔒 Security Checklist

- [ ] API key stored in backend only
- [ ] CORS restricted to your domain
- [ ] Rate limiting on search endpoint
- [ ] Input validation (lat/lng ranges)
- [ ] Sanitize user inputs
- [ ] HTTPS in production
- [ ] Environment variables for secrets

---

## 🧪 Testing Scenarios

### GPS Detection
- ✅ Desktop Chrome/Firefox/Safari
- ✅ Mobile iOS Safari
- ✅ Mobile Android Chrome
- ✅ Permission denied handling
- ✅ Timeout handling
- ✅ Fallback to manual input

### Search
- ✅ Empty results handling
- ✅ API error handling
- ✅ Invalid coordinates
- ✅ Large radius (>10km)
- ✅ No categories selected
- ✅ All filters at max

### Map
- ✅ Map loads correctly
- ✅ Markers render
- ✅ Popups display data
- ✅ Live tracking starts/stops
- ✅ Route displays
- ✅ Zoom/pan works

---

## 📞 Quick Commands

### Run Desktop App
```bash
cd aroundme
python launch_aroundme.py
```

### Test GPS Function
```python
from map_viewer import get_current_gps_location
location = get_current_gps_location()
print(location)  # (lat, lng)
```

### Test Search
```python
from integrated_aroundme_system import IntegratedAroundMeSystem
system = IntegratedAroundMeSystem('YOUR_API_KEY', False)
places = system.fetch_places_near_location(
    (18.5089, 73.7654), 1000, ['Italian'], 'meals'
)
print(places.head())
```

### Generate Sample JSON
```bash
python -c "
from integrated_aroundme_system import IntegratedAroundMeSystem
import json
system = IntegratedAroundMeSystem('YOUR_KEY', False)
df = system.fetch_places_near_location((18.5089, 73.7654), 1000, [], 'meals')
print(json.dumps(df.head(3).to_dict('records'), indent=2))
" > sample_data.json
```

---

## 🎯 User Flow

1. **Land** → See "Find places near you" CTA
2. **Click** → GPS auto-detects or manual input modal
3. **Choose** → Meals / Utilities / Malls tabs
4. **Select** → Multi-select checkboxes for types
5. **Adjust** → Radius slider (500m - 10km)
6. **Filter** → Optional: rating/price/reviews
7. **View** → Split: List (scrollable) + Map (interactive)
8. **Track** → Toggle live GPS tracking on map
9. **Click** → Place card/marker → Details + Google links
10. **Navigate** → Google Maps or call/directions

---

## 🔢 Current Stats

- **Total search types**: 25 (10 meals + 11 utilities + 4 malls)
- **Filter options**: 5 criteria × multiple values = 100+ combinations
- **Distance range**: 500m to 10km (custom supported)
- **API efficiency**: 1-2 calls per category (vs 36+ generic)
- **Map update rate**: 5 seconds (live tracking)
- **Coordinate precision**: 6 decimal places (~0.1m accuracy)

---

## 📚 Files You Need

### Backend (Priority 1)
1. `integrated_aroundme_system.py` - Core search logic
2. `map_viewer.py` - GPS + nearest stop functions

### Frontend Components (Priority 2)
3. GPS detection service
4. Search interface
5. Filter panel
6. Map component
7. Place list/cards

### Documentation (Reference)
8. `WEB_APP_INTEGRATION_GUIDE.md` - Full guide
9. `QUICK_REFERENCE.md` - This file

---

## ⏱️ Time Estimates

| Task | Hours | Priority |
|------|-------|----------|
| Backend API setup | 16-24 | HIGH |
| GPS service | 4-6 | HIGH |
| Map component | 12-16 | HIGH |
| Search UI | 8-12 | MEDIUM |
| Filters UI | 6-8 | MEDIUM |
| Place cards | 4-6 | MEDIUM |
| Live tracking | 6-8 | LOW |
| Testing | 12-16 | HIGH |
| **Total** | **68-96** | - |

---

*Version 3.0 | Last Updated: December 2, 2024*
