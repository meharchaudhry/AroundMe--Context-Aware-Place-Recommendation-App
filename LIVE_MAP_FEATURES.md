# 🗺️ AroundMe Live Map Feature - Complete Guide

## Overview
The Live Map View helps you decide **where to get off the shuttle** by showing you:
- The exact shuttle route with FLAME Bus Point waypoint
- Your current GPS location
- Filtered restaurants based on your current craving/occasion
- Real-time distance from restaurants to help you decide where to exit

---

## 🎯 Key Features

### 1. **Session-Based Preferences (Occasion-Driven)**
Every time you use the map, you can set NEW preferences for the current occasion:

**Occasions:**
- Quick Bite (I'm hungry now!)
- Coffee/Study Session  
- Date/Romantic Dinner
- Friends Hangout
- Family Meal
- Business/Formal Lunch
- Late Night Cravings
- Just Exploring

**Why?** Your preferences change based on context! You might want:
- Italian for a date → Asian for late-night cravings
- Budget-friendly for quick bite → Premium for business lunch

### 2. **Live GPS Location Tracking**
- Enter your actual GPS coordinates (from Google Maps/phone)
- Map centers on YOUR location
- Shows 500m visibility radius around you
- Calculates exact walking distance to each restaurant

### 3. **Interactive Map Elements**

**Shuttle Route:**
- Blue line showing the full route
- Green marker (▶) at start point
- Red marker (⬛) at end point  
- Orange marker (🚌) at FLAME Bus Point (Bavdhan)

**Your Location:**
- Dark blue marker (📍) showing where you are
- Light blue circle showing 500m immediate area
- Updates in real-time when you move

**Restaurant Markers:**
- Color-coded by rating:
  - 🟢 Green: 4.5+ stars (Excellent)
  - 🟢 Light Green: 4.0-4.4 stars (Very Good)
  - 🟠 Orange: 3.5-3.9 stars (Good)
  - 🔴 Red: <3.5 stars (Average)
  
- Click any marker to see:
  - Restaurant name & ranking
  - Rating with star emojis
  - Price level (₹ symbols)
  - Distance from you (e.g., "247m from you")
  - AI algorithm used
  - Categories/cuisine type
  - Recommendation reason

### 4. **Smart Filtering**
Restaurants shown are filtered by:
- ✅ Your session occasion (date vs quick bite)
- ✅ Cuisine preferences (Asian, Italian, etc.)
- ✅ Budget for this meal
- ✅ AI algorithm (Time-based, Explore, Hybrid, Cluster)
- ✅ Distance from shuttle route

### 5. **Live Updates**

**Option 1: Update Location**
- Move along the shuttle route
- Enter new GPS coordinates
- Map refreshes with NEW distances
- Restaurants re-ranked by proximity

**Option 2: Change Preferences**
- Changed your mind? Want different food?
- Select new occasion/cuisine/budget
- Map refreshes with NEW filtered restaurants
- Same location, different recommendations

---

## 📱 How to Use

### Step 1: Launch Map Mode
```
Select algorithm (1-10): 8
```

### Step 2: Set Session Preferences
- Choose occasion (e.g., "Friends Hangout")
- Select cuisine(s) (e.g., "Asian")
- Set budget (e.g., "Moderate")

### Step 3: Enter GPS Location
```
Latitude: 18.5167
Longitude: 73.7700
```

### Step 4: Choose Filtering Algorithm
1. Time-Based → Best for current meal time
2. Explore Mode → Adventure, try new things
3. Hybrid → Balanced recommendations
4. Cluster-Based → Location + preferences

### Step 5: View Interactive Map
- Browser opens automatically
- Zoom, pan, click markers
- See shuttle route overlay
- Check distances from your location

### Step 6: Decide Where to Get Off!
**Decision Strategy:**
- See cluster of green markers? → Great area, get off here!
- Restaurant 247m away? → Easy walk from bus stop
- High ratings nearby? → Worth getting off early
- Multiple options close together? → Food street area!

### Step 7: Update as Needed
- Moving? → Update location (#1)
- Changed mind? → Update preferences (#2)
- Done? → Back to main menu (#3)

---

## 🎨 Map Features

### Legend (Top Right Corner)
Shows current session:
- Occasion selected
- Cuisines chosen  
- Budget range
- Rating color guide
- Map symbol meanings

### Interactive Tools
- **Fullscreen Mode** → Maximize map
- **Search Location** → Find specific places
- **Measure Tool** → Measure distances
- **Zoom Controls** → Get detailed view

---

## 💡 Use Cases

### Scenario 1: "Where should I eat lunch?"
1. Select: Quick Bite occasion
2. Choose: Indian cuisine  
3. Budget: Budget-friendly
4. Algorithm: Time-Based
5. **Result:** Map shows nearby South Indian/North Indian spots perfect for lunch

### Scenario 2: "Date night planning"
1. Select: Date/Romantic Dinner
2. Choose: Italian + Continental
3. Budget: Premium
4. Algorithm: Hybrid
5. **Result:** Map shows upscale romantic restaurants along route

### Scenario 3: "Late night on shuttle"
1. Select: Late Night Cravings
2. Choose: Street Food + Asian
3. Budget: Budget
4. Algorithm: Explore Mode
5. **Result:** Map shows open late-night spots + adventurous picks

### Scenario 4: "Study session with friends"  
1. Select: Coffee/Study Session
2. Choose: Cafe
3. Budget: Moderate
4. Algorithm: Cluster-Based
5. **Result:** Map shows cafes near FC Road/Koregaon Park with good ambience

---

## 🚀 Advanced Tips

### Getting the Best Results:
- **Be specific with occasion** → Better filtering
- **Use Explore Mode** → Discover new places
- **Check distance circles** → Walking vs auto distance
- **Look for marker clusters** → Popular food areas
- **Update live** → As you move on shuttle

### Deciding Where to Get Off:
1. Look for **green marker clusters** (high-rated areas)
2. Check **distance from bus stop** (< 500m = easy walk)
3. Consider **multiple options nearby** (backup choices)
4. Use **route convenience** score (closer to route = better)
5. See **price distribution** (mix of budgets)

### Pro Strategy:
- **Start of ride:** Check whole route on map
- **During ride:** Update location every 5-10 min
- **Near destination:** Switch to distance sorting
- **Changed plans:** Update preferences on-the-fly

---

## 📊 Technical Details

### Data Sources:
- Google Places API for restaurant data
- Google Directions API for shuttle route
- Real-time GPS for location tracking
- 6 AI algorithms for smart filtering

### Map Technology:
- Folium (Python) for interactive maps
- OpenStreetMap base layer
- HTML/JavaScript for interactivity
- Auto-opens in default browser

### Filtering Logic:
1. Get all restaurants within search radius (500m-5km)
2. Apply AI algorithm filtering (time/explore/hybrid/cluster)
3. Filter by session preferences (cuisine/budget/occasion)
4. Calculate distances from current GPS location
5. Sort by distance or rating
6. Display top 50 on map

---

## 🔄 Workflow Comparison

### Old Way (Text List):
❌ Just see restaurant names
❌ Don't know where they are
❌ Can't see route context
❌ Hard to decide where to get off

### New Way (Live Map):
✅ See restaurants ON the map
✅ Know exact location vs shuttle route  
✅ Visual spatial context
✅ Easy decision: "Get off at next stop!"

---

## 📝 Notes

- Map files saved as `aroundme_live_map.html`
- Can open saved maps later offline
- GPS coordinates can be from phone's location
- Works with both FLAME→FC and FC→FLAME routes
- Preferences are session-based (not saved to profile)
- Can switch algorithms on-the-fly

---

## 🎯 Future Enhancements (Ideas)

- [ ] Auto-detect GPS from mobile device
- [ ] "Get off here!" alerts when near good clusters
- [ ] Walking directions from bus stop to restaurant
- [ ] Real-time shuttle tracking integration
- [ ] Save favorite "get off" spots
- [ ] Share map link with friends
- [ ] Restaurant photos on map markers
- [ ] Filter by "open now" status
- [ ] Show busy times/wait times

---

**Enjoy exploring with AroundMe Live Map! 🗺️🍽️**
