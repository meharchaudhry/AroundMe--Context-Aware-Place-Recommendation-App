"""
AroundMe Integrated System v3.0 - AI Recommendations + Google Places API
Combines sophisticated recommendation algorithms with real-world data
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
import requests
import json
from geopy.distance import geodesic
import os
from typing import Dict, List, Tuple, Optional

class IntegratedAroundMeSystem:
    def __init__(self, google_api_key: str, use_synthetic_data: bool = True):
        """
        Initialize the integrated system
        
        Args:
            google_api_key: Your Google Maps API key
            use_synthetic_data: If True, uses synthetic data for development/testing
                               If False, uses real Google Places API data
        """
        self.google_api_key = google_api_key
        self.use_synthetic_data = use_synthetic_data
        
        # Initialize data sources
        if use_synthetic_data:
            self._load_synthetic_data()
        else:
            self.places = pd.DataFrame()  # Will be populated from Google Places
            self.users = pd.DataFrame()   # Will be managed locally
            self.interactions = pd.DataFrame()  # Will be tracked locally
        
        self.current_user_file = "current_user.txt"
        
        # Predefined shuttle routes (can be expanded)
        self.shuttle_routes = {
            "flame_to_fc_road": {
                "origin": "FLAME University, Pune",
                "waypoints": ["FLAME Bus Point, Bavdhan, Pune"],
                "destination": "FC Road, Pune"
            },
            "fc_road_to_flame": {
                "origin": "FC Road, Pune",
                "waypoints": ["FLAME Bus Point, Bavdhan, Pune"],
                "destination": "FLAME University, Pune"
            }
        }
        
    def _load_synthetic_data(self):
        """Load synthetic data for development/testing"""
        try:
            self.data_dir = "aroundme_synth"
            self.places = pd.read_csv(f"{self.data_dir}/places.csv")
            self.users = pd.read_csv(f"{self.data_dir}/users.csv")
            self.interactions = pd.read_csv(f"{self.data_dir}/interactions.csv")
            print(f"[SYNTHETIC DATA] Loaded {len(self.places)} places, {len(self.users)} users, {len(self.interactions)} interactions")
        except FileNotFoundError as e:
            print(f"[ERROR] Synthetic data not found: {e}")
            raise
    
    def get_route_coordinates(self, route_name: str) -> List[Tuple[float, float]]:
        """Get coordinate points along a predefined shuttle route"""
        if route_name not in self.shuttle_routes:
            raise ValueError(f"Route {route_name} not found. Available routes: {list(self.shuttle_routes.keys())}")
        
        route = self.shuttle_routes[route_name]
        
        # Build Google Directions API request
        waypoints_str = "|".join(route["waypoints"]) if route["waypoints"] else ""
        directions_url = (
            f"https://maps.googleapis.com/maps/api/directions/json?"
            f"origin={route['origin']}&destination={route['destination']}"
            f"&waypoints={waypoints_str}&key={self.google_api_key}"
        )
        
        try:
            response = requests.get(directions_url)
            route_data = response.json()
            
            if not route_data.get("routes"):
                print(f"❌ Route {route_name} not found. Check API key or place names.")
                return []
            
            # Extract coordinate points from route
            points = []
            for leg in route_data["routes"][0]["legs"]:
                for step in leg["steps"]:
                    loc = step["end_location"]
                    points.append((loc["lat"], loc["lng"]))
            
            print(f"✅ Route {route_name}: Found {len(points)} coordinate points")
            return points
            
        except Exception as e:
            print(f"[ERROR] Failed to get route coordinates: {e}")
            return []
    
    def fetch_restaurants_from_google_places(self, route_coords: List[Tuple[float, float]], 
                                           radius: int = 500) -> pd.DataFrame:
        """Fetch real restaurants from Google Places API along route coordinates"""
        restaurants = []
        
        print(f"[GOOGLE PLACES] Searching for restaurants within {radius}m of route...")
        
        # Search for different types of food establishments for variety
        search_types = ['restaurant', 'cafe']  # Reduced to 2 main types
        seen_place_ids = set()
        
        # Search at MORE points than before (every 3rd point) but not ALL points
        sample_interval = max(2, len(route_coords) // 6)  # Search ~6-8 points
        
        for search_type in search_types:
            for i, (lat, lng) in enumerate(route_coords[::sample_interval]):
                url = (
                    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    f"?location={lat},{lng}&radius={radius}&type={search_type}&key={self.google_api_key}"
                )
                
                try:
                    response = requests.get(url)
                    data = response.json()
                    
                    if "results" in data:
                        for place in data["results"]:
                            place_id = place.get('place_id')
                            if place_id and place_id not in seen_place_ids:
                                # Convert Google Places format to our internal format
                                restaurant = self._convert_google_place_to_internal(place, i)
                                if restaurant:
                                    restaurants.append(restaurant)
                                    seen_place_ids.add(place_id)
                                    
                except Exception as e:
                    print(f"[ERROR] Google Places API error at point {i}: {e}")
                    continue
                    
        # Additional keyword searches for popular cuisines - focused on middle of route
        popular_cuisines = ['indian', 'pizza', 'chinese', 'biryani']  # Reduced to top 4
        
        # Search only at middle of route to save API calls
        if len(route_coords) > 0:
            mid_lat, mid_lng = route_coords[len(route_coords)//2]
            
            for cuisine in popular_cuisines:
                if len(restaurants) > 250:  # Reasonable limit
                    break
                    
                url = (
                    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    f"?location={mid_lat},{mid_lng}&radius={radius*2}&keyword={cuisine}&key={self.google_api_key}"
                )
                
                try:
                    response = requests.get(url)
                    data = response.json()
                    
                    if "results" in data:
                        for place in data["results"]:
                            place_id = place.get('place_id')
                            if place_id and place_id not in seen_place_ids and len(restaurants) < 300:
                                restaurant = self._convert_google_place_to_internal(place, 0)
                                if restaurant:
                                    restaurants.append(restaurant)
                                    seen_place_ids.add(place_id)
                                    
                except Exception as e:
                    print(f"[ERROR] Cuisine search failed for '{cuisine}': {e}")
                    continue
        
        # Remove duplicates and convert to DataFrame
        unique_restaurants = []
        seen_names = set()
        
        for restaurant in restaurants:
            name_key = (restaurant['name'], restaurant['neighborhood'])
            if name_key not in seen_names:
                unique_restaurants.append(restaurant)
                seen_names.add(name_key)
        
        df = pd.DataFrame(unique_restaurants)
        print(f"✅ Found {len(df)} unique restaurants from Google Places API")
        return df
    
    def fetch_restaurants_near_location(self, location: Tuple[float, float], radius: int = 1000, cuisines: list = None) -> pd.DataFrame:
        """Fetch restaurants near a specific GPS location with optional cuisine filter"""
        restaurants = []
        seen_place_ids = set()
        
        lat, lng = location
        
        if cuisines and len(cuisines) > 0:
            # Search with cuisine-specific keywords
            print(f"[GOOGLE PLACES] Searching for {', '.join(cuisines)} restaurants within {radius}m of ({lat:.4f}, {lng:.4f})...")
            
            cuisine_keywords_map = {
                'Italian': ['italian restaurant', 'pizza', 'pasta'],
                'Indian': ['indian restaurant', 'biryani', 'curry'],
                'Asian': ['chinese restaurant', 'japanese restaurant', 'thai restaurant', 'asian restaurant', 'sushi'],
                'Mexican': ['mexican restaurant', 'taco'],
                'American': ['burger', 'bbq restaurant', 'steakhouse', 'american restaurant'],
                'Continental': ['continental restaurant', 'european restaurant', 'mediterranean restaurant'],
                'Street Food': ['street food', 'fast food'],
                'Healthy': ['healthy restaurant', 'salad bar', 'vegan restaurant'],
                'Desserts': ['dessert', 'bakery', 'ice cream'],
                'Cafe': ['cafe', 'coffee shop']
            }
            
            for cuisine in cuisines:
                keywords = cuisine_keywords_map.get(cuisine, [cuisine.lower() + ' restaurant'])
                
                for keyword in keywords:
                    url = (
                        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                        f"?location={lat},{lng}&radius={radius}&keyword={keyword}&key={self.google_api_key}"
                    )
                    
                    try:
                        response = requests.get(url)
                        data = response.json()
                        
                        if "results" in data:
                            for place in data["results"]:
                                place_id = place.get('place_id')
                                if place_id and place_id not in seen_place_ids:
                                    restaurant = self._convert_google_place_to_internal(place, 0)
                                    if restaurant:
                                        restaurant['cuisine'] = cuisine  # Tag with searched cuisine
                                        restaurants.append(restaurant)
                                        seen_place_ids.add(place_id)
                    except Exception as e:
                        print(f"[ERROR] API error for '{keyword}': {e}")
                    
                    # Only use first keyword per cuisine to save API calls
                    break
        else:
            # No cuisine filter - search generic restaurants
            print(f"[GOOGLE PLACES] Searching within {radius}m of location ({lat:.4f}, {lng:.4f})...")
            
            search_types = ['restaurant', 'cafe']
            
            for search_type in search_types:
                url = (
                    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    f"?location={lat},{lng}&radius={radius}&type={search_type}&key={self.google_api_key}"
                )
                
                try:
                    response = requests.get(url)
                    data = response.json()
                    
                    if "results" in data:
                        for place in data["results"]:
                            place_id = place.get('place_id')
                            if place_id and place_id not in seen_place_ids:
                                restaurant = self._convert_google_place_to_internal(place, 0)
                                if restaurant:
                                    restaurants.append(restaurant)
                                    seen_place_ids.add(place_id)
                except Exception as e:
                    print(f"[ERROR] API error: {e}")
        
        # Remove duplicates
        unique_restaurants = []
        seen_names = set()
        for restaurant in restaurants:
            name_key = (restaurant['name'], restaurant['neighborhood'])
            if name_key not in seen_names:
                unique_restaurants.append(restaurant)
                seen_names.add(name_key)
        
        df = pd.DataFrame(unique_restaurants)
        print(f"✅ Found {len(df)} restaurants")
        return df
    
    def fetch_places_near_location(self, location: Tuple[float, float], radius: int = 1000, categories: list = None, place_type: str = 'meals') -> pd.DataFrame:
        """Fetch places (restaurants OR utilities OR malls) near a specific GPS location with optional category filter"""
        
        if place_type == 'meals':
            # Search for restaurants/cafes
            return self.fetch_restaurants_near_location(location, radius, categories)
        elif place_type == 'malls':
            # Search for malls/shopping centers
            return self.fetch_malls_near_location(location, radius, categories)
        else:
            # Search for utilities (grocery stores, etc.)
            return self.fetch_utilities_near_location(location, radius, categories)
    
    def fetch_utilities_near_location(self, location: Tuple[float, float], radius: int = 1000, utility_types: list = None) -> pd.DataFrame:
        """Fetch utilities (grocery stores, pharmacies, etc.) near a specific GPS location"""
        places = []
        seen_place_ids = set()
        
        lat, lng = location
        
        if utility_types and len(utility_types) > 0:
            # Search with utility-specific keywords
            print(f"[GOOGLE PLACES] Searching for {', '.join(utility_types)} within {radius}m of ({lat:.4f}, {lng:.4f})...")
            
            utility_keywords_map = {
                'Grocery Store': ['grocery store', 'grocery'],
                'Supermarket': ['supermarket', 'super market'],
                'Convenience Store': ['convenience store', '7-eleven', 'twenty four seven'],
                'Pharmacy': ['pharmacy', 'medical store', 'chemist'],
                'ATM/Bank': ['atm', 'bank'],
                'Gas Station': ['gas station', 'petrol pump', 'fuel station'],
                'Laundry': ['laundry', 'dry cleaning'],
                'Hardware Store': ['hardware store', 'hardware shop'],
                'Car Repair': ['car repair', 'auto repair', 'mechanic', 'car service'],
                'Car Wash': ['car wash', 'car cleaning'],
                'Tailor': ['tailor', 'tailoring', 'alteration']
            }
            
            for utility in utility_types:
                keywords = utility_keywords_map.get(utility, [utility.lower()])
                
                for keyword in keywords:
                    url = (
                        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                        f"?location={lat},{lng}&radius={radius}&keyword={keyword}&key={self.google_api_key}"
                    )
                    
                    try:
                        response = requests.get(url)
                        data = response.json()
                        
                        if "results" in data:
                            for place in data["results"]:
                                place_id = place.get('place_id')
                                if place_id and place_id not in seen_place_ids:
                                    converted_place = self._convert_google_place_to_internal(place, 0)
                                    if converted_place:
                                        converted_place['cuisine'] = utility  # Tag with utility type
                                        converted_place['categories'] = utility
                                        places.append(converted_place)
                                        seen_place_ids.add(place_id)
                    except Exception as e:
                        print(f"[ERROR] API error for '{keyword}': {e}")
                    
                    # Only use first keyword per utility to save API calls
                    break
        else:
            # No utility filter - search generic stores
            print(f"[GOOGLE PLACES] Searching for all stores within {radius}m...")
            
            search_types = ['store', 'supermarket']
            
            for search_type in search_types:
                url = (
                    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    f"?location={lat},{lng}&radius={radius}&type={search_type}&key={self.google_api_key}"
                )
                
                try:
                    response = requests.get(url)
                    data = response.json()
                    
                    if "results" in data:
                        for place in data["results"]:
                            place_id = place.get('place_id')
                            if place_id and place_id not in seen_place_ids:
                                converted_place = self._convert_google_place_to_internal(place, 0)
                                if converted_place:
                                    places.append(converted_place)
                                    seen_place_ids.add(place_id)
                except Exception as e:
                    print(f"[ERROR] API error: {e}")
        
        # Remove duplicates
        unique_places = []
        seen_names = set()
        for place in places:
            name_key = (place['name'], place['neighborhood'])
            if name_key not in seen_names:
                unique_places.append(place)
                seen_names.add(name_key)
        
        df = pd.DataFrame(unique_places)
        print(f"✅ Found {len(df)} utilities")
        return df
    
    def fetch_malls_near_location(self, location: Tuple[float, float], radius: int = 1000, mall_types: list = None) -> pd.DataFrame:
        """Fetch malls and shopping centers near a specific GPS location"""
        places = []
        seen_place_ids = set()
        
        lat, lng = location
        
        if mall_types and len(mall_types) > 0:
            # Search with mall-specific keywords
            print(f"[GOOGLE PLACES] Searching for {', '.join(mall_types)} within {radius}m of ({lat:.4f}, {lng:.4f})...")
            
            mall_keywords_map = {
                'Shopping Mall': ['shopping mall', 'mall'],
                'Department Store': ['department store'],
                'Shopping Center': ['shopping center', 'shopping centre'],
                'Outlet Mall': ['outlet mall', 'outlet store']
            }
            
            for mall in mall_types:
                keywords = mall_keywords_map.get(mall, [mall.lower()])
                
                for keyword in keywords:
                    url = (
                        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                        f"?location={lat},{lng}&radius={radius}&keyword={keyword}&key={self.google_api_key}"
                    )
                    
                    try:
                        response = requests.get(url)
                        data = response.json()
                        
                        if "results" in data:
                            for place in data["results"]:
                                place_id = place.get('place_id')
                                if place_id and place_id not in seen_place_ids:
                                    converted_place = self._convert_google_place_to_internal(place, 0)
                                    if converted_place:
                                        converted_place['cuisine'] = mall  # Tag with mall type
                                        converted_place['categories'] = mall
                                        places.append(converted_place)
                                        seen_place_ids.add(place_id)
                    except Exception as e:
                        print(f"[ERROR] API error for '{keyword}': {e}")
                    
                    # Only use first keyword per mall type
                    break
        else:
            # No mall type filter - search generic malls
            print(f"[GOOGLE PLACES] Searching for malls within {radius}m of location ({lat:.4f}, {lng:.4f})...")
            
            search_types = ['shopping_mall']
            
            for search_type in search_types:
                url = (
                    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    f"?location={lat},{lng}&radius={radius}&type={search_type}&key={self.google_api_key}"
                )
                
                try:
                    response = requests.get(url)
                    data = response.json()
                    
                    if "results" in data:
                        for place in data["results"]:
                            place_id = place.get('place_id')
                            if place_id and place_id not in seen_place_ids:
                                converted_place = self._convert_google_place_to_internal(place, 0)
                                if converted_place:
                                    places.append(converted_place)
                                    seen_place_ids.add(place_id)
                except Exception as e:
                    print(f"[ERROR] API error: {e}")
        
        # Remove duplicates
        unique_places = []
        seen_names = set()
        for place in places:
            name_key = (place['name'], place['neighborhood'])
            if name_key not in seen_names:
                unique_places.append(place)
                seen_names.add(name_key)
        
        df = pd.DataFrame(unique_places)
        print(f"✅ Found {len(df)} malls")
        return df
    
    def fetch_restaurants_in_area(self, area_name: str, radius: int = 1000) -> pd.DataFrame:
        """Fetch restaurants in a specific named area using geocoding"""
        import requests
        
        print(f"[GEOCODING] Finding coordinates for '{area_name}'...")
        
        # Use Google Geocoding API to get coordinates for the area
        geocode_url = (
            f"https://maps.googleapis.com/maps/api/geocode/json"
            f"?address={area_name},Pune,India&key={self.google_api_key}"
        )
        
        try:
            response = requests.get(geocode_url)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                lat, lng = location['lat'], location['lng']
                print(f"✅ Found {area_name} at ({lat:.4f}, {lng:.4f})")
                
                # Now search for restaurants there
                return self.fetch_restaurants_near_location((lat, lng), radius)
            else:
                print(f"❌ Could not find area '{area_name}'. Using default search.")
                return pd.DataFrame()
        except Exception as e:
            print(f"[ERROR] Geocoding failed: {e}")
            return pd.DataFrame()
    
    def _enrich_with_place_details(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fetch Place Details API for each restaurant to get accurate cuisine information"""
        import time
        
        enriched_restaurants = []
        
        for idx, row in df.iterrows():
            place_id = row['place_id']
            
            # Fetch Place Details
            url = (
                f"https://maps.googleapis.com/maps/api/place/details/json"
                f"?place_id={place_id}&fields=types,editorial_summary&key={self.google_api_key}"
            )
            
            try:
                response = requests.get(url)
                data = response.json()
                
                if data['status'] == 'OK' and 'result' in data:
                    result = data['result']
                    
                    # Get detailed types which may include cuisine-specific types
                    detailed_types = result.get('types', [])
                    editorial_summary = result.get('editorial_summary', {}).get('overview', '')
                    
                    # Update the row with detailed information
                    row['types'] = detailed_types
                    row['editorial_summary'] = editorial_summary
                    
                    # Extract cuisine from types and editorial summary
                    cuisine_info = self._extract_cuisine_from_details(detailed_types, editorial_summary, row['name'])
                    row['cuisine'] = cuisine_info
                    
                # Add small delay to avoid rate limiting
                time.sleep(0.05)  # 50ms delay
                
            except Exception as e:
                print(f"[WARNING] Failed to fetch details for {row['name']}: {e}")
                row['cuisine'] = ''
                row['editorial_summary'] = ''
            
            enriched_restaurants.append(row)
        
        enriched_df = pd.DataFrame(enriched_restaurants)
        print(f"✅ Enriched {len(enriched_df)} restaurants with cuisine details")
        return enriched_df
    
    def _extract_cuisine_from_details(self, types: list, editorial_summary: str, name: str) -> str:
        """Extract cuisine type from place details"""
        cuisines = []
        
        # Check types for cuisine-specific entries
        cuisine_type_map = {
            'italian_restaurant': 'Italian',
            'indian_restaurant': 'Indian',
            'chinese_restaurant': 'Asian',
            'japanese_restaurant': 'Asian',
            'thai_restaurant': 'Asian',
            'korean_restaurant': 'Asian',
            'mexican_restaurant': 'Mexican',
            'american_restaurant': 'American',
            'fast_food_restaurant': 'American',
            'pizza_restaurant': 'Italian',
            'sushi_restaurant': 'Asian',
            'hamburger_restaurant': 'American',
            'sandwich_shop': 'American',
            'seafood_restaurant': 'Continental',
            'steak_house': 'American',
            'bakery': 'Desserts',
            'cafe': 'Cafe',
            'coffee_shop': 'Cafe',
            'meal_takeaway': 'Street Food',
            'meal_delivery': 'Street Food'
        }
        
        for place_type in types:
            if place_type in cuisine_type_map:
                cuisine = cuisine_type_map[place_type]
                if cuisine not in cuisines:
                    cuisines.append(cuisine)
        
        # Check name and editorial summary for keywords
        combined_text = (name + ' ' + editorial_summary).lower()
        
        keyword_map = {
            'Italian': ['italian', 'pizza', 'pasta', 'pizzeria', 'trattoria', 'romano'],
            'Indian': ['indian', 'biryani', 'curry', 'tandoor', 'masala', 'dosa', 'idli', 'punjabi', 'mughlai', 'maratha'],
            'Asian': ['chinese', 'japanese', 'thai', 'korean', 'sushi', 'noodles', 'ramen', 'wok', 'dim sum', 'asian'],
            'Mexican': ['mexican', 'taco', 'burrito', 'quesadilla', 'nacho'],
            'American': ['american', 'burger', 'bbq', 'steak', 'grill', 'barbeque', 'smokehouse'],
            'Continental': ['continental', 'european', 'mediterranean', 'french', 'german'],
            'Street Food': ['street food', 'chaat', 'vada pav', 'fast food'],
            'Healthy': ['healthy', 'salad', 'organic', 'vegan', 'juice'],
            'Desserts': ['dessert', 'bakery', 'cake', 'pastry', 'ice cream', 'sweet'],
            'Cafe': ['cafe', 'coffee', 'espresso', 'latte', 'cappuccino']
        }
        
        for cuisine, keywords in keyword_map.items():
            if any(keyword in combined_text for keyword in keywords):
                if cuisine not in cuisines:
                    cuisines.append(cuisine)
        
        return ', '.join(cuisines) if cuisines else 'Restaurant'
    
    def _convert_google_place_to_internal(self, google_place: Dict, route_index: int) -> Optional[Dict]:
        """Convert Google Places API response to internal restaurant format"""
        try:
            # Extract basic info
            place_id = google_place.get('place_id', f"google_{route_index}")
            name = google_place.get('name', 'Unknown Restaurant')
            rating = google_place.get('rating', 3.5)
            price_level = google_place.get('price_level', 2)  # Google uses 0-4, we use 1-4
            if price_level == 0:
                price_level = 1
                
            # Get location
            location = google_place['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            
            # Determine neighborhood based on location (basic geocoding)
            neighborhood = self._determine_neighborhood_from_coords(lat, lng)
            
            # Extract categories/types from Google Places
            place_types = google_place.get('types', [])
            categories = self._convert_google_types_to_categories(place_types)
            
            # Generate cluster label based on neighborhood and categories
            cluster_label = self._generate_cluster_label(neighborhood, categories, price_level)
            
            # Default values for fields not available in Google Places
            user_rating_count = 50  # Default
            ambience = self._infer_ambience_from_types(place_types)
            veg_only = 0  # Default, would need additional API call to determine
            
            # Extract opening hours information
            opening_hours = google_place.get('opening_hours', {})
            open_now = opening_hours.get('open_now', None)
            weekday_text = opening_hours.get('weekday_text', [])
            
            return {
                'place_id': place_id,
                'name': name,
                'neighborhood': neighborhood,
                'cluster_label': cluster_label,
                'lat': lat,
                'lng': lng,
                'categories': categories,
                'types': place_types,  # Store original Google types as list
                'price_level': price_level,
                'rating': rating,
                'user_rating_count': user_rating_count,
                'user_ratings_total': google_place.get('user_ratings_total', user_rating_count),  # Add actual review count
                'ambience': ambience,
                'veg_only': veg_only,
                'cat_list': str(categories.split(',')),
                'open_now': open_now,
                'weekday_text': weekday_text
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to convert Google Place: {e}")
            return None
    
    def _determine_neighborhood_from_coords(self, lat: float, lng: float) -> str:
        """Determine Pune neighborhood from coordinates (simplified)"""
        # Simplified neighborhood detection based on coordinate ranges
        # In production, you'd use proper reverse geocoding
        
        pune_neighborhoods = {
            "Koregaon Park": {"lat_range": (18.535, 18.545), "lng_range": (73.885, 73.905)},
            "Baner": {"lat_range": (18.555, 18.575), "lng_range": (73.765, 73.785)},
            "FC Road": {"lat_range": (18.515, 18.525), "lng_range": (73.835, 73.845)},
            "Camp": {"lat_range": (18.510, 18.520), "lng_range": (73.875, 73.885)},
            "Viman Nagar": {"lat_range": (18.565, 18.575), "lng_range": (73.905, 73.925)},
            "Kothrud": {"lat_range": (18.500, 18.515), "lng_range": (73.800, 73.820)},
            "Hinjawadi": {"lat_range": (18.585, 18.600), "lng_range": (73.730, 73.750)},
            "Katraj": {"lat_range": (18.445, 18.465), "lng_range": (73.855, 73.875)}
        }
        
        for neighborhood, bounds in pune_neighborhoods.items():
            if (bounds["lat_range"][0] <= lat <= bounds["lat_range"][1] and
                bounds["lng_range"][0] <= lng <= bounds["lng_range"][1]):
                return neighborhood
        
        return "Central Pune"  # Default fallback
    
    def _convert_google_types_to_categories(self, google_types: List[str]) -> str:
        """Convert Google Places types to our internal categories"""
        # Mapping Google Places types to our cuisine categories
        type_mapping = {
            'restaurant': 'restaurant',
            'food': 'restaurant', 
            'meal_takeaway': 'takeaway',
            'cafe': 'cafe',
            'bakery': 'bakery',
            'bar': 'bar',
            'meal_delivery': 'delivery',
            'night_club': 'bar',
            'establishment': 'restaurant'
        }
        
        # Cuisine-specific mappings (would be expanded with more data)
        cuisine_keywords = {
            'pizza': 'pizza',
            'indian': 'north_indian', 
            'chinese': 'asian',
            'italian': 'italian',
            'mexican': 'mexican',
            'thai': 'asian',
            'japanese': 'asian',
            'fast_food': 'street_food',
            'vegetarian': 'veg_only',
            'healthy': 'healthy',
            'dessert': 'dessert'
        }
        
        categories = []
        
        # Add categories based on Google types
        for gtype in google_types:
            if gtype in type_mapping:
                categories.append(type_mapping[gtype])
        
        # Add cuisine categories if detected
        place_name_lower = " ".join(google_types).lower()
        for keyword, category in cuisine_keywords.items():
            if keyword in place_name_lower:
                categories.append(category)
        
        # Default categories if none found
        if not categories:
            categories = ['restaurant', 'general']
        
        return ",".join(list(set(categories)))  # Remove duplicates
    
    def _generate_cluster_label(self, neighborhood: str, categories: str, price_level: int) -> str:
        """Generate semantic cluster label based on location and characteristics"""
        # Simplified cluster generation
        category_list = categories.split(',')
        
        if price_level >= 3:
            price_desc = "upscale"
        elif price_level <= 1:
            price_desc = "budget" 
        else:
            price_desc = "mid-range"
        
        if 'cafe' in category_list or 'bakery' in category_list:
            cluster_type = "cafes & bakeries"
        elif 'italian' in category_list or 'pizza' in category_list:
            cluster_type = "Italian & pizza"
        elif 'bar' in category_list:
            cluster_type = "bars & nightlife"
        elif 'asian' in category_list:
            cluster_type = "Asian cuisine"
        else:
            cluster_type = "general dining"
        
        return f"{neighborhood} {price_desc} {cluster_type}"
    
    def _infer_ambience_from_types(self, google_types: List[str]) -> str:
        """Infer restaurant ambience from Google Places types"""
        if 'bar' in google_types or 'night_club' in google_types:
            return "live_music,date"
        elif 'cafe' in google_types:
            return "study,cozy"
        elif 'meal_takeaway' in google_types:
            return "casual,quick"
        else:
            return "casual,group"
    
    def initialize_real_data_mode(self, route_name: str = "flame_to_fc_road", search_radius: int = 1000):
        """Initialize the system with real Google Places data along a route"""
        if self.use_synthetic_data:
            print("[INFO] Currently using synthetic data. Set use_synthetic_data=False to use real data.")
            return
        
        print(f"[REAL DATA MODE] Initializing with route: {route_name}")
        
        # Get route coordinates
        route_coords = self.get_route_coordinates(route_name)
        if not route_coords:
            print("[ERROR] Failed to get route coordinates")
            return
        
        # Fetch restaurants from Google Places
        self.places = self.fetch_restaurants_from_google_places(route_coords, search_radius)
        
        # Initialize empty user and interaction data (to be populated as users interact)
        self.users = pd.DataFrame(columns=['user_id', 'segment', 'home_neighborhood', 
                                          'pref_categories', 'price_preference', 
                                          'distance_tolerance_km', 'ambience_prefs', 'explore_rate'])
        self.interactions = pd.DataFrame(columns=['interaction_id', 'user_id', 'place_id', 
                                                'type', 'rating', 'dwell_sec', 'timestamp'])
        
        print(f"[REAL DATA MODE] Initialized with {len(self.places)} real restaurants")
    
    def create_user_for_real_data(self, user_preferences: Dict) -> Dict:
        """Create a new user profile for real data mode"""
        user_id = f"real_user_{len(self.users) + 1:03d}"
        
        # Determine user segment based on preferences
        segment = self._determine_user_segment(user_preferences)
        
        user_data = {
            'user_id': user_id,
            'segment': segment,
            'home_neighborhood': user_preferences.get('home_neighborhood', 'Central Pune'),
            'pref_categories': user_preferences.get('preferred_cuisines', 'restaurant,general'),
            'price_preference': user_preferences.get('price_preference', 2),
            'distance_tolerance_km': user_preferences.get('distance_tolerance', 5.0),
            'ambience_prefs': user_preferences.get('ambience_preference', 'casual'),
            'explore_rate': user_preferences.get('explore_rate', 0.3)
        }
        
        # Add to users DataFrame
        new_user_df = pd.DataFrame([user_data])
        self.users = pd.concat([self.users, new_user_df], ignore_index=True)
        
        # Save current user
        with open(self.current_user_file, 'w') as f:
            f.write(user_id)
        
        print(f"[REAL DATA] Created new user: {user_id}")
        return user_data
    
    def _determine_user_segment(self, preferences: Dict) -> str:
        """Determine user segment based on preferences"""
        cuisines = preferences.get('preferred_cuisines', '').lower()
        price = preferences.get('price_preference', 2)
        ambience = preferences.get('ambience_preference', '').lower()
        
        if 'italian' in cuisines and 'date' in ambience:
            return 'romantic_italian_lover'
        elif 'cafe' in cuisines and price <= 2:
            return 'budget_cafe_enthusiast'
        elif price >= 3:
            return 'upscale_diner'
        elif 'asian' in cuisines:
            return 'asian_food_explorer'
        else:
            return 'general_foodie'
    
    def record_interaction(self, user_id: str, place_id: str, interaction_type: str, 
                          rating: Optional[float] = None, dwell_seconds: Optional[int] = None):
        """Record user interaction with a restaurant (for learning)"""
        interaction_id = f"real_int_{len(self.interactions) + 1:06d}"
        timestamp = datetime.now().isoformat()
        
        interaction_data = {
            'interaction_id': interaction_id,
            'user_id': user_id,
            'place_id': place_id,
            'type': interaction_type,
            'rating': rating,
            'dwell_sec': dwell_seconds,
            'timestamp': timestamp
        }
        
        new_interaction_df = pd.DataFrame([interaction_data])
        self.interactions = pd.concat([self.interactions, new_interaction_df], ignore_index=True)
        
        print(f"[INTERACTION] Recorded: {user_id} -> {place_id} ({interaction_type})")
    
    # ========== AI RECOMMENDATION ALGORITHMS ==========
    # (Your existing algorithms adapted to work with both synthetic and real data)
    
    def get_current_time_context(self):
        """Get current time context for recommendations"""
        current_time = datetime.now().time()
        current_day = datetime.now().strftime('%A')
        
        if current_day in ['Saturday', 'Sunday'] and time(10, 0) <= current_time <= time(14, 0):
            return 'weekend_brunch'
        elif time(7, 0) <= current_time <= time(11, 0):
            return 'breakfast'
        elif time(11, 30) <= current_time <= time(15, 0):
            return 'lunch'
        elif time(15, 30) <= current_time <= time(18, 0):
            return 'tea_time'
        elif time(18, 30) <= current_time <= time(23, 0):
            return 'dinner'
        elif current_time >= time(23, 0) or current_time <= time(6, 30):
            return 'late_night'
        else:
            return 'general'
    
    def get_route_aware_recommendations(self, user_data: Dict, route_name: str = "flame_to_fc_road", 
                                     algorithm: str = "time_based", limit: int = 5,
                                     current_location_index: float = 0.5,
                                     current_location_coords: Tuple[float, float] = None,
                                     sort_by: List[str] = None) -> List[Dict]:
        """
        Get AI-powered recommendations that are aware of shuttle route proximity
        
        Args:
            user_data: User preference data
            route_name: Name of the shuttle route
            algorithm: Recommendation algorithm to use
            limit: Number of recommendations to return
            current_location_index: Position on route (0.0=start, 0.5=middle, 1.0=end) - used if coords not provided
            current_location_coords: Actual GPS coordinates (lat, lng) - takes priority over index
            sort_by: List of sort criteria ['rating', 'distance', 'price', 'score']
        """
        
        if sort_by is None:
            sort_by = ['score']  # Default to AI score
        
        # Get route coordinates for proximity calculation
        route_coords = self.get_route_coordinates(route_name) if not self.use_synthetic_data else []
        
        # Determine current location coordinates
        current_location = current_location_coords  # Use GPS coords if provided
        
        if current_location is None and route_coords and current_location_index is not None:
            # Fall back to index-based location if GPS not provided
            coord_index = int(len(route_coords) * current_location_index)
            coord_index = min(coord_index, len(route_coords) - 1)
            current_location = route_coords[coord_index]
        
        # Get ALL matching recommendations (use large limit initially)
        initial_limit = 1000  # Get all matching restaurants
        
        # Get recommendations using specified algorithm
        # Get recommendations using specified algorithm
        if algorithm == "time_based":
            recommendations = self._get_time_based_recommendations_internal(user_data, initial_limit)
        elif algorithm == "history_based":
            recommendations = self._get_history_based_recommendations_internal(user_data, initial_limit)
        elif algorithm == "social_collaborative":
            recommendations = self._get_social_recommendations_internal(user_data, initial_limit)
        elif algorithm == "cluster_based":
            recommendations = self._get_cluster_recommendations_internal(user_data, initial_limit)
        elif algorithm == "hybrid":
            recommendations = self._get_hybrid_recommendations_internal(user_data, initial_limit)
        else:
            recommendations = self._get_explore_recommendations_internal(user_data, initial_limit)
        
        # Add distance from current location if available
        if current_location:
            from geopy.distance import geodesic
            for rec in recommendations:
                rec['distance_from_current'] = geodesic(
                    current_location,
                    (rec['lat'], rec['lng'])
                ).meters
        
        # Add route proximity scoring if using real data
        if not self.use_synthetic_data and route_coords:
            for rec in recommendations:
                rec['route_convenience'] = self._calculate_route_convenience(
                    rec['lat'], rec['lng'], route_coords
                )
                # Adjust final score based on route convenience
                rec['final_score'] = rec.get('score', 0) * rec['route_convenience']
        
        # Apply multi-criteria sorting
        def sort_key(rec):
            sort_values = []
            for criterion in sort_by:
                if criterion == 'rating':
                    sort_values.append(-rec.get('rating', 0))  # Higher rating first
                elif criterion == 'distance':
                    sort_values.append(rec.get('distance_from_current', float('inf')))  # Closer first
                elif criterion == 'price':
                    sort_values.append(rec.get('price_level', 2))  # Lower price first
                elif criterion == 'score':
                    sort_values.append(-rec.get('final_score', rec.get('score', 0)))  # Higher score first
            return tuple(sort_values)
        
        recommendations.sort(key=sort_key)
        
        return recommendations[:limit]
    
    def _calculate_route_convenience(self, restaurant_lat: float, restaurant_lng: float, 
                                   route_coords: List[Tuple[float, float]]) -> float:
        """Calculate how convenient a restaurant is relative to the shuttle route"""
        if not route_coords:
            return 1.0  # No penalty if no route data
        
        # Find minimum distance to any point on the route
        min_distance = min(
            geodesic((restaurant_lat, restaurant_lng), route_point).meters 
            for route_point in route_coords
        )
        
        # Convert distance to convenience score (closer = higher score)
        if min_distance <= 200:  # Very close
            return 1.0
        elif min_distance <= 500:  # Walking distance
            return 0.8
        elif min_distance <= 1000:  # Short detour
            return 0.6
        elif min_distance <= 2000:  # Moderate detour
            return 0.4
        else:  # Far from route
            return 0.2
    
    def _get_time_based_recommendations_internal(self, user_data: Dict, limit: int) -> List[Dict]:
        """Internal time-based recommendation logic (adapted from your original code)"""
        time_context = self.get_current_time_context()
        
        # Time-specific category preferences
        preferences = {
            'breakfast': ['cafe', 'bakery', 'healthy'],
            'weekend_brunch': ['cafe', 'bakery', 'healthy', 'dessert'],
            'lunch': ['south_indian', 'north_indian', 'asian', 'healthy', 'street_food', 'pizza'],
            'tea_time': ['cafe', 'bakery', 'dessert'],
            'dinner': ['south_indian', 'north_indian', 'italian', 'asian', 'mexican', 'pizza'],
            'late_night': ['street_food', 'pizza', 'asian'],
            'general': []
        }
        
        preferred_categories = preferences.get(time_context, [])
        
        # Filter places based on user preferences and time context
        candidate_places = self.places.copy()
        
        # FIRST: Apply user's cuisine preferences (if specified)
        user_categories = user_data.get('pref_categories', '').lower().split(',')
        user_categories = [cat.strip() for cat in user_categories if cat.strip()]
        
        if user_categories and user_categories != ['restaurant', 'cafe']:
            # User has specific cuisine preferences - filter strictly
            pattern = '|'.join(user_categories)
            category_column = 'types' if 'types' in candidate_places.columns else 'categories'
            
            cuisine_filtered = candidate_places[
                candidate_places[category_column].str.contains(pattern, na=False, case=False) |
                candidate_places['name'].str.contains(pattern, na=False, case=False)  # Also check name
            ]
            
            if not cuisine_filtered.empty:
                candidate_places = cuisine_filtered
                print(f"[FILTER] Filtered to {len(candidate_places)} restaurants matching: {', '.join(user_categories)}")
            else:
                print(f"[FILTER] No exact matches for {', '.join(user_categories)}, showing all restaurants")
        
        # THEN: Apply time-context filtering if categories are specified
        if preferred_categories:
            pattern = '|'.join(preferred_categories)
            # Use 'types' column for Google Places data, 'categories' for synthetic data
            category_column = 'types' if 'types' in candidate_places.columns else 'categories'
            
            # For Google Places data, be more flexible - include all restaurants if no specific matches
            time_filtered = candidate_places[
                candidate_places[category_column].str.contains(pattern, na=False, case=False)
            ]
            
            # If no matches found with specific categories, include all restaurants/food places
            if time_filtered.empty:
                broad_pattern = r'(restaurant|food|meal_takeaway|bakery|cafe|bar)'
                candidate_places = candidate_places[
                    candidate_places[category_column].str.contains(broad_pattern, na=False, case=False)
                ]
            else:
                candidate_places = time_filtered
        
        # Calculate time-aware scores
        recommendations = []
        for _, place in candidate_places.iterrows():
            score = self._calculate_time_based_score(place, user_data, time_context)
            
            recommendations.append({
                'place_id': place['place_id'],
                'name': place['name'],
                'neighborhood': place['neighborhood'],
                'categories': place['categories'],
                'rating': place['rating'],
                'price_level': place['price_level'],
                'lat': place['lat'],
                'lng': place['lng'],
                'score': score,
                'algorithm': 'time_based',
                'context': time_context,
                'reasoning': f"Perfect for {time_context.replace('_', ' ')}"
            })
        
        # Add significant randomization for variety while keeping quality high
        sorted_recs = sorted(recommendations, key=lambda x: x['score'], reverse=True)
        
        if len(sorted_recs) > limit:
            import random
            # Take top 20% guaranteed + random selection from top 80% for MORE variety
            guaranteed_count = max(1, limit // 5)
            top_candidates = sorted_recs[:int(len(sorted_recs) * 0.8)]
            
            guaranteed = sorted_recs[:guaranteed_count]
            remaining_slots = limit - guaranteed_count
            
            # Random selection from remaining top candidates for diversity
            available = [r for r in top_candidates if r not in guaranteed]
            if available and remaining_slots > 0:
                random_picks = random.sample(available, min(remaining_slots, len(available)))
                # Shuffle the final list for even more variety
                final_list = guaranteed + random_picks
                random.shuffle(final_list)
                return final_list
        
        return sorted_recs[:limit]
    
    def _calculate_time_based_score(self, place: pd.Series, user_data: Dict, time_context: str) -> float:
        """Calculate time-based recommendation score"""
        score = place['rating'] * 0.3  # Base score
        
        # Time-specific bonuses
        categories = place['categories'].lower()
        if time_context == 'breakfast' and any(cat in categories for cat in ['cafe', 'bakery', 'healthy']):
            score += 1.5
        elif time_context == 'lunch' and any(cat in categories for cat in ['south_indian', 'north_indian', 'asian']):
            score += 1.2
        elif time_context == 'dinner' and any(cat in categories for cat in ['italian', 'mexican', 'asian']):
            score += 1.3
        elif time_context == 'tea_time' and any(cat in categories for cat in ['cafe', 'dessert']):
            score += 1.4
        elif time_context == 'weekend_brunch' and any(cat in categories for cat in ['cafe', 'healthy', 'dessert']):
            score += 1.3
        elif time_context == 'late_night' and any(cat in categories for cat in ['street_food', 'pizza']):
            score += 1.1
        
        # Price preference matching
        user_price = user_data.get('price_preference', 2)
        if place['price_level'] == user_price:
            score += 0.4
        elif abs(place['price_level'] - user_price) == 1:
            score += 0.2
        
        # User category preference matching
        user_cats = user_data.get('pref_categories', '').split(',')
        if any(cat.strip().lower() in categories for cat in user_cats):
            score += 0.5
        
        # High rating bonus
        if place['rating'] >= 4.5:
            score += 0.2
        
        return score
    
    def _get_history_based_recommendations_internal(self, user_data: Dict, limit: int) -> List[Dict]:
        """Internal history-based recommendation logic"""
        user_id = user_data['user_id']
        
        # Get user's interaction history
        user_interactions = self.interactions[self.interactions['user_id'] == user_id]
        
        if user_interactions.empty:
            # No history available, fall back to popular recommendations
            return self._get_popular_recommendations_internal(user_data, limit)
        
        # Analyze user's preferences from history
        high_rated_interactions = user_interactions[user_interactions['rating'] >= 4.0]
        
        if high_rated_interactions.empty:
            return self._get_popular_recommendations_internal(user_data, limit)
        
        # Extract patterns from liked places
        liked_place_ids = high_rated_interactions['place_id'].unique()
        liked_places = self.places[self.places['place_id'].isin(liked_place_ids)]
        
        # Get unvisited places
        visited_place_ids = user_interactions['place_id'].unique()
        unvisited_places = self.places[~self.places['place_id'].isin(visited_place_ids)]
        
        # Calculate history-based scores
        recommendations = []
        
        # Extract preference patterns
        enjoyed_categories = set()
        enjoyed_neighborhoods = set()
        price_levels = []
        
        for _, place in liked_places.iterrows():
            enjoyed_categories.update(place['categories'].split(','))
            enjoyed_neighborhoods.add(place['neighborhood'])
            price_levels.append(place['price_level'])
        
        preferred_price = np.mean(price_levels) if price_levels else 2
        
        for _, place in unvisited_places.iterrows():
            score = self._calculate_history_based_score(
                place, enjoyed_categories, enjoyed_neighborhoods, preferred_price
            )
            
            recommendations.append({
                'place_id': place['place_id'],
                'name': place['name'],
                'neighborhood': place['neighborhood'],
                'categories': place['categories'],
                'rating': place['rating'],
                'price_level': place['price_level'],
                'lat': place['lat'],
                'lng': place['lng'],
                'score': score,
                'algorithm': 'history_based',
                'reasoning': "Based on your dining history and preferences"
            })
        
        # Add randomization for variety
        sorted_recs = sorted(recommendations, key=lambda x: x['score'], reverse=True)
        if len(sorted_recs) > limit:
            import random
            guaranteed_count = max(1, limit // 4)
            top_candidates = sorted_recs[:int(len(sorted_recs) * 0.7)]
            guaranteed = sorted_recs[:guaranteed_count]
            remaining = [r for r in top_candidates if r not in guaranteed]
            if remaining:
                random_picks = random.sample(remaining, min(limit - guaranteed_count, len(remaining)))
                final_list = guaranteed + random_picks
                random.shuffle(final_list)
                return final_list
        return sorted_recs[:limit]
    
    def _calculate_history_based_score(self, place: pd.Series, enjoyed_categories: set,
                                     enjoyed_neighborhoods: set, preferred_price: float) -> float:
        """Calculate history-based recommendation score"""
        score = place['rating'] * 0.4  # Base score
        
        # Category similarity bonus
        place_categories = set(place['categories'].split(','))
        category_overlap = len(place_categories.intersection(enjoyed_categories))
        score += category_overlap * 0.3
        
        # Neighborhood preference
        if place['neighborhood'] in enjoyed_neighborhoods:
            score += 0.5
        
        # Price alignment
        price_diff = abs(place['price_level'] - preferred_price)
        if price_diff == 0:
            score += 0.4
        elif price_diff <= 1:
            score += 0.2
        
        # High rating bonus
        if place['rating'] >= 4.5:
            score += 0.3
        
        return score
    
    def _get_social_recommendations_internal(self, user_data: Dict, limit: int) -> List[Dict]:
        """Internal social collaborative filtering logic"""
        # Simplified version - in production you'd implement full user similarity
        # For now, return popular places that match user preferences
        return self._get_popular_recommendations_internal(user_data, limit, algorithm_name="social_collaborative")
    
    def _get_cluster_recommendations_internal(self, user_data: Dict, limit: int) -> List[Dict]:
        """Internal cluster-based recommendation logic"""
        # Simplified version - recommend from clusters based on user preferences
        user_neighborhoods = [user_data.get('home_neighborhood', '')]
        user_categories = user_data.get('pref_categories', '').split(',')
        user_categories = [cat.strip().lower() for cat in user_categories if cat.strip()]
        user_price = user_data.get('price_preference', 2)
        
        # Filter places by cuisine preferences first
        candidate_places = self.places.copy()
        
        if user_categories and user_categories != ['restaurant', 'cafe']:
            # User has specific cuisine preferences - filter strictly
            pattern = '|'.join(user_categories)
            category_column = 'types' if 'types' in candidate_places.columns else 'categories'
            
            cuisine_filtered = candidate_places[
                candidate_places[category_column].str.contains(pattern, na=False, case=False) |
                candidate_places['name'].str.contains(pattern, na=False, case=False)
            ]
            
            if not cuisine_filtered.empty:
                candidate_places = cuisine_filtered
                print(f"[CLUSTER] Filtered to {len(candidate_places)} restaurants matching cuisines")
            else:
                print(f"[CLUSTER] No matches for specified cuisines, showing all")
        
        # Score places based on cluster compatibility
        recommendations = []
        
        for _, place in candidate_places.iterrows():
            score = 0
            
            # Neighborhood compatibility
            if place['neighborhood'] in user_neighborhoods:
                score += 2.0
            
            # Category compatibility
            place_categories = place['categories'].split(',')
            category_matches = sum(1 for cat in user_categories if cat.strip().lower() in [pc.strip().lower() for pc in place_categories])
            score += category_matches * 0.5
            
            # Price compatibility
            if abs(place['price_level'] - user_price) <= 1:
                score += 1.0
            
            # Base quality
            score += place['rating'] * 0.3
            
            recommendations.append({
                'place_id': place['place_id'],
                'name': place['name'],
                'neighborhood': place['neighborhood'],
                'categories': place['categories'],
                'rating': place['rating'],
                'price_level': place['price_level'],
                'lat': place['lat'],
                'lng': place['lng'],
                'score': score,
                'algorithm': 'cluster_based',
                'cluster': place.get('cluster_label', 'Unknown'),
                'reasoning': f"Matches your preferred area and cuisine type"
            })
        
        # Add randomization for variety
        sorted_recs = sorted(recommendations, key=lambda x: x['score'], reverse=True)
        if len(sorted_recs) > limit:
            import random
            guaranteed_count = max(1, limit // 4)
            top_candidates = sorted_recs[:int(len(sorted_recs) * 0.75)]
            guaranteed = sorted_recs[:guaranteed_count]
            remaining = [r for r in top_candidates if r not in guaranteed]
            if remaining:
                random_picks = random.sample(remaining, min(limit - guaranteed_count, len(remaining)))
                final_list = guaranteed + random_picks
                random.shuffle(final_list)
                return final_list
        return sorted_recs[:limit]
    
    def _get_hybrid_recommendations_internal(self, user_data: Dict, limit: int) -> List[Dict]:
        """Internal hybrid recommendation logic"""
        # Combine multiple algorithms with different weights
        time_recs = self._get_time_based_recommendations_internal(user_data, limit * 2)
        cluster_recs = self._get_cluster_recommendations_internal(user_data, limit * 2)
        
        # Merge and re-score
        all_recs = {}
        
        # Add time-based recommendations with weight
        for rec in time_recs:
            place_id = rec['place_id']
            if place_id not in all_recs:
                all_recs[place_id] = rec.copy()
                all_recs[place_id]['score'] = rec['score'] * 0.4  # 40% weight
                all_recs[place_id]['algorithm'] = 'hybrid'
            else:
                all_recs[place_id]['score'] += rec['score'] * 0.4
        
        # Add cluster-based recommendations with weight
        for rec in cluster_recs:
            place_id = rec['place_id']
            if place_id not in all_recs:
                all_recs[place_id] = rec.copy()
                all_recs[place_id]['score'] = rec['score'] * 0.6  # 60% weight
                all_recs[place_id]['algorithm'] = 'hybrid'
            else:
                all_recs[place_id]['score'] += rec['score'] * 0.6
        
        # Update reasoning
        for rec in all_recs.values():
            rec['reasoning'] = "Combines time context + location preferences + taste patterns"
        
        return sorted(all_recs.values(), key=lambda x: x['score'], reverse=True)[:limit]
    
    def _get_explore_recommendations_internal(self, user_data: Dict, limit: int) -> List[Dict]:
        """Internal exploration recommendation logic"""
        explore_rate = user_data.get('explore_rate', 0.3)
        
        # Get places that are different from user's usual preferences
        user_categories = set(user_data.get('pref_categories', '').lower().split(','))
        user_categories = {cat.strip() for cat in user_categories if cat.strip()}
        user_neighborhood = user_data.get('home_neighborhood', '')
        user_price = user_data.get('price_preference', 2)
        
        # For explore mode, still respect cuisine filter if specific ones selected
        candidate_places = self.places.copy()
        
        if user_categories and user_categories != {'restaurant', 'cafe'}:
            # User has specific cuisine preferences - filter but be more lenient
            pattern = '|'.join(user_categories)
            category_column = 'types' if 'types' in candidate_places.columns else 'categories'
            
            cuisine_filtered = candidate_places[
                candidate_places[category_column].str.contains(pattern, na=False, case=False) |
                candidate_places['name'].str.contains(pattern, na=False, case=False)
            ]
            
            if not cuisine_filtered.empty:
                candidate_places = cuisine_filtered
                print(f"[EXPLORE] Filtered to {len(candidate_places)} restaurants matching cuisines")
        
        recommendations = []
        
        for _, place in candidate_places.iterrows():
            novelty_score = 0
            
            # Neighborhood novelty
            if place['neighborhood'] != user_neighborhood:
                novelty_score += 1.0
            
            # Category novelty
            place_categories = set(place['categories'].lower().split(','))
            category_overlap = len(user_categories.intersection(place_categories))
            category_novelty = 1.0 - (category_overlap / max(len(user_categories), 1))
            novelty_score += category_novelty * 0.8
            
            # Price stretch (but not too much)
            price_diff = abs(place['price_level'] - user_price)
            if price_diff == 1:  # Slight price stretch is good for exploration
                novelty_score += 0.5
            elif price_diff > 2:  # Too much stretch
                novelty_score -= 0.5
            
            # Quality assurance (don't recommend bad places)
            if place['rating'] < 3.5:
                novelty_score -= 1.0
            
            # Apply exploration rate
            final_score = (place['rating'] * 0.3) + (novelty_score * explore_rate)
            
            recommendations.append({
                'place_id': place['place_id'],
                'name': place['name'],
                'neighborhood': place['neighborhood'],
                'categories': place['categories'],
                'rating': place['rating'],
                'price_level': place['price_level'],
                'lat': place['lat'],
                'lng': place['lng'],
                'score': final_score,
                'algorithm': 'explore_mode',
                'novelty_score': novelty_score,
                'reasoning': f"Adventure recommendation - try something new!"
            })
        
        # Add strong randomization for exploration variety
        sorted_recs = sorted(recommendations, key=lambda x: x['score'], reverse=True)
        if len(sorted_recs) > limit:
            import random
            # For explore mode, use even more randomization
            guaranteed_count = max(1, limit // 5)
            top_candidates = sorted_recs[:int(len(sorted_recs) * 0.85)]  # Larger pool
            guaranteed = sorted_recs[:guaranteed_count]
            remaining = [r for r in top_candidates if r not in guaranteed]
            if remaining:
                random_picks = random.sample(remaining, min(limit - guaranteed_count, len(remaining)))
                final_list = guaranteed + random_picks
                random.shuffle(final_list)  # Shuffle everything for adventure!
                return final_list
        return sorted_recs[:limit]
    
    def _get_popular_recommendations_internal(self, user_data: Dict, limit: int, 
                                           algorithm_name: str = "popular") -> List[Dict]:
        """Internal popular recommendations logic (fallback)"""
        user_cats = user_data.get('pref_categories', '').lower().split(',')
        user_price = user_data.get('price_preference', 2)
        
        # Filter by user preferences and sort by rating
        filtered_places = self.places.copy()
        
        # Category filter
        if user_cats and user_cats[0]:  # Check if not empty
            pattern = '|'.join(user_cats)
            # Use 'types' column for Google Places data, 'categories' for synthetic data
            category_column = 'types' if 'types' in filtered_places.columns else 'categories'
            filtered_places = filtered_places[
                filtered_places[category_column].str.contains(pattern, na=False, case=False)
            ]
        
        # Price filter (within 1 level)
        price_mask = abs(filtered_places['price_level'] - user_price) <= 1
        filtered_places = filtered_places[price_mask]
        
        # Sort by rating
        popular_places = filtered_places.nlargest(limit, 'rating')
        
        recommendations = []
        for _, place in popular_places.iterrows():
            recommendations.append({
                'place_id': place['place_id'],
                'name': place['name'],
                'neighborhood': place['neighborhood'],
                'categories': place['categories'],
                'rating': place['rating'],
                'price_level': place['price_level'],
                'lat': place['lat'],
                'lng': place['lng'],
                'score': place['rating'],
                'algorithm': algorithm_name,
                'reasoning': "Popular choice matching your preferences"
            })
        
        return recommendations
    
    def display_recommendations(self, recommendations: List[Dict], route_name: str = None):
        """Display recommendations in a formatted way"""
        print(f"\n{'='*60}")
        print(f"🍽️  AROUNDME INTEGRATED RECOMMENDATIONS")
        if route_name:
            print(f"📍 Route: {route_name.replace('_', ' ').title()}")
        print(f"🤖 Data Source: {'Synthetic (Development)' if self.use_synthetic_data else 'Real (Google Places)'}")
        print(f"{'='*60}")
        
        if not recommendations:
            print("❌ No recommendations found matching your criteria.")
            return
        
        for i, rec in enumerate(recommendations, 1):
            rating_stars = '★' * int(rec['rating'])
            print(f"\n{i}. 🏪 {rec['name']}")
            print(f"   📍 {rec['neighborhood']}")
            print(f"   ⭐ Rating: {rec['rating']:.1f} {rating_stars}")
            print(f"   💰 Price Level: Rs.{rec['price_level']}")
            
            # Show distance from current location if available
            if 'distance_from_current' in rec:
                distance_m = rec['distance_from_current']
                if distance_m < 1000:
                    print(f"   🚶 Distance: {distance_m:.0f}m from you")
                else:
                    print(f"   🚶 Distance: {distance_m/1000:.1f}km from you")
            
            print(f"   🍽️  Categories: {rec['categories']}")
            print(f"   🎯 Algorithm: {rec['algorithm'].replace('_', ' ').title()}")
            print(f"   📊 Score: {rec['score']:.3f}")
            
            if 'route_convenience' in rec:
                print(f"   🚌 Route Convenience: {rec['route_convenience']:.1f}")
            
            if 'reasoning' in rec:
                print(f"   💡 Why: {rec['reasoning']}")
            
            if not self.use_synthetic_data:
                print(f"   📱 Coordinates: {rec['lat']:.6f}, {rec['lng']:.6f}")
    
    def save_session_data(self, filename: str = "integrated_session_data.json"):
        """Save current session data for future use"""
        session_data = {
            'users': self.users.to_dict('records') if not self.users.empty else [],
            'interactions': self.interactions.to_dict('records') if not self.interactions.empty else [],
            'places_count': len(self.places),
            'data_source': 'synthetic' if self.use_synthetic_data else 'google_places',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        print(f"📁 Session data saved to {filename}")


def main_demo():
    """Demonstration of the integrated system"""
    
    # Initialize with synthetic data for development
    print("🚀 Initializing AroundMe Integrated System...")
    
    # Replace with your actual Google API key for real data mode
    GOOGLE_API_KEY = os.environ.get('AROUNDME_GOOGLE_API_KEY', '')    
    # Start with synthetic data
    system = IntegratedAroundMeSystem(
        google_api_key=GOOGLE_API_KEY,
        use_synthetic_data=True  # Change to False for real Google Places data
    )
    
    # Demo user preferences
    user_preferences = {
        'home_neighborhood': 'Koregaon Park',
        'preferred_cuisines': 'italian,pizza,cafe',
        'price_preference': 2,
        'ambience_preference': 'date,cozy',
        'explore_rate': 0.3,
        'distance_tolerance': 5.0
    }
    
    # Create or load user
    if system.use_synthetic_data:
        # Use existing synthetic user
        user_data = {
            'user_id': 'u_0001',
            'home_neighborhood': 'Koregaon Park',
            'pref_categories': 'italian,pizza',
            'price_preference': 2,
            'explore_rate': 0.25
        }
    else:
        # For real data mode, initialize and create user
        system.initialize_real_data_mode("flame_to_fc_road")
        user_data = system.create_user_for_real_data(user_preferences)
    
    # Test different algorithms
    algorithms = ["time_based", "history_based", "cluster_based", "hybrid", "explore_mode"]
    
    for algorithm in algorithms:
        print(f"\n\n🔍 Testing {algorithm.replace('_', ' ').title()} Algorithm")
        recommendations = system.get_route_aware_recommendations(
            user_data=user_data,
            route_name="flame_to_fc_road",
            algorithm=algorithm,
            limit=3
        )
        
        system.display_recommendations(recommendations, "flame_to_fc_road")
    
    # Save session data
    system.save_session_data()
    
    print(f"\n\n✅ Demo completed! System ready for{'real-world deployment' if not system.use_synthetic_data else 'further development'}.")


if __name__ == "__main__":
    main_demo()
