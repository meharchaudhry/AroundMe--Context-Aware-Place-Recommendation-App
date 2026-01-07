"""
AroundMe Live Map Viewer
Interactive map showing shuttle route, current location, and filtered restaurants
"""

import folium
from folium import plugins
import webbrowser
import os
from typing import Dict, List, Tuple
import time
from datetime import datetime
from geopy.distance import geodesic
import numpy as np

class AroundMeMapViewer:
    def __init__(self, system):
        """Initialize map viewer with the AroundMe system"""
        self.system = system
        self.map = None
        self.current_location = None
        self.route_coords = []
        self.filtered_restaurants = []
        
    def create_interactive_map(self, route_name: str, current_location: Tuple[float, float],
                              restaurants: List[Dict], session_preferences: Dict):
        """
        Create an interactive HTML map with shuttle route and restaurants
        
        Args:
            route_name: Name of the shuttle route
            current_location: (lat, lng) of current position
            restaurants: List of restaurant recommendations
            session_preferences: Current session's filter preferences (occasion-based)
        """
        # Get route coordinates
        self.route_coords = self.system.get_route_coordinates(route_name)
        self.current_location = current_location
        self.filtered_restaurants = restaurants
        
        # Calculate map center (midpoint of route or current location)
        if current_location:
            center_lat, center_lng = current_location
        elif self.route_coords:
            center_lat = sum(coord[0] for coord in self.route_coords) / len(self.route_coords)
            center_lng = sum(coord[1] for coord in self.route_coords) / len(self.route_coords)
        else:
            center_lat, center_lng = 18.5167, 73.7700  # Default Pune center
        
        # Create base map
        self.map = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=14,
            tiles='OpenStreetMap'
        )
        
        # Add shuttle route line
        if self.route_coords:
            folium.PolyLine(
                locations=self.route_coords,
                color='blue',
                weight=5,
                opacity=0.8,
                popup=f'<b>{route_name.replace("_", " ").title()} Route</b>',
                tooltip='FLAME Shuttle Route'
            ).add_to(self.map)
            
            # Add route start/end markers
            folium.Marker(
                location=self.route_coords[0],
                popup='<b>Route Start</b>',
                icon=folium.Icon(color='green', icon='play', prefix='fa'),
                tooltip='Start Point'
            ).add_to(self.map)
            
            folium.Marker(
                location=self.route_coords[-1],
                popup='<b>Route End</b>',
                icon=folium.Icon(color='red', icon='stop', prefix='fa'),
                tooltip='End Point'
            ).add_to(self.map)
            
            # Add FLAME Bus Point waypoint if present
            if len(self.route_coords) > 2:
                mid_idx = len(self.route_coords) // 2
                folium.Marker(
                    location=self.route_coords[mid_idx],
                    popup='<b>🚌 FLAME Bus Point</b><br>Bavdhan',
                    icon=folium.Icon(color='orange', icon='bus', prefix='fa'),
                    tooltip='FLAME Bus Point - Bavdhan'
                ).add_to(self.map)
        
        # Add current location marker with pulsing circle
        if current_location:
            # Static marker for initial position
            folium.Marker(
                location=current_location,
                popup=f'<b>📍 You are here</b><br>{datetime.now().strftime("%H:%M:%S")}',
                icon=folium.Icon(color='darkblue', icon='user', prefix='fa'),
                tooltip='Your Current Location'
            ).add_to(self.map)
            
            # Add pulsing circle to show current location
            folium.CircleMarker(
                location=current_location,
                radius=15,
                color='blue',
                fill=True,
                fillColor='blue',
                fillOpacity=0.3,
                popup='Your location',
                tooltip='Live location tracking enabled'
            ).add_to(self.map)
            
            # Add current location circle (visibility radius)
            folium.Circle(
                location=current_location,
                radius=500,  # 500m radius
                color='lightblue',
                fill=True,
                fillOpacity=0.1,
                popup='500m visibility radius',
                tooltip='Your immediate area'
            ).add_to(self.map)
        
        # Detect restaurant clusters and add "Get off here!" recommendations
        self._add_cluster_recommendations(restaurants)
        
        # Add restaurant markers with color coding
        self._add_restaurant_markers(restaurants, session_preferences)
        
        # Add legend
        self._add_legend(session_preferences)
        
        # Add fullscreen option
        plugins.Fullscreen().add_to(self.map)
        
        # Add location search
        plugins.Geocoder().add_to(self.map)
        
        # Add measure tool
        plugins.MeasureControl(position='bottomleft').add_to(self.map)
        
        return self.map
    
    def _find_nearest_shuttle_stop(self, restaurant_location: Tuple[float, float]) -> Dict:
        """Find the nearest shuttle stop to a restaurant"""
        if not self.route_coords:
            return None
        
        min_distance = float('inf')
        nearest_stop = None
        stop_index = -1
        
        # Check each route point
        for i, route_point in enumerate(self.route_coords):
            distance = geodesic(restaurant_location, route_point).meters
            if distance < min_distance:
                min_distance = distance
                nearest_stop = route_point
                stop_index = i
        
        # Determine stop name based on route position
        total_stops = len(self.route_coords)
        if stop_index == 0:
            stop_name = "Route Start"
        elif stop_index == total_stops - 1:
            stop_name = "Route End"
        elif stop_index == total_stops // 2:
            stop_name = "FLAME Bus Point (Bavdhan)"
        else:
            # Calculate percentage along route
            percent = int((stop_index / total_stops) * 100)
            stop_name = f"Stop {stop_index + 1} ({percent}% along route)"
        
        return {
            'location': nearest_stop,
            'distance': min_distance,
            'name': stop_name,
            'index': stop_index
        }
    
    def _add_cluster_recommendations(self, restaurants: List[Dict]):
        """Detect high-density restaurant clusters and mark optimal get-off points"""
        if not restaurants or not self.route_coords:
            return
        
        # Find clusters of restaurants (density-based)
        clusters = []
        
        # For each route point, count nearby high-quality restaurants
        for route_point in self.route_coords:
            nearby_restaurants = []
            total_quality_score = 0
            
            for restaurant in restaurants:
                rest_location = (restaurant['lat'], restaurant['lng'])
                distance = geodesic(route_point, rest_location).meters
                
                # Consider restaurants within 200m of this route point
                if distance <= 200:
                    # Quality score: rating * (1 - distance/200)
                    rating = restaurant.get('rating', 3.0)
                    distance_factor = 1 - (distance / 200)
                    quality_score = rating * distance_factor
                    total_quality_score += quality_score
                    nearby_restaurants.append(restaurant)
            
            # If this route point has 3+ restaurants nearby, it's a cluster
            if len(nearby_restaurants) >= 3:
                clusters.append({
                    'location': route_point,
                    'restaurant_count': len(nearby_restaurants),
                    'quality_score': total_quality_score,
                    'restaurants': nearby_restaurants
                })
        
        # Sort clusters by quality score and take top 3
        clusters.sort(key=lambda x: x['quality_score'], reverse=True)
        top_clusters = clusters[:3]
        
        print(f"\n🎯 Found {len(clusters)} restaurant clusters, showing top {len(top_clusters)}:")
        
        # Add cluster markers to map
        for i, cluster in enumerate(top_clusters, 1):
            lat, lng = cluster['location']
            count = cluster['restaurant_count']
            score = cluster['quality_score']
            
            # Get restaurant names in this cluster
            restaurant_names = [r['name'] for r in cluster['restaurants'][:5]]
            restaurant_list = '<br>'.join([f"• {name}" for name in restaurant_names])
            if len(cluster['restaurants']) > 5:
                restaurant_list += f"<br>• ...and {len(cluster['restaurants']) - 5} more"
            
            # Create popup HTML
            popup_html = f"""
            <div style='width: 250px; font-family: Arial, sans-serif;'>
                <h3 style='color: #FF6B6B; margin: 0; padding-bottom: 8px; border-bottom: 2px solid #FF6B6B;'>
                    🎯 GET OFF HERE! (Stop #{i})
                </h3>
                <p style='margin: 8px 0;'>
                    <b>{count} restaurants</b> within 200m walking distance<br>
                    <b>Quality Score:</b> {score:.1f}/5.0
                </p>
                <p style='margin: 8px 0;'><b>Top restaurants nearby:</b></p>
                <div style='font-size: 12px; line-height: 1.4;'>
                    {restaurant_list}
                </div>
            </div>
            """
            
            # Add prominent marker
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"🎯 Stop #{i}: {count} restaurants nearby!",
                icon=folium.Icon(color='darkred', icon='star', prefix='fa')
            ).add_to(self.map)
            
            # Add circle to show cluster area
            folium.Circle(
                location=[lat, lng],
                radius=200,
                color='#FF6B6B',
                fill=True,
                fillOpacity=0.15,
                weight=2,
                dashArray='5, 5',
                popup=f'Cluster zone: {count} restaurants'
            ).add_to(self.map)
            
            print(f"  Stop #{i}: {count} restaurants, Quality: {score:.1f} - {restaurant_names[0]}, etc.")
    
    def _add_restaurant_markers(self, restaurants: List[Dict], preferences: Dict):
        """Add restaurant markers to the map with smart color coding"""
        
        for i, restaurant in enumerate(restaurants, 1):
            lat, lng = restaurant['lat'], restaurant['lng']
            name = restaurant['name']
            rating = restaurant.get('rating', 0)
            price = restaurant.get('price_level', 2)
            distance = restaurant.get('distance_from_current', 0)
            algorithm = restaurant.get('algorithm', 'unknown')
            open_now = restaurant.get('open_now', None)
            weekday_text = restaurant.get('weekday_text', [])
            
            # Color code by rating
            if rating >= 4.5:
                color = 'green'
                rating_emoji = '⭐⭐⭐⭐⭐'
            elif rating >= 4.0:
                color = 'lightgreen'
                rating_emoji = '⭐⭐⭐⭐'
            elif rating >= 3.5:
                color = 'orange'
                rating_emoji = '⭐⭐⭐'
            else:
                color = 'red'
                rating_emoji = '⭐⭐'
            
            # Price indicators
            price_indicator = '₹' * int(price)
            
            # Distance formatting
            if distance < 1000:
                distance_str = f"{int(distance)}m"
            else:
                distance_str = f"{distance/1000:.1f}km"
            
            # Find nearest shuttle stop
            rest_location = (lat, lng)
            nearest_stop = self._find_nearest_shuttle_stop(rest_location)
            
            # Create Google Maps and Search links
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_id={restaurant.get('place_id', '')}"
            google_search_url = f"https://www.google.com/search?q={name.replace(' ', '+')}"
            
            # Format opening hours info
            if open_now is True:
                hours_status = '<span style="color: #2e7d32; font-weight: bold;">🟢 Open Now</span>'
            elif open_now is False:
                hours_status = '<span style="color: #c62828; font-weight: bold;">🔴 Closed</span>'
            else:
                hours_status = '<span style="color: #757575;">⚪ Hours Unknown</span>'
            
            # Get today's hours
            today_hours_html = ""
            if weekday_text:
                from datetime import datetime
                today_index = datetime.now().weekday()  # Monday=0, Sunday=6
                google_today_index = (today_index + 1) % 7  # Adjust to Google's Sunday=0 format
                if google_today_index < len(weekday_text):
                    today_hours = weekday_text[google_today_index]
                    today_hours_html = f'<br><b>🕒 Today:</b> {today_hours}'
            
            hours_info = f"""
            <div style="background-color: #e3f2fd; padding: 8px; margin: 8px 0; border-radius: 4px; border-left: 4px solid #2196f3;">
                <span style="font-size: 13px;">
                    {hours_status}{today_hours_html}
                </span>
            </div>
            """
            
            # Format shuttle stop info
            if nearest_stop:
                stop_distance = nearest_stop['distance']
                if stop_distance < 1000:
                    stop_dist_str = f"{int(stop_distance)}m"
                else:
                    stop_dist_str = f"{stop_distance/1000:.1f}km"
                
                shuttle_info = f"""
                <div style="background-color: #fff3cd; padding: 8px; margin: 8px 0; border-radius: 4px; border-left: 4px solid #ffc107;">
                    <b style="color: #856404;">🚌 Nearest Shuttle Stop:</b><br>
                    <span style="font-size: 13px;">
                        📍 {nearest_stop['name']}<br>
                        🚶 {stop_dist_str} walk from stop
                    </span>
                </div>
                """
            else:
                shuttle_info = ""
            
            # Create popup content
            popup_html = f"""
            <div style="width: 300px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0; color: #2c3e50; padding-bottom: 8px; border-bottom: 2px solid #3498db;">#{i}. {name}</h4>
                <p style="margin: 8px 0; font-size: 13px;">
                    <b>Rating:</b> {rating_emoji} ({rating}/5.0)<br>
                    <b>Price:</b> {price_indicator}<br>
                    <b>Distance:</b> 🚶 {distance_str} from you<br>
                    <b>Categories:</b> {restaurant.get('categories', 'N/A')}
                </p>
                {hours_info}
                {shuttle_info}
                <div style="margin: 10px 0; padding: 8px; background-color: #e8f5e9; border-radius: 4px;">
                    <a href="{google_maps_url}" target="_blank" style="display: inline-block; padding: 6px 12px; background-color: #4285f4; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; margin-right: 5px;">
                        🗺️ Open in Google Maps
                    </a>
                    <a href="{google_search_url}" target="_blank" style="display: inline-block; padding: 6px 12px; background-color: #34a853; color: white; text-decoration: none; border-radius: 4px; font-size: 12px;">
                        🔍 Google Search
                    </a>
                </div>
                <p style="margin: 8px 0; font-style: italic; color: #7f8c8d; font-size: 12px;">
                    💡 {restaurant.get('reasoning', 'Recommended for you')}
                </p>
            </div>
            """
            
            # Create marker with shuttle stop info in tooltip
            if nearest_stop:
                tooltip_text = f"#{i}. {name} - {rating}★ - {distance_str} | 🚌 {nearest_stop['name']}"
            else:
                tooltip_text = f"#{i}. {name} - {rating}★ - {distance_str}"
            
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=350),
                icon=folium.Icon(
                    color=color,
                    icon='cutlery',
                    prefix='fa'
                ),
                tooltip=tooltip_text
            ).add_to(self.map)
            
            # Add numbered circle marker for better visibility
            folium.CircleMarker(
                location=[lat, lng],
                radius=8,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                popup=f"#{i}",
                weight=2
            ).add_to(self.map)
    
    def _add_legend(self, preferences: Dict):
        """Add legend showing current filters and color coding"""
        
        occasion = preferences.get('occasion', 'General Dining')
        cuisines = preferences.get('cuisines_display', 'All')
        budget = preferences.get('budget_display', 'All')
        
        legend_html = f'''
        <div style="
            position: fixed; 
            top: 10px; right: 10px; 
            width: 280px; 
            background-color: white; 
            border: 2px solid #2c3e50;
            border-radius: 5px;
            z-index: 9999;
            padding: 10px;
            font-family: Arial, sans-serif;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        ">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                🍽️ AroundMe Live Map
            </h4>
            
            <div style="margin: 8px 0;">
                <b>📍 Current Session:</b><br>
                <span style="color: #7f8c8d;">Occasion: {occasion}</span><br>
                <span style="color: #7f8c8d;">Cuisines: {cuisines}</span><br>
                <span style="color: #7f8c8d;">Budget: {budget}</span>
            </div>
            
            <hr style="margin: 8px 0;">
            
            <div style="margin: 8px 0;">
                <b>🎨 Rating Colors:</b><br>
                <span style="color: green;">● 4.5+ ⭐⭐⭐⭐⭐</span><br>
                <span style="color: lightgreen;">● 4.0-4.4 ⭐⭐⭐⭐</span><br>
                <span style="color: orange;">● 3.5-3.9 ⭐⭐⭐</span><br>
                <span style="color: red;">● &lt;3.5 ⭐⭐</span>
            </div>
            
            <hr style="margin: 8px 0;">
            
            <div style="margin: 8px 0; font-size: 11px;">
                <b>🗺️ Map Legend:</b><br>
                <span style="color: blue;">━━ Shuttle Route</span><br>
                <span style="color: darkblue;">📍 Your Location</span><br>
                <span style="color: orange;">🚌 Bus Stop</span><br>
                <span style="color: green;">▶ Start Point</span><br>
                <span style="color: red;">⬛ End Point</span><br>
                <span style="color: darkred;">⭐ Get Off Here!</span>
            </div>
        </div>
        '''
        
        self.map.get_root().html.add_child(folium.Element(legend_html))
    
    def save_and_open_map(self, filename: str = "aroundme_live_map.html"):
        """Save the map to HTML file with live GPS tracking and open in browser"""
        if self.map:
            filepath = os.path.join(os.getcwd(), filename)
            self.map.save(filepath)
            
            # Add live GPS tracking script to the HTML
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Insert GPS tracking JavaScript before closing body tag
            gps_tracking_script = """
            <script>
            // Live GPS tracking
            var liveLocationMarker = null;
            var liveLocationCircle = null;
            var trackingInterval = null;
            var isTracking = false;
            var watchId = null;
            
            function startTracking() {
                if (navigator.geolocation) {
                    console.log('Starting GPS tracking...');
                    isTracking = true;
                    
                    // Watch position for continuous updates
                    watchId = navigator.geolocation.watchPosition(
                        updatePosition,
                        handleError,
                        {enableHighAccuracy: true, maximumAge: 0, timeout: 10000}
                    );
                } else {
                    alert('Geolocation is not supported by your browser');
                }
            }
            
            function updatePosition(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                var accuracy = position.coords.accuracy;
                
                console.log('Live position:', lat, lng, 'accuracy:', accuracy + 'm');
                
                // Remove old marker if exists
                if (liveLocationMarker) {
                    map.removeLayer(liveLocationMarker);
                }
                if (liveLocationCircle) {
                    map.removeLayer(liveLocationCircle);
                }
                
                // Create new pulsing marker
                liveLocationMarker = L.marker([lat, lng], {
                    icon: L.divIcon({
                        className: 'live-location-marker',
                        html: '<div class="pulse-marker"></div>',
                        iconSize: [20, 20]
                    }),
                    zIndexOffset: 1000
                }).addTo(map);
                
                var timestamp = new Date().toLocaleTimeString();
                liveLocationMarker.bindPopup('<b>🔴 LIVE LOCATION</b><br>Updated: ' + timestamp + '<br><small>Accuracy: ±' + Math.round(accuracy) + 'm</small>');
                
                // Add accuracy circle
                liveLocationCircle = L.circle([lat, lng], {
                    radius: accuracy,
                    color: '#4285F4',
                    fillColor: '#4285F4',
                    fillOpacity: 0.1,
                    weight: 1
                }).addTo(map);
                
                // Auto-pan to location on first update
                if (!liveLocationMarker._hasPanned) {
                    map.panTo([lat, lng]);
                    liveLocationMarker._hasPanned = true;
                }
            }
            
            function handleError(error) {
                var errorMsg = 'GPS Error: ';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg += 'Location permission denied';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg += 'Location unavailable';
                        break;
                    case error.TIMEOUT:
                        errorMsg += 'Request timed out';
                        break;
                    default:
                        errorMsg += 'Unknown error';
                }
                console.error(errorMsg);
                alert(errorMsg + '. Please check browser permissions.');
            }
            
            function stopTracking() {
                isTracking = false;
                if (watchId) {
                    navigator.geolocation.clearWatch(watchId);
                    watchId = null;
                }
                console.log('GPS tracking stopped');
            }
            
            // Add tracking control button
            var trackingControl = L.control({position: 'topright'});
            trackingControl.onAdd = function(map) {
                var div = L.DomUtil.create('div', 'tracking-control');
                div.innerHTML = '<button id="trackBtn" class="track-btn">📍 Start Live Tracking</button>';
                return div;
            };
            trackingControl.addTo(map);
            
            // Add tracking toggle
            setTimeout(function() {
                var btn = document.getElementById('trackBtn');
                if (btn) {
                    btn.addEventListener('click', function() {
                        if (!isTracking) {
                            startTracking();
                            this.innerHTML = '⏸️ Stop Tracking';
                            this.classList.add('tracking-active');
                        } else {
                            stopTracking();
                            this.innerHTML = '📍 Start Live Tracking';
                            this.classList.remove('tracking-active');
                        }
                    });
                }
            }, 100);
            
            // Add CSS styles
            var style = document.createElement('style');
            style.innerHTML = `
                @keyframes pulse {
                    0%, 100% { transform: scale(1); opacity: 1; }
                    50% { transform: scale(1.3); opacity: 0.7; }
                }
                .pulse-marker {
                    width: 20px;
                    height: 20px;
                    background: #4285F4;
                    border: 3px solid white;
                    border-radius: 50%;
                    box-shadow: 0 0 15px rgba(66,133,244,0.8);
                    animation: pulse 2s infinite;
                }
                .track-btn {
                    padding: 10px 15px;
                    background: white;
                    border: 2px solid #ddd;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    transition: all 0.3s;
                }
                .track-btn:hover {
                    background: #f0f0f0;
                    transform: translateY(-1px);
                    box-shadow: 0 3px 6px rgba(0,0,0,0.3);
                }
                .track-btn.tracking-active {
                    background: #4285F4;
                    color: white;
                    border-color: #4285F4;
                }
            `;
            document.head.appendChild(style);
            </script>
            """
            
            # Insert before closing body tag
            html_content = html_content.replace('</body>', gps_tracking_script + '</body>')
            
            # Write modified HTML
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n🗺️ Map saved to: {filepath}")
            print("🌐 Opening map in your browser...")
            print("💡 TIP: Click 'Start Live Tracking' button to track your location in real-time on the shuttle route!")
            
            # Open in default browser
            webbrowser.open('file://' + filepath, new=2)
            
            return filepath
        else:
            print("❌ No map created yet!")
            return None
    
    def update_location_and_refresh(self, new_location: Tuple[float, float],
                                   route_name: str, restaurants: List[Dict],
                                   preferences: Dict):
        """Update current location and refresh the map"""
        print(f"\n📍 Updating location to: {new_location}")
        self.create_interactive_map(route_name, new_location, restaurants, preferences)
        return self.save_and_open_map(f"aroundme_map_{int(time.time())}.html")


def get_session_preferences():
    """
    Quick preference collection for the current session/occasion
    Different from user profile - this is for the immediate dining need
    """
    print("\n" + "="*60)
    print("🎯 WHAT ARE YOU IN THE MOOD FOR RIGHT NOW?")
    print("="*60)
    
    preferences = {}
    
    # Occasion/Context
    print("\n🎭 What's the occasion for this meal?")
    occasions = [
        "Quick Bite (I'm hungry now!)",
        "Coffee/Study Session",
        "Date/Romantic Dinner",
        "Friends Hangout",
        "Family Meal",
        "Business/Formal Lunch",
        "Late Night Cravings",
        "Just Exploring"
    ]
    for i, occasion in enumerate(occasions, 1):
        print(f"{i}. {occasion}")
    
    while True:
        try:
            occ_choice = input(f"\nSelect occasion (1-{len(occasions)}, or Enter for Quick Bite): ").strip()
            if not occ_choice:
                preferences['occasion'] = occasions[0]
                break
            occ_idx = int(occ_choice) - 1
            if 0 <= occ_idx < len(occasions):
                preferences['occasion'] = occasions[occ_idx]
                break
            print(f"❌ Please enter 1-{len(occasions)}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Quick cuisine filter
    cuisines_list = [
        "Italian", "Indian", "Asian", "Mexican", "American", 
        "Continental", "Street Food", "Healthy/Organic", "Desserts/Bakery", "Cafe"
    ]
    print("\n🍽️ What cuisine(s) are you craving? (multiple: e.g., 1,3,5)")
    for i, cuisine in enumerate(cuisines_list, 1):
        print(f"{i}. {cuisine}")
    
    while True:
        try:
            cuisine_input = input(f"\nEnter choice(s) (1-{len(cuisines_list)}, or Enter for all): ").strip()
            if not cuisine_input:
                preferences['cuisines'] = "all"
                preferences['cuisines_display'] = "All Cuisines"
                break
            
            choices = [int(x.strip()) - 1 for x in cuisine_input.split(',')]
            if all(0 <= c < len(cuisines_list) for c in choices):
                selected = [cuisines_list[c] for c in choices]
                preferences['cuisines'] = ','.join(selected)
                preferences['cuisines_display'] = ', '.join(selected)
                break
            print(f"❌ Invalid choices")
        except ValueError:
            print("❌ Please enter valid numbers")
    
    # Budget for this session
    print("\n💰 Budget for this meal?")
    budgets = ["Budget (₹100-300)", "Moderate (₹300-600)", "Premium (₹600-1000)", "Luxury (₹1000+)"]
    for i, budget in enumerate(budgets, 1):
        print(f"{i}. {budget}")
    
    while True:
        try:
            budget_input = input(f"\nEnter choice (1-{len(budgets)}, or Enter for all): ").strip()
            if not budget_input:
                preferences['budget'] = [1, 2, 3, 4]
                preferences['budget_display'] = "All Budgets"
                break
            budget_choice = int(budget_input)
            if 1 <= budget_choice <= len(budgets):
                preferences['budget'] = [budget_choice]
                preferences['budget_display'] = budgets[budget_choice - 1]
                break
            print(f"❌ Please enter 1-{len(budgets)}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return preferences


def get_current_gps_location():
    """Get current GPS location with option for automatic or manual entry"""
    print("\n📍 How would you like to provide your location?")
    print("1. 🤖 Auto-detect (use device GPS)")
    print("2. ✍️  Enter manually")
    
    while True:
        choice = input("\nSelect option (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("❌ Please enter 1 or 2")
    
    if choice == '1':
        # Use browser-based GPS with local server for automatic capture
        print("\n🔍 Starting GPS detection server...")
        print("💡 Your browser will open - just click 'Allow' for location access")
        
        import socket
        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import webbrowser
        import json
        
        # Shared variable to store detected coordinates
        detected_coords = {'lat': None, 'lng': None, 'ready': False}
        
        class GPSHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress log messages
            
            def do_GET(self):
                if self.path == '/':
                    # Serve the GPS detection page
                    html = """<!DOCTYPE html>
<html>
<head>
    <title>GPS Detection</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }
        h1 { color: #333; margin-bottom: 20px; }
        .status { font-size: 18px; margin: 20px 0; color: #666; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .success { color: #28a745; font-weight: bold; font-size: 20px; }
        .coords {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 GPS Location Detection</h1>
        <div id="status" class="status">Requesting location access...</div>
        <div id="spinner" class="spinner"></div>
        <div id="result" style="display:none;"></div>
    </div>
    <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    var lat = position.coords.latitude;
                    var lng = position.coords.longitude;
                    var accuracy = position.coords.accuracy;
                    
                    // Send coordinates back to server
                    fetch('/coords?lat=' + lat + '&lng=' + lng + '&acc=' + accuracy)
                        .then(function() {
                            document.getElementById('spinner').style.display = 'none';
                            document.getElementById('status').innerHTML = '<span class="success">✅ Location detected!</span>';
                            document.getElementById('result').innerHTML = 
                                '<div class="coords">' +
                                '<b>Latitude:</b> ' + lat.toFixed(6) + '<br>' +
                                '<b>Longitude:</b> ' + lng.toFixed(6) + '<br>' +
                                '<small>Accuracy: ±' + Math.round(accuracy) + 'm</small>' +
                                '</div>' +
                                '<p>You can close this window now.</p>';
                            document.getElementById('result').style.display = 'block';
                        });
                },
                function(error) {
                    document.getElementById('spinner').style.display = 'none';
                    var msg = '';
                    switch(error.code) {
                        case error.PERMISSION_DENIED: msg = 'Location access denied'; break;
                        case error.POSITION_UNAVAILABLE: msg = 'Location unavailable'; break;
                        case error.TIMEOUT: msg = 'Request timeout'; break;
                        default: msg = 'Unknown error';
                    }
                    document.getElementById('status').innerHTML = '<span style="color: #dc3545">❌ ' + msg + '</span>';
                    fetch('/error?msg=' + encodeURIComponent(msg));
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            document.getElementById('status').innerHTML = '<span style="color: #dc3545">❌ Geolocation not supported</span>';
            fetch('/error?msg=not_supported');
        }
    </script>
</body>
</html>"""
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
                
                elif self.path.startswith('/coords?'):
                    # Parse coordinates from query string
                    from urllib.parse import parse_qs, urlparse
                    query = parse_qs(urlparse(self.path).query)
                    detected_coords['lat'] = float(query['lat'][0])
                    detected_coords['lng'] = float(query['lng'][0])
                    detected_coords['ready'] = True
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')
                
                elif self.path.startswith('/error?'):
                    detected_coords['ready'] = True
                    detected_coords['error'] = True
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')
        
        try:
            # Find available port
            port = 8765
            server = HTTPServer(('localhost', port), GPSHandler)
            
            # Start server in background thread
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            # Open browser
            url = f'http://localhost:{port}'
            webbrowser.open(url)
            
            print(f"✅ Browser opened at {url}")
            print("⏳ Waiting for GPS detection (this happens automatically)...")
            
            # Wait for coordinates (max 30 seconds)
            import time
            timeout = 30
            elapsed = 0
            while not detected_coords['ready'] and elapsed < timeout:
                time.sleep(0.5)
                elapsed += 0.5
            
            # Shutdown server
            server.shutdown()
            
            if detected_coords.get('error'):
                print("\n⚠️ GPS detection failed in browser")
                print("📝 Let's enter coordinates manually...")
            elif detected_coords['lat'] and detected_coords['lng']:
                lat = detected_coords['lat']
                lng = detected_coords['lng']
                print(f"\n✅ Location automatically detected: ({lat:.6f}, {lng:.6f})")
                
                # Validate coordinates
                if 18.0 <= lat <= 19.0 and 73.0 <= lng <= 74.5:
                    confirm = input("Use this location? (y/n): ").strip().lower()
                    if confirm == 'y' or confirm == '':
                        return (lat, lng)
                else:
                    print("⚠️ Coordinates outside Pune area")
                    confirm = input("Use anyway? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return (lat, lng)
                
                print("\n📝 Let's enter manually instead...")
            else:
                print("\n⏱️ Detection timed out")
                print("📝 Let's enter coordinates manually...")
                
        except Exception as e:
            print(f"\n⚠️ Auto-detection error: {e}")
            print("📝 Let's enter manually instead...")
    
    # Manual entry
    print("\n📍 Enter your GPS coordinates:")
    print("💡 Tip: You can find coordinates from Google Maps (right-click → Copy coordinates)")
    print("\nCommon FLAME locations:")
    print("  - FLAME University: 18.5089, 73.7654")
    print("  - FLAME Bus Point (Bavdhan): 18.5058, 73.7687")
    print("  - FC Road: 18.5204, 73.8567")
    
    while True:
        try:
            lat_str = input("\nLatitude (e.g., 18.5089): ").strip()
            lng_str = input("Longitude (e.g., 73.7654): ").strip()
            
            if not lat_str or not lng_str:
                print("❌ Please enter both coordinates")
                continue
            
            lat = float(lat_str)
            lng = float(lng_str)
            
            # Validate coordinates are reasonable for Pune area
            if 18.0 <= lat <= 19.0 and 73.0 <= lng <= 74.5:
                print(f"✅ Location set: ({lat:.4f}, {lng:.4f})")
                return (lat, lng)
            else:
                print("⚠️ Coordinates seem outside Pune area. Please verify.")
                retry = input("Continue anyway? (y/n): ").strip().lower()
                if retry == 'y':
                    return (lat, lng)
        except ValueError:
            print("❌ Invalid format. Please enter numeric coordinates.")
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user")
            return None
        except ValueError:
            print("   ❌ Invalid coordinates. Please enter numbers.")
