# AroundMe Recommendation System - Detailed Algorithm Flows

## System Architecture Overview
**Project**: AroundMe Restaurant Recommendation System v2.0  
**Total Algorithms**: 6 Independent Recommendation Engines  
**Data Sources**: users.csv (228 users), places.csv (139 restaurants), interactions.csv (5,106 interactions)  
**Output**: Top 5 ranked recommendations per algorithm  

---

## Table of Contents
1. [Time-Based Recommendations](#algorithm-1-time-based-recommendations)
2. [History-Based Learning](#algorithm-2-history-based-learning)
3. [Enhanced Social Collaborative Filtering](#algorithm-3-enhanced-social-collaborative-filtering)
4. [Cluster-Based Intelligence](#algorithm-4-cluster-based-intelligence)
5. [Hybrid Social+Cluster](#algorithm-5-hybrid-socialcluster)
6. [Explore Mode Discovery](#algorithm-6-explore-mode-discovery)

---

## Algorithm 1: Time-Based Recommendations

### **Step 1: Context Detection**
```
INPUT: Current system time, user preferences
├── time_detection = datetime.now().time()
├── day_detection = datetime.now().strftime('%A')
└── context_mapping:
    ├── IF Weekend + 10:00-14:00 → 'weekend_brunch'
    ├── IF 07:00-11:00 → 'breakfast'
    ├── IF 11:30-15:00 → 'lunch'
    ├── IF 15:30-18:00 → 'tea_time'
    ├── IF 18:30-23:00 → 'dinner'
    ├── IF 23:00-06:30 → 'late_night'
    └── ELSE → 'general'
```

### **Step 2: Category Context Mapping**
```
context_preferences = {
    'breakfast': ['cafe', 'bakery', 'healthy'],
    'weekend_brunch': ['cafe', 'bakery', 'healthy', 'dessert'],
    'lunch': ['south_indian', 'north_indian', 'asian', 'healthy', 'street_food', 'pizza'],
    'tea_time': ['cafe', 'bakery', 'dessert'],
    'dinner': ['south_indian', 'north_indian', 'italian', 'asian', 'mexican', 'pizza'],
    'late_night': ['street_food', 'pizza', 'asian'],
    'general': []
}
```

### **Step 3: Geographic Filtering**
```
location_filter = restaurants WHERE neighborhood = user.home_neighborhood
├── INPUT: user_data['home_neighborhood']
├── FILTER: places[places['neighborhood'] == user_neighborhood]
└── RESULT: nearby_places[]
```

### **Step 4: Time-Context Filtering**
```
IF preferred_categories NOT empty:
    ├── pattern = '|'.join(preferred_categories)
    ├── time_filtered = nearby_places WHERE categories CONTAINS pattern
    └── RESULT: contextual_restaurants[]
ELSE:
    └── time_filtered = nearby_places (no category filter)
```

### **Step 5: Time-Aware Scoring Algorithm**
```
FOR each restaurant IN time_filtered:
    ├── base_score = rating × 0.3
    ├── time_bonus = CALCULATE_TIME_BONUS(context, categories)
    ├── price_match = CALCULATE_PRICE_COMPATIBILITY(restaurant, user)
    ├── preference_match = CALCULATE_PREFERENCE_OVERLAP(restaurant, user)
    ├── quality_bonus = 0.2 IF rating >= 4.5 ELSE 0
    └── total_score = base_score + time_bonus + price_match + preference_match + quality_bonus

CALCULATE_TIME_BONUS(context, categories):
├── breakfast + ['cafe','bakery','healthy'] → +1.5
├── lunch + ['south_indian','north_indian','asian'] → +1.2
├── dinner + ['italian','mexican','asian'] → +1.3
├── tea_time + ['cafe','dessert'] → +1.4
├── weekend_brunch + ['cafe','healthy','dessert'] → +1.3
├── late_night + ['street_food','pizza'] → +1.1
└── no_match → +0.0

CALCULATE_PRICE_COMPATIBILITY(restaurant, user):
├── exact_match: restaurant.price == user.price → +0.4
├── close_match: |restaurant.price - user.price| == 1 → +0.2
└── no_match → +0.0

CALCULATE_PREFERENCE_OVERLAP(restaurant, user):
├── user_categories = user.pref_categories.split(',')
├── restaurant_categories = restaurant.categories.split(',')
├── IF any_overlap(user_categories, restaurant_categories) → +0.5
└── ELSE → +0.0
```

### **Step 6: Ranking & Output**
```
├── Sort restaurants by total_score DESC
├── Limit to top 5 results
└── Output format:
    ├── Restaurant name (neighborhood)
    ├── Rating: X.X ★★★★★ | Price: Rs.X | Score: X.XXX
    ├── Categories: category1, category2, category3
    └── Context reasoning: "Perfect for [time_context]"
```

---

## Algorithm 2: History-Based Learning

### **Step 1: User History Analysis**
```
INPUT: user_id
├── user_interactions = interactions WHERE user_id = current_user
├── high_rated = interactions WHERE rating >= 4.0
└── EXTRACT patterns:
    ├── enjoyed_categories = UNIQUE(categories from high_rated places)
    ├── enjoyed_neighborhoods = UNIQUE(neighborhoods from high_rated places)
    └── preferred_price = MEAN(price_levels from high_rated places)
```

### **Step 2: Visited Places Exclusion**
```
visited_places = UNIQUE(place_ids from user_interactions)
├── unvisited_places = places WHERE place_id NOT IN visited_places
└── candidate_pool = unvisited_places
```

### **Step 3: History-Based Scoring**
```
FOR each place IN candidate_pool:
    ├── base_score = rating × 0.4
    ├── category_bonus = CALCULATE_CATEGORY_OVERLAP(place, enjoyed_categories)
    ├── neighborhood_bonus = CALCULATE_LOCATION_PREFERENCE(place, enjoyed_neighborhoods)
    ├── price_alignment = CALCULATE_PRICE_ALIGNMENT(place, preferred_price)
    ├── quality_bonus = 0.3 IF rating >= 4.5 ELSE 0
    └── history_score = base_score + category_bonus + neighborhood_bonus + price_alignment + quality_bonus

CALCULATE_CATEGORY_OVERLAP(place, enjoyed_categories):
├── place_categories = SET(place.categories.split(','))
├── enjoyed_set = SET(enjoyed_categories)
├── overlap_count = LENGTH(place_categories ∩ enjoyed_set)
└── RETURN overlap_count × 0.3

CALCULATE_LOCATION_PREFERENCE(place, enjoyed_neighborhoods):
├── IF place.neighborhood IN enjoyed_neighborhoods → +0.5
└── ELSE → +0.0

CALCULATE_PRICE_ALIGNMENT(place, preferred_price):
├── price_diff = |place.price_level - preferred_price|
├── exact_match: price_diff == 0 → +0.4
├── close_match: price_diff <= 1 → +0.2
└── ELSE → +0.0
```

### **Step 4: Learning Output**
```
├── Sort by history_score DESC
├── Limit to top 5 recommendations
└── Output with learning insights:
    ├── Restaurant details + history_score
    ├── "Why recommended": category overlaps, location preferences, price alignment
    └── Learning summary: "Based on your X high-rated experiences"
```

---

## Algorithm 3: Enhanced Social Collaborative Filtering

### **Step 1: Multi-Dimensional User Similarity**
```
INPUT: current_user, all_users
FOR each other_user IN users:
    ├── similarity_data = CALCULATE_ENHANCED_SIMILARITY(current_user, other_user)
    ├── IF similarity_data.total_similarity > 0.2 → add_to_similar_users
    └── STORE: {user_id, similarity, breakdown_scores}

CALCULATE_ENHANCED_SIMILARITY(user1, user2):
├── cuisine_similarity = JACCARD_SIMILARITY(user1.cuisines, user2.cuisines)
├── price_compatibility = CALCULATE_PRICE_OVERLAP(user1.prices, user2.prices)
├── location_overlap = JACCARD_SIMILARITY(user1.locations, user2.locations)
├── context_similarity = JACCARD_SIMILARITY(user1.contexts, user2.contexts)
├── dietary_compatibility = JACCARD_SIMILARITY(user1.dietary, user2.dietary)
└── RETURN weighted_average:
    └── (cuisine × 0.40) + (price × 0.20) + (location × 0.15) + (context × 0.15) + (dietary × 0.10)

JACCARD_SIMILARITY(set1, set2):
├── intersection = LENGTH(set1 ∩ set2)
├── union = LENGTH(set1 ∪ set2)
└── RETURN intersection / union
```

### **Step 2: Similar User Filtering & Ranking**
```
├── similar_users = FILTER(users WHERE similarity > 0.2)
├── SORT similar_users BY similarity DESC
├── top_similar = LIMIT(similar_users, 8)
└── OUTPUT similarity breakdown for top match
```

### **Step 3: Collaborative Recommendation Collection**
```
similar_user_ids = EXTRACT(user_ids from top_similar)
├── similar_interactions = interactions WHERE:
    ├── user_id IN similar_user_ids
    ├── rating >= 4.0 (high-rated only)
    └── place_id NOT IN current_user_visited_places

place_scoring = {}
FOR each interaction IN similar_interactions:
    ├── place_id = interaction.place_id
    ├── user_similarity = GET_SIMILARITY(interaction.user_id)
    ├── restaurant_data = GET_RESTAURANT(place_id)
    ├── personal_match = CALCULATE_RESTAURANT_MATCH(restaurant_data, current_user)
    └── enhanced_score = (user_similarity × rating) + (personal_match × 0.5)
```

### **Step 4: Enhanced Social Scoring**
```
FOR each place_id IN place_scores:
    ├── scores_list = ALL_SCORES_FOR_PLACE(place_id)
    ├── average_score = MEAN(scores_list)
    ├── recommender_count = LENGTH(scores_list)
    └── STORE: {place, enhanced_score, recommender_count, score_details}
```

### **Step 5: Social Intelligence Output**
```
├── Sort by enhanced_score DESC
├── Limit to top 5 recommendations
└── Output with social proof:
    ├── Restaurant details + enhanced_score
    ├── "Social proof": X similar users with multi-dimensional taste match
    ├── "Perfect because": top personal match reasons
    └── "Recommended by": similarity scores + ratings from top recommenders
```

---

## Algorithm 4: Cluster-Based Intelligence

### **Step 1: User Cluster History Analysis**
```
INPUT: user_id
├── user_interactions = GET_USER_INTERACTIONS(user_id)
├── cluster_analysis = {}

FOR each interaction IN user_interactions:
    ├── place = GET_PLACE(interaction.place_id)
    ├── cluster = place.cluster_label
    ├── rating = interaction.rating
    └── ADD_TO_CLUSTER_ANALYSIS(cluster, rating)

cluster_preferences = {}
FOR each cluster IN cluster_analysis:
    ├── ratings_list = cluster_analysis[cluster]
    ├── avg_rating = MEAN(ratings_list)
    ├── interaction_count = LENGTH(ratings_list)
    ├── IF avg_rating >= 4.0:
        └── preference_score = avg_rating × (1 + LOG(interaction_count))
```

### **Step 2: Preferred Cluster Ranking**
```
├── preferred_clusters = FILTER(clusters WHERE avg_rating >= 4.0)
├── SORT preferred_clusters BY preference_score DESC
└── OUTPUT top 3 clusters with statistics
```

### **Step 3: Cluster-Based Restaurant Scoring**
```
visited_places = GET_VISITED_PLACES(user_id)
recommendations = []

FOR each cluster IN preferred_clusters:
    ├── cluster_places = GET_PLACES_IN_CLUSTER(cluster)
    ├── unvisited_places = FILTER(cluster_places WHERE NOT IN visited_places)
    
    FOR each place IN unvisited_places:
        ├── cluster_preference = GET_CLUSTER_PREFERENCE_SCORE(cluster)
        ├── place_quality = place.rating × 1.5
        ├── price_match_bonus = 0.5 IF exact_price ELSE 0.2 IF close_price ELSE 0
        ├── category_match_bonus = 0.3 IF category_overlap ELSE 0
        └── total_score = cluster_preference + place_quality + price_match_bonus + category_match_bonus
```

### **Step 4: Cluster Intelligence Output**
```
├── Sort by total_score DESC
├── Limit to top 5 recommendations
└── Output with cluster insights:
    ├── Restaurant details + cluster_score
    ├── "Cluster": semantic cluster name
    ├── "Why recommended": Similar to clusters you've enjoyed
    └── Cluster preference summary with visit counts and ratings
```

---

## Algorithm 5: Hybrid Social+Cluster

### **Step 1: Social User Discovery**
```
INPUT: current_user
├── similar_users = FIND_SIMILAR_USERS(current_user, similarity_threshold=0.3)
├── SORT similar_users BY similarity DESC
├── top_similar = LIMIT(similar_users, 8)
└── OUTPUT social analysis summary
```

### **Step 2: Social Cluster Preference Analysis**
```
similar_user_ids = EXTRACT(user_ids from top_similar)
├── similar_interactions = GET_INTERACTIONS(similar_user_ids, min_rating=4.0)

cluster_social_scores = {}
FOR each interaction IN similar_interactions:
    ├── place = GET_PLACE(interaction.place_id)
    ├── cluster = place.cluster_label
    ├── user_similarity = GET_USER_SIMILARITY(interaction.user_id)
    ├── social_score = interaction.rating × user_similarity
    └── ADD_TO_CLUSTER_SOCIAL_SCORES(cluster, social_score)

cluster_preferences = {}
FOR each cluster IN cluster_social_scores:
    ├── scores_list = cluster_social_scores[cluster]
    ├── avg_social_score = MEAN(scores_list)
    ├── recommendation_count = LENGTH(scores_list)
    └── total_social_weight = SUM(scores_list)
```

### **Step 3: Social Cluster Ranking**
```
├── SORT clusters BY total_social_weight DESC
├── top_social_clusters = LIMIT(clusters, 5)
└── OUTPUT cluster insights with social scores
```

### **Step 4: Hybrid Scoring Algorithm**
```
visited_places = GET_VISITED_PLACES(current_user)
hybrid_recommendations = []

FOR each cluster IN top_social_clusters:
    ├── cluster_places = GET_UNVISITED_PLACES_IN_CLUSTER(cluster, visited_places)
    
    FOR each place IN cluster_places:
        ├── social_cluster_score = GET_TOTAL_SOCIAL_WEIGHT(cluster)
        ├── place_quality = place.rating × 2.0
        ├── personal_match = CALCULATE_PERSONAL_ALIGNMENT(place, current_user)
        └── hybrid_score = social_cluster_score + place_quality + personal_match

CALCULATE_PERSONAL_ALIGNMENT(place, user):
├── category_match = 0.5 IF cuisine_overlap ELSE 0
├── price_match = 0.3 IF price_compatible ELSE 0
└── RETURN category_match + price_match
```

### **Step 5: Hybrid Intelligence Output**
```
├── Sort by hybrid_score DESC
├── Limit to top 5 recommendations
└── Output with hybrid reasoning:
    ├── Restaurant details + hybrid_score
    ├── "Cluster": semantic cluster name
    ├── "Social proof": X similar users love this cluster
    ├── "Why perfect": hybrid reasoning (social + quality + personal fit)
    └── Cluster social analytics summary
```

---

## Algorithm 6: Explore Mode Discovery

### **Step 1: Adventure Zone Detection**
```
INPUT: user_data
├── user_neighborhoods = user.preferred_neighborhoods[]
├── user_cuisines = user.preferred_cuisines[]
├── user_prices = user.price_range[]
├── adventure_level = user.explore_rate
└── comfort_zone = DEFINE_COMFORT_ZONE(user_data)
```

### **Step 2: Multi-Dimensional Filtering**
```
exploration_candidates = places.copy()

APPLY_FILTERS:
├── neighborhood_expansion:
    ├── IF adventure_level > 0.3 → include_adjacent_neighborhoods
    └── ELSE → limit_to_preferred_neighborhoods
├── cuisine_exploration:
    ├── IF adventure_level > 0.4 → include_fusion_cuisines
    └── ELSE → limit_to_familiar_cuisines
└── price_flexibility:
    ├── IF adventure_level > 0.35 → expand_price_range(±1)
    └── ELSE → strict_price_preference
```

### **Step 3: Discovery Scoring**
```
FOR each place IN exploration_candidates:
    ├── base_score = place.rating × 0.4
    ├── adventure_bonus = CALCULATE_ADVENTURE_BONUS(place, user)
    ├── quality_assurance = 0.3 IF rating >= 4.0 ELSE 0
    ├── novelty_score = CALCULATE_NOVELTY_FACTOR(place, user)
    └── exploration_score = base_score + adventure_bonus + quality_assurance + novelty_score

CALCULATE_ADVENTURE_BONUS(place, user):
├── neighborhood_novelty = 0.5 IF new_neighborhood ELSE 0
├── cuisine_novelty = 0.4 IF new_cuisine ELSE 0
├── price_stretch = 0.2 IF price_stretch_acceptable ELSE 0
└── RETURN adventure_level × (neighborhood_novelty + cuisine_novelty + price_stretch)

CALCULATE_NOVELTY_FACTOR(place, user):
├── unique_categories = COUNT(categories NOT IN user.tried_categories)
├── ambience_novelty = 0.3 IF new_ambience_type ELSE 0
└── RETURN (unique_categories × 0.1) + ambience_novelty
```

### **Step 4: Exploration Output**
```
├── Sort by exploration_score DESC
├── Limit to top 5 discoveries
└── Output with adventure insights:
    ├── Restaurant details + exploration_score
    ├── "Adventure Level": user.explore_rate × 100%
    ├── "New Experience": highlight novel aspects
    ├── "Safe Bets": quality assurance indicators
    └── "Stretch Factor": comfort zone expansion details
```

---

## Common Output Format Template

```
RESTAURANT_OUTPUT_FORMAT:
├── Rank. Restaurant_Name (Neighborhood)
├── Rating: X.X ★★★★★ | Price: Rs.X | Algorithm_Score: X.XXX
├── Categories: category1, category2, category3
├── Special_Attributes: [VEGETARIAN], [VEGAN], [HIGH_RATED], etc.
├── Algorithm_Specific_Reasoning: Why this recommendation
└── Additional_Context: Social proof, learning insights, cluster info, etc.

SUMMARY_OUTPUT:
├── Applied_Filters: Location, Category, Price constraints
├── Algorithm_Used: Name and key methodology
├── Results_Count: X recommendations found
├── Special_Notes: Adventure level, similarity thresholds, time context
└── Exploration_Encouragement: "Try something new!" or comfort zone suggestions
```

---

## System Integration Flow

```
MAIN_SYSTEM_FLOW:
├── User_Authentication → Load user preferences
├── Algorithm_Selection → Choose recommendation engine
├── Data_Loading → places.csv + users.csv + interactions.csv
├── Algorithm_Execution → Run selected algorithm with parameters
├── Results_Ranking → Sort and limit to top 5
├── Output_Formatting → Standardized display with algorithm-specific insights
└── User_Feedback_Loop → Capture interactions for learning
```

**Total Complexity**: O(n²) worst case (user similarity calculations)  
**Typical Performance**: O(n log n) for most algorithms  
**Optimization**: Pre-computed similarities and cached cluster preferences  

---

**Algorithm Documentation Generated**: November 2025  
**System Version**: AroundMe v2.0 Enhanced Multi-Preference  
**Implementation**: Production-ready with 5,106 interaction training data  