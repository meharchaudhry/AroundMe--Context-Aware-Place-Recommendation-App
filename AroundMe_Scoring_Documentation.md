# AroundMe Recommendation System - Scoring Algorithms Documentation

## System Overview
**Project**: AroundMe Restaurant Recommendation System  
**Version**: 2.0 Enhanced Multi-Preference  
**Date**: November 2025  
**Algorithms**: 6 Different Recommendation Engines  

---

## Table of Contents
1. [Time-Based Recommendation Scoring](#time-based)
2. [User Similarity Calculation (Collaborative Filtering)](#user-similarity)
3. [Restaurant Match Scoring](#restaurant-match)
4. [History-Based Recommendation Scoring](#history-based)
5. [Cluster-Based Recommendation Scoring](#cluster-based)
6. [Hybrid Social+Cluster Scoring](#hybrid-scoring)
7. [Maximum Score Analysis](#maximum-scores)
8. [Implementation Examples](#examples)

---

## 1. Time-Based Recommendation Scoring {#time-based}

### Purpose
Provides context-aware recommendations based on current time and dining context.

### Formula
```
Time_Score = Base_Score + Time_Bonus + Price_Match + Category_Match + Quality_Bonus
```

### Components

#### Base Score (30% weight)
```python
Base_Score = Restaurant_Rating × 0.3
Range: 0 to 1.5 (for 5★ restaurant)
```

#### Time Context Bonuses
```python
Time_Bonus_Map = {
    'breakfast':      +1.5  # cafe, bakery, healthy
    'tea_time':       +1.4  # cafe, dessert
    'dinner':         +1.3  # italian, mexican, asian
    'weekend_brunch': +1.3  # cafe, healthy, dessert
    'lunch':          +1.2  # south_indian, north_indian, asian
    'late_night':     +1.1  # street_food, pizza
}
```

#### Price Compatibility
```python
if Restaurant_Price == User_Price_Preference:
    Price_Score = +0.4
elif abs(Restaurant_Price - User_Price_Preference) == 1:
    Price_Score = +0.2
else:
    Price_Score = 0
```

#### Category Preference Match
```python
if any(user_category in restaurant_categories):
    Category_Score = +0.5
else:
    Category_Score = 0
```

#### Quality Bonus
```python
if Restaurant_Rating >= 4.5:
    Quality_Score = +0.2
else:
    Quality_Score = 0
```

### Maximum Possible Score: 4.1
**Example Calculation:**
```
Restaurant: "Tea Garden Cafe" (5.0★, Rs.2, cafe,dessert)
User: Prefers cafe, Rs.2 budget, tea_time context
Time: 4:30 PM

Base_Score = 5.0 × 0.3 = 1.5
Time_Bonus = 1.4 (tea_time + cafe match)
Price_Match = 0.4 (exact Rs.2 match)
Category_Match = 0.5 (cafe overlap)
Quality_Bonus = 0.2 (5.0 >= 4.5)

Final_Score = 1.5 + 1.4 + 0.4 + 0.5 + 0.2 = 4.0
```

---

## 2. User Similarity Calculation (Collaborative Filtering) {#user-similarity}

### Purpose
Finds users with similar multi-dimensional preferences for collaborative filtering.

### Formula
```
User_Similarity = (Cuisine_Jaccard × 0.40) + (Price_Overlap × 0.20) + 
                  (Location_Overlap × 0.15) + (Context_Similarity × 0.15) + 
                  (Dietary_Compatibility × 0.10)
```

### Components

#### Jaccard Similarity Calculation
```python
Jaccard_Similarity = |Set1 ∩ Set2| / |Set1 ∪ Set2|
Where:
∩ = Intersection (common elements)
∪ = Union (all unique elements)
```

#### 1. Cuisine Similarity (40% weight)
```python
Example:
User1_Cuisines = {italian, asian, pizza}
User2_Cuisines = {italian, mexican, pizza}
Intersection = {italian, pizza} = 2
Union = {italian, asian, pizza, mexican} = 4
Cuisine_Jaccard = 2/4 = 0.5
Weighted_Score = 0.5 × 0.40 = 0.20
```

#### 2. Price Range Overlap (20% weight)
```python
Example:
User1_Prices = {1, 2, 3}
User2_Prices = {2, 3, 4}
Intersection = {2, 3} = 2
Union = {1, 2, 3, 4} = 4
Price_Overlap = 2/4 = 0.5
Weighted_Score = 0.5 × 0.20 = 0.10
```

#### 3. Location Overlap (15% weight)
```python
Example:
User1_Locations = {Baner, Camp}
User2_Locations = {Camp, FC_Road}
Intersection = {Camp} = 1
Union = {Baner, Camp, FC_Road} = 3
Location_Overlap = 1/3 = 0.33
Weighted_Score = 0.33 × 0.15 = 0.05
```

#### 4. Context Similarity (15% weight)
```python
Example:
User1_Contexts = {social, casual}
User2_Contexts = {casual, romantic}
Intersection = {casual} = 1
Union = {social, casual, romantic} = 3
Context_Similarity = 1/3 = 0.33
Weighted_Score = 0.33 × 0.15 = 0.05
```

#### 5. Dietary Compatibility (10% weight)
```python
Example:
User1_Dietary = {no_restrictions}
User2_Dietary = {no_restrictions, healthy}
Intersection = {no_restrictions} = 1
Union = {no_restrictions, healthy} = 2
Dietary_Compatibility = 1/2 = 0.5
Weighted_Score = 0.5 × 0.10 = 0.05
```

### Maximum Possible Score: 1.0 (100% similarity)
**Example Calculation:**
```
Total_Similarity = 0.20 + 0.10 + 0.05 + 0.05 + 0.05 = 0.45 (45% similar)
```

---

## 3. Restaurant Match Scoring {#restaurant-match}

### Purpose
Calculates how well a restaurant matches user's multi-dimensional preferences.

### Formula
```
Restaurant_Score = Cuisine_Score + Location_Score + Price_Score + 
                  Quality_Score + Adventure_Score + Dietary_Score
```

### Components

#### 1. Cuisine Match (40% weight)
```python
Cuisine_Score = (Shared_Cuisines / Total_User_Cuisines) × 2.0
Max_Score = 2.0 (when all user cuisines are matched)

Example:
User_Cuisines = {italian, asian, pizza} (3 total)
Restaurant_Cuisines = {italian, pizza, dessert}
Shared = {italian, pizza} (2 shared)
Cuisine_Score = (2/3) × 2.0 = 1.33
```

#### 2. Location Preference (25% weight)
```python
if Restaurant_Neighborhood in User_Preferred_Neighborhoods:
    Location_Score = +1.5
else:
    Location_Score = 0
```

#### 3. Price Compatibility (20% weight)
```python
if Restaurant_Price in User_Price_Range:
    Price_Score = +1.0
elif any(abs(Restaurant_Price - p) == 1 for p in User_Price_Range):
    Price_Score = +0.5
else:
    Price_Score = 0
```

#### 4. Quality Bonus (10% weight)
```python
if Restaurant_Rating >= 4.5:
    Quality_Score = +0.6
elif Restaurant_Rating >= 4.0:
    Quality_Score = +0.3
else:
    Quality_Score = 0
```

#### 5. Adventure Factor (5% weight)
```python
if User_Adventure_Level > 0.7:
    Adventure_Score = +0.3
else:
    Adventure_Score = 0
```

#### 6. Dietary Bonuses
```python
Dietary_Bonuses = {
    'vegetarian' + restaurant.veg_only: +0.4
    'vegan' + 'vegan' in restaurant: +0.4
    'healthy' + 'healthy' in restaurant: +0.3
}
Max_Dietary_Score = 1.1 (all bonuses)
```

### Maximum Possible Score: 6.5
**Example Calculation:**
```
Restaurant: "Perfect Bistro" (4.8★, Rs.2, {asian,pizza,vegan}, Baner, veg_only)
User: Likes {asian,pizza}, {Baner,Camp}, Rs.{1,2,3}, vegetarian+vegan, adventure=0.8

Cuisine_Score = (2/2) × 2.0 = 2.0  (100% match)
Location_Score = 1.5  (Baner match)
Price_Score = 1.0  (Rs.2 in range)
Quality_Score = 0.6  (4.8 >= 4.5)
Adventure_Score = 0.3  (0.8 > 0.7)
Dietary_Score = 0.4 + 0.4 = 0.8  (vegetarian + vegan)

Final_Score = 2.0 + 1.5 + 1.0 + 0.6 + 0.3 + 0.8 = 6.2
```

---

## 4. History-Based Recommendation Scoring {#history-based}

### Purpose
Learns from user's past interactions to recommend similar places they haven't tried.

### Formula
```
History_Score = Base_Rating + Category_Overlap_Bonus + Neighborhood_Bonus + 
                Price_Alignment + Quality_Bonus
```

### Components

#### Base Score
```python
Base_Score = Restaurant_Rating × 0.4
Range: 0 to 2.0 (for 5★ restaurant)
```

#### Category Similarity Bonus
```python
place_categories = set(restaurant_categories)
enjoyed_categories = set(from_high_rated_history)
category_overlap = len(place_categories.intersection(enjoyed_categories))
Category_Score = category_overlap × 0.3
```

#### Neighborhood Preference
```python
if restaurant_neighborhood in enjoyed_neighborhoods:
    Neighborhood_Score = +0.5
else:
    Neighborhood_Score = 0
```

#### Price Alignment
```python
preferred_price = mean(historical_high_rated_prices)
price_diff = abs(restaurant_price - preferred_price)
if price_diff == 0:
    Price_Score = +0.4
elif price_diff <= 1:
    Price_Score = +0.2
else:
    Price_Score = 0
```

#### Quality Bonus
```python
if Restaurant_Rating >= 4.5:
    Quality_Score = +0.3
else:
    Quality_Score = 0
```

### Example Calculation
```
User History: 8 high-rated visits (avg Rs.2, loves {asian,cafe}, in {Baner,Camp})
Restaurant: "New Asian Cafe" (4.6★, Rs.2, {asian,cafe,healthy}, Baner)

Base_Score = 4.6 × 0.4 = 1.84
Category_Score = 2 × 0.3 = 0.6  (asian,cafe overlap)
Neighborhood_Score = 0.5  (Baner in enjoyed)
Price_Score = 0.4  (Rs.2 exact match)
Quality_Score = 0.3  (4.6 >= 4.5)

History_Score = 1.84 + 0.6 + 0.5 + 0.4 + 0.3 = 3.64
```

---

## 5. Cluster-Based Recommendation Scoring {#cluster-based}

### Purpose
Recommends places from clusters that user has historically enjoyed.

### Formula
```
Cluster_Score = Cluster_Preference_Score + Place_Quality + Personal_Match
```

### Components

#### Cluster Preference Score
```python
cluster_avg_rating = mean(user_ratings_in_cluster)
interaction_count = count(user_interactions_in_cluster)
Cluster_Preference = cluster_avg_rating × (1 + log(interaction_count))
```

#### Place Quality
```python
Place_Quality = Restaurant_Rating × 1.5
```

#### Personal Match Bonuses
```python
price_match_bonus = 0.5 if exact_price else 0.2 if close_price else 0
category_match_bonus = 0.3 if category_overlap else 0
Personal_Match = price_match_bonus + category_match_bonus
```

### Example Calculation
```
Cluster: "Katraj student budget"
User's History: 12 visits, average 4.4★ rating in this cluster
Restaurant: "New Budget Bistro" (4.7★, Rs.1, matches preferences)

Cluster_Preference = 4.4 × (1 + log(12)) = 4.4 × (1 + 1.08) = 9.15
Place_Quality = 4.7 × 1.5 = 7.05
Personal_Match = 0.5 + 0.3 = 0.8

Cluster_Score = 9.15 + 7.05 + 0.8 = 16.0
```

---

## 6. Hybrid Social+Cluster Scoring {#hybrid-scoring}

### Purpose
Combines social collaborative filtering with cluster analysis for maximum intelligence.

### Formula
```
Hybrid_Score = Social_Cluster_Score + Place_Quality + Personal_Match
```

### Components

#### Social Cluster Score
```python
For each similar user who rated places in this cluster:
    user_similarity = calculated_similarity_score
    rating = user_rating_for_place
    weighted_score = rating × user_similarity

Social_Cluster_Score = sum(weighted_scores) / count(ratings)
```

#### Place Quality (Enhanced)
```python
Place_Quality = Restaurant_Rating × 2.0
```

#### Personal Match (Enhanced)
```python
Personal_Match = Restaurant_Match_Score × 0.5
(Uses full restaurant match algorithm with 0.5 multiplier)
```

### Example Calculation
```
Cluster: "Camp trendy dining"
Similar Users: 5 users with ratings [4.5, 4.8, 4.2, 4.7, 4.6] and similarities [0.7, 0.8, 0.6, 0.9, 0.75]
Restaurant: "Trendy Fusion" (4.8★, perfect personal match score 5.0)

Social_Cluster_Score = (4.5×0.7 + 4.8×0.8 + 4.2×0.6 + 4.7×0.9 + 4.6×0.75) / 5
                     = (3.15 + 3.84 + 2.52 + 4.23 + 3.45) / 5 = 3.44

Place_Quality = 4.8 × 2.0 = 9.6
Personal_Match = 5.0 × 0.5 = 2.5

Hybrid_Score = 3.44 + 9.6 + 2.5 = 15.54
```

---

## 7. Maximum Score Analysis {#maximum-scores}

### Theoretical Maximums

| Algorithm | Max Score | Typical High | Components |
|-----------|-----------|--------------|------------|
| **Time-Based** | 4.1 | 3.8 | Base(1.5) + Time(1.5) + Price(0.4) + Category(0.5) + Quality(0.2) |
| **User Similarity** | 1.0 | 0.8 | Perfect overlap in all 5 dimensions |
| **Restaurant Match** | 6.5 | 5.5 | Cuisine(2.0) + Location(1.5) + Price(1.0) + Quality(0.6) + Adventure(0.3) + Dietary(1.1) |
| **History-Based** | ~5.0 | 4.0 | Base(2.0) + Categories(1.5) + Neighborhood(0.5) + Price(0.4) + Quality(0.3) |
| **Cluster-Based** | 23.3 | 18.0 | ClusterPref(15.0) + Quality(7.5) + Personal(0.8) |
| **Hybrid Social+Cluster** | 63.25 | 45.0 | SocialCluster(50.0) + Quality(10.0) + Personal(3.25) |

### Score Interpretation

#### Time-Based Scores
- **3.5+**: Excellent time-context match
- **2.5-3.4**: Good match with some bonuses
- **1.5-2.4**: Decent match, basic compatibility
- **<1.5**: Poor time-context fit

#### User Similarity Scores
- **0.7+**: Very similar users (strong recommendations)
- **0.4-0.6**: Moderately similar users
- **0.2-0.3**: Some similarity (minimum threshold)
- **<0.2**: Not similar enough for recommendations

#### Restaurant Match Scores
- **5.0+**: Perfect or near-perfect match
- **3.5-4.9**: Excellent match with most criteria
- **2.0-3.4**: Good match with some criteria
- **<2.0**: Basic compatibility only

---

## 8. Implementation Examples {#examples}

### Example 1: Time-Based Scoring
```python
# Dinner time recommendation
user = {
    'pref_categories': 'italian,asian,pizza',
    'price_preference': 2,
    'home_neighborhood': 'Baner'
}

restaurant = {
    'name': 'Italian Fusion',
    'rating': 4.6,
    'price_level': 2,
    'categories': 'italian,pizza,dessert',
    'neighborhood': 'Baner'
}

time_context = 'dinner'

# Calculation
base_score = 4.6 * 0.3 = 1.38
time_bonus = 1.3  # dinner + italian match
price_match = 0.4  # exact match
category_match = 0.5  # italian overlap  
quality_bonus = 0.2  # 4.6 >= 4.5

final_score = 1.38 + 1.3 + 0.4 + 0.5 + 0.2 = 3.78
```

### Example 2: User Similarity Calculation
```python
user1 = {
    'preferred_cuisines': 'italian,asian,cafe',
    'preferred_neighborhoods': 'Baner,Camp',
    'preferred_prices': '1,2,3',
    'dining_contexts': 'social,casual',
    'dietary_preferences': 'no_restrictions'
}

user2 = {
    'preferred_cuisines': 'italian,mexican,cafe',
    'preferred_neighborhoods': 'Camp,FC_Road',
    'preferred_prices': '2,3,4',
    'dining_contexts': 'casual,romantic',
    'dietary_preferences': 'no_restrictions,healthy'
}

# Jaccard calculations
cuisine_jaccard = 2/4 = 0.5  # {italian,cafe} / {italian,asian,cafe,mexican}
price_jaccard = 2/4 = 0.5    # {2,3} / {1,2,3,4}
location_jaccard = 1/3 = 0.33 # {Camp} / {Baner,Camp,FC_Road}
context_jaccard = 1/3 = 0.33  # {casual} / {social,casual,romantic}
dietary_jaccard = 1/2 = 0.5   # {no_restrictions} / {no_restrictions,healthy}

similarity = (0.5*0.4) + (0.5*0.2) + (0.33*0.15) + (0.33*0.15) + (0.5*0.1)
           = 0.2 + 0.1 + 0.05 + 0.05 + 0.05 = 0.45 (45% similar)
```

### Example 3: Restaurant Match Scoring
```python
user = {
    'preferred_cuisines': 'asian,cafe,dessert',
    'preferred_neighborhoods': 'Baner,Camp,FC_Road',
    'preferred_prices': '1,2,3',
    'adventure_level': 0.8,
    'dietary_preferences': 'vegan,healthy'
}

restaurant = {
    'categories': 'asian,cafe,vegan',
    'neighborhood': 'Baner',
    'price_level': 2,
    'rating': 4.7,
    'veg_only': False
}

# Calculation
cuisine_score = (2/3) * 2.0 = 1.33  # 2 shared out of 3 user cuisines
location_score = 1.5  # Baner in preferred
price_score = 1.0     # Rs.2 in range {1,2,3}
quality_score = 0.6   # 4.7 >= 4.5
adventure_score = 0.3 # 0.8 > 0.7
vegan_bonus = 0.4     # vegan preference + vegan category

total_score = 1.33 + 1.5 + 1.0 + 0.6 + 0.3 + 0.4 = 5.13
```

---

## Technical Notes

### Data Types
- **Ratings**: Float (1.0 - 5.0)
- **Prices**: Integer (1-4)
- **Categories**: Comma-separated strings
- **Neighborhoods**: String enumeration
- **Similarities**: Float (0.0 - 1.0)

### Performance Considerations
- **Time Complexity**: O(n) for most algorithms, O(n²) for user similarity
- **Space Complexity**: O(n) for storing scores
- **Optimization**: Pre-compute user similarities, cache cluster preferences

### Validation
- All algorithms tested with synthetic dataset (139 restaurants, 228 users, 5106 interactions)
- Score ranges validated against theoretical maximums
- Cross-validation performed with multiple user profiles

### Future Enhancements
1. **Dynamic Weight Adjustment**: Learn optimal weights from user feedback
2. **Temporal Factors**: Consider day of week, season, weather
3. **Social Network Effects**: Include friend recommendations
4. **Machine Learning Integration**: Use ML models for scoring refinement

---

**Document Generated**: November 2025  
**System Version**: AroundMe v2.0 Enhanced Multi-Preference  
**Total Algorithms**: 6 Different Recommendation Engines  
**Author**: AroundMe Development Team