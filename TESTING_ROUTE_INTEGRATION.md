# Google Maps Route Integration - Testing Guide

## What's New

The system now fetches **REAL shuttle route coordinates from Google Maps API** instead of using hardcoded values.

### Architecture

```
[Map Demo UI]
    ↓ (Click "Load Recommendations")
    ↓
[fetchRealRouteCoordinates(token)]
    ↓ (GET /api/route/coordinates/?route=flame_to_fc_road)
    ↓
[Django Endpoint: route_coordinates_view]
    ↓ (Reads AROUNDME_GOOGLE_API_KEY from settings)
    ↓
[IntegratedAroundMeSystem.get_route_coordinates(route_name)]
    ↓ (Calls REAL Google Maps Directions API)
    ↓
[Google Maps API Returns]
    ↓ (Actual coordinates for FLAME → Bavdhan → Kothrud → FC)
    ↓
[Map Renders Real Route + 4 Waypoint Markers]
```

## Setup Instructions

### 1. Set Environment Variable with Your Google API Key

```powershell
$env:AROUNDME_GOOGLE_API_KEY = "AIzaSy..."  # Replace with your actual API key
```

Verify it's set:

```powershell
echo $env:AROUNDME_GOOGLE_API_KEY
```

### 2. Start Django Server

```powershell
cd c:\Users\Sneh Pahuja\backend
python manage.py runserver
```

### 3. Open Map Demo

Navigate to:

```
http://127.0.0.1:8000/api/map/aroundme/
```

## Testing the Integration

### Step 1: Verify API Endpoint Works

Test the new endpoint directly:

```powershell
$token = "your_jwt_token_here"  # Optional - for future auth
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/route/coordinates/?route=flame_to_fc_road" `
  -Headers @{"Authorization" = "Bearer $token"} `
  -Method GET | ConvertTo-Json
```

**Expected Response:**

```json
{
  "status": "success",
  "route_name": "flame_to_fc_road",
  "coordinates": [
    [18.5967, 73.7698],  # FLAME University
    [18.5450, 73.7500],  # Bavdhan area
    [18.5204, 73.8567],  # Kothrud area
    [18.5160, 73.8580],  # FC Road area
    ... (many intermediate points from Google Maps)
  ],
  "waypoints": 4,
  "num_points": N
}
```

### Step 2: Load Recommendations on Map

1. Go to http://127.0.0.1:8000/api/map/aroundme/
2. Leave defaults or enter:
   - **Algorithm**: `time` (or any option)
   - **Limit**: `25`
   - **Lat/Lng**: `18.5204, 73.8567` (Kothrud area)
3. Click **"Load Recommendations"**

### Step 3: Verify Route Display

**Expected Behavior:**

✅ **Real Route Visible**:

- Route line shows ACTUAL path from FLAME to Bavdhan to Kothrud to FC Road
- Coordinates match Google Maps Directions API output
- Smooth curved line (not jagged or wrong)

✅ **4 Waypoint Markers**:

- 🏫 **Green marker** at FLAME University (Gat No. 1270, Lavale, Off Pune Bangalore Highway)
- 🚌 **Orange markers** at intermediate stops (Bavdhan, Kothrud areas)
- 🅿️ **Red marker** at Val Gandarva Parking (1204/4, Jangali Maharaj Rd, Shivajinagar)

✅ **Marker Popups**:

- Click each marker → popup shows name and address
- Addresses should match real shuttle stops

✅ **Browser Console**:

- Should see: `✅ Loaded real route with N points from Google Maps`
- No errors about API key or route fetching

✅ **Recommendation Markers**:

- Green circles appear for recommended places
- Cluster detection works (grouping nearby points)

## Troubleshooting

### Issue: Map shows fallback route (interpolated, not real)

**Cause**: Either:

1. API key not set
2. Network error fetching from endpoint
3. Google API key invalid/expired

**Fix**:

1. Check console for error logs
2. Verify: `$env:AROUNDME_GOOGLE_API_KEY` is set
3. Test endpoint directly (see Step 1 above)
4. Check API key has "Maps Directions API" enabled in Google Cloud Console

### Issue: 404 Not Found on /api/route/coordinates/

**Cause**: URL route not registered in Django

**Fix**:

1. Verify `api/urls.py` has:
   ```python
   path("route/coordinates/", route_coordinates_view, name='route-coordinates'),
   ```
2. Verify `api/views.py` has `route_coordinates_view()` function defined
3. Restart server: `python manage.py runserver`

### Issue: Markers don't have addresses in popups

**Cause**: Fallback route array missing address fields

**Fix**:

- Verify `fallbackRoute` array in HTML has structure:

```javascript
{name: "Stop Name", address: "Full Address", lat: 18.xxx, lng: 73.xxx}
```

## Code Files Modified

1. **`api/views.py`**

   - Added: `route_coordinates_view()` function
   - Calls: `IntegratedAroundMeSystem.get_route_coordinates(route_name)`
   - Returns: Real coordinates from Google Maps Directions API

2. **`api/urls.py`**

   - Added: URL pattern for `/api/route/coordinates/`
   - Wires: `route_coordinates_view` endpoint

3. **`recommendations/static/recommendations/map_demo.html`**
   - Added: `routeCoordinatesCache` variable
   - Added: `fetchRealRouteCoordinates(token)` function
   - Updated: "Load Recommendations" button click handler to fetch route
   - Updated: `getSimulatedRoute()` to use cached coordinates or fallback
   - Updated: `drawShuttleRoute()` to render 4 waypoint markers with addresses

## Expected Timeline

- **Map loads**: Shows fallback route (interpolated)
- **"Load Recommendations" clicked**: Triggers `fetchRealRouteCoordinates(token)`
- **API endpoint called**: `/api/route/coordinates/?route=flame_to_fc_road`
- **Route fetched**: Real Google Maps coordinates received (~100-200 points)
- **Route cached**: Stored in `routeCoordinatesCache`
- **`drawShuttleRoute()` called**: Uses cached real coordinates
- **Map updates**: Shows actual FLAME → Bavdhan → Kothrud → FC Road path
- **Waypoint markers**: Rendered with correct addresses

## Success Criteria

✅ **Route is Correct**: Matches actual FLAME → Bavdhan → Kothrud → FC Road shuttle path
✅ **Coordinates from Google**: Not hardcoded, fetched from real Google Maps API
✅ **Waypoint Markers**: All 4 stops visible with addresses
✅ **Recommendations Render**: Place markers appear on map
✅ **Cluster Detection**: Works correctly
✅ **No Hardcoding**: All route data sourced from friend's code + Google API

---

**User's Request Met**: ✅ Using actual shuttle route coordinates from friend's code (which calls Google Maps API), not hardcoded values.
