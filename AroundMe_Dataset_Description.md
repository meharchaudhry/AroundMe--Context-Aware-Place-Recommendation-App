# AroundMe Synthetic Dataset - Data Description

## Dataset Overview
**Project**: AroundMe Restaurant Recommendation System  
**Dataset Type**: Synthetic Data for Testing & Development  
**Generated**: November 2025  
**Purpose**: Multi-dimensional recommendation algorithm testing  
**Location**: Pune, Maharashtra, India  

---

## File Structure Summary

| File | Records | Purpose | Key Features |
|------|---------|---------|-------------|
| **users.csv** | 228 users | User profiles with preferences | Multi-segment user types, preference vectors |
| **places.csv** | 139 restaurants | Restaurant database with clustering | Semantic clusters, multi-category classification |
| **interactions.csv** | 5,106 interactions | User-restaurant interaction history | Multiple interaction types, temporal data |

---

## 1. Users.csv - User Profiles Dataset

### File Statistics
- **Total Records**: 228 users (229 lines including header)
- **File Size**: ~15KB
- **Encoding**: UTF-8
- **Format**: Comma-separated values

### Schema Description

| Column | Data Type | Description | Example Values | Constraints |
|--------|-----------|-------------|---------------|-------------|
| `user_id` | String | Unique user identifier | u_0001, u_0002, u_0228 | Format: u_NNNN |
| `segment` | String | User behavior segment | italian_date_kp, budget_cafe_fc, veg_hingej_baner | 8 distinct segments |
| `home_neighborhood` | String | User's primary neighborhood | Koregaon Park, Baner, Camp, FC Road | 8 Pune neighborhoods |
| `pref_categories` | String (CSV) | Preferred cuisine types | "italian,pizza", "cafe,dessert" | Comma-separated list |
| `price_preference` | Integer | Budget preference level | 1, 2, 3, 4 | 1=Budget, 4=Premium |
| `distance_tolerance_km` | Float | Max travel distance (km) | 3.0, 4.5, 6.2 | Range: 2.0-8.0 km |
| `ambience_prefs` | String | Preferred dining atmosphere | date, study, group, casual | Single preference |
| `explore_rate` | Float | Willingness to try new places | 0.25, 0.3, 0.4 | Range: 0.2-0.4 |

### User Segments Distribution

| Segment | Count | Description | Characteristics |
|---------|-------|-------------|----------------|
| `italian_date_kp` | 32 | Italian food lovers in KP | Price: Rs.2, Distance: 4km, Ambience: date, Explore: 0.25 |
| `budget_cafe_fc` | 24 | Budget cafe enthusiasts | Price: Rs.1, Distance: 3km, Ambience: study, Explore: 0.3 |
| `veg_hingej_baner` | 28 | Vegetarian families in Baner | Price: Rs.2, Distance: 4.5km, Ambience: group, Explore: 0.2 |
| `street_food_katraj` | 25 | Street food lovers | Price: Rs.1, Distance: 2.5km, Ambience: casual, Explore: 0.35 |
| `upscale_camp_mg` | 30 | Premium diners in Camp/MG | Price: Rs.3-4, Distance: 5km, Ambience: upscale, Explore: 0.3 |
| `asian_kothrud_fam` | 26 | Asian cuisine families | Price: Rs.2-3, Distance: 4km, Ambience: family, Explore: 0.25 |
| `cafe_viman_nagar` | 32 | Cafe culture enthusiasts | Price: Rs.2, Distance: 3.5km, Ambience: study, Explore: 0.4 |
| `foodie_explorer` | 31 | Adventurous food explorers | Price: Rs.2-4, Distance: Variable, Ambience: Mixed, Explore: 0.4 |

### Sample User Profiles

```csv
u_0001,italian_date_kp,Koregaon Park,"italian,pizza",2,4.0,date,0.25
u_0049,budget_cafe_fc,FC Road,"cafe,dessert",1,3.0,study,0.3
u_0072,veg_hingej_baner,Baner,"veg_only,north_indian",2,4.5,group,0.2
```

### Data Quality Notes
- **Consistency**: All users within same segment share identical characteristics (by design)
- **Realism**: Segments based on actual Pune dining patterns
- **Coverage**: Represents diverse user types across economic and preference spectrums
- **Missing Values**: None (complete dataset)

---

## 2. Places.csv - Restaurant Database

### File Statistics
- **Total Records**: 139 restaurants (140 lines including header)
- **File Size**: ~25KB
- **Encoding**: UTF-8
- **Format**: Comma-separated values

### Schema Description

| Column | Data Type | Description | Example Values | Constraints |
|--------|-----------|-------------|---------------|-------------|
| `place_id` | String | Unique restaurant identifier | p_0001, p_0002, p_0139 | Format: p_NNNN |
| `name` | String | Restaurant name | "Pizza Grill & Co", "Asian Oven Hub" | Synthetic names |
| `neighborhood` | String | Location area | Koregaon Park, Baner, Camp | 8 Pune neighborhoods |
| `cluster_label` | String | Semantic cluster assignment | "KP date-night & Italian", "Baner upscale dining" | 8 distinct clusters |
| `lat` | Float | Latitude coordinate | 18.542715, 18.569395 | Pune coordinate range |
| `lng` | Float | Longitude coordinate | 73.896372, 73.916955 | Pune coordinate range |
| `categories` | String (CSV) | Cuisine/restaurant types | "asian,pizza,south_indian" | Comma-separated |
| `price_level` | Integer | Price category | 1, 2, 3, 4 | 1=Budget, 4=Premium |
| `rating` | Float | Average user rating | 3.48, 4.88, 4.97 | Range: 3.0-5.0 |
| `user_rating_count` | Integer | Number of ratings | 50 | Standardized to 50 |
| `ambience` | String (CSV) | Atmosphere tags | "cozy,date", "study,group" | Comma-separated |
| `veg_only` | Integer | Vegetarian-only flag | 0, 1 | Boolean (0=Mixed, 1=Veg-only) |
| `cat_list` | String | Categories as Python list | "['asian', 'pizza']" | For easy parsing |

### Geographic Distribution

| Neighborhood | Count | Cluster Types | Characteristics |
|--------------|-------|---------------|----------------|
| **Koregaon Park** | 24 | KP date-night & Italian | Premium dating spots, Italian cuisine focus |
| **FC Road** | 18 | FC Road student hangouts | Budget-friendly, study-oriented cafes |
| **Baner** | 21 | Baner upscale dining | Mid-to-premium, family & group dining |
| **Viman Nagar** | 19 | Viman Nagar malls & cafes | Mall culture, cafe & bakery focus |
| **Camp** | 15 | Camp trendy classics, MG Road classics | Traditional & trendy mix |
| **Kothrud** | 16 | Kothrud family spots | Family-oriented, diverse cuisines |
| **Katraj** | 14 | Katraj student budget | Ultra-budget, street food heavy |
| **Hinjawadi** | 12 | Hinjawadi working professionals | Office-goer focused, quick dining |

### Cuisine Categories Distribution

| Category | Frequency | Neighborhoods | Price Range |
|----------|-----------|---------------|-------------|
| **italian** | 45 restaurants | All areas | Rs.1-4 |
| **pizza** | 38 restaurants | KP, Baner, Camp | Rs.1-3 |
| **asian** | 35 restaurants | All areas | Rs.1-3 |
| **cafe** | 32 restaurants | VN, FC, Hinjawadi | Rs.1-3 |
| **bar** | 28 restaurants | All areas | Rs.1-4 |
| **dessert** | 25 restaurants | FC, VN, KP | Rs.1-2 |
| **south_indian** | 22 restaurants | All areas | Rs.1-2 |
| **north_indian** | 20 restaurants | Baner, Kothrud | Rs.1-3 |
| **veg_only** | 18 restaurants | All areas | Rs.1-3 |
| **mexican** | 15 restaurants | KP, FC, Camp | Rs.1-3 |

### Semantic Clusters

| Cluster Label | Restaurant Count | Avg Price | Dominant Categories |
|---------------|------------------|-----------|-------------------|
| **KP date-night & Italian** | 24 | 2.1 | italian, pizza, dessert |
| **FC Road student hangouts** | 18 | 1.6 | cafe, dessert, bar |
| **Baner upscale dining** | 21 | 2.3 | italian, pizza, veg_only |
| **Viman Nagar malls & cafes** | 19 | 1.7 | cafe, asian, bakery |
| **Camp trendy classics** | 8 | 2.4 | italian, asian, bar |
| **MG Road classics** | 7 | 2.6 | north_indian, south_indian |
| **Kothrud family spots** | 16 | 1.9 | asian, south_indian, family |
| **Katraj student budget** | 14 | 1.2 | street_food, south_indian |
| **Hinjawadi working professionals** | 12 | 1.8 | asian, cafe, quick_service |

### Sample Restaurant Records

```csv
p_0001,Pizza Grill & Co,Koregaon Park,KP date-night & Italian,18.542715,73.896372,"dessert,pizza,veg_only,vegan",2,4.81,50,"cozy,date",1,"['dessert', 'pizza', 'veg_only', 'vegan']"
p_0055,Italian Bistro Spot,Viman Nagar,Viman Nagar malls & cafes,18.569395,73.916955,italian,1,4.97,50,"live_music,date",0,['italian']
p_0079,Bar Trattoria Hub,Baner,Baner upscale dining,18.562575,73.779382,bar,1,4.38,50,"quiet,cozy,outdoor",0,['bar']
```

---

## 3. Interactions.csv - User-Restaurant Interactions

### File Statistics
- **Total Records**: 5,106 interactions (5,107 lines including header)
- **File Size**: ~250KB
- **Encoding**: UTF-8
- **Format**: Comma-separated values

### Schema Description

| Column | Data Type | Description | Example Values | Constraints |
|--------|-----------|-------------|---------------|-------------|
| `interaction_id` | String | Unique interaction identifier | i_000001, i_000025, i_005106 | Format: i_NNNNNN |
| `user_id` | String | User who performed interaction | u_0001, u_0045, u_0228 | Foreign key to users.csv |
| `place_id` | String | Restaurant interacted with | p_0013, p_0061, p_0139 | Foreign key to places.csv |
| `type` | String | Type of interaction | view, click, save, checkin | 4 interaction types |
| `rating` | Float | User rating (if applicable) | 3.1, 4.6, 5.0 | Range: 1.0-5.0, nullable |
| `dwell_sec` | Integer | Time spent viewing (seconds) | 169, 242, 350 | Range: 20-400, nullable |
| `timestamp` | String | When interaction occurred | 2025-08-13T18:51:43 | ISO datetime format |

### Interaction Types Distribution

| Type | Count | % of Total | Has Rating | Has Dwell Time | Description |
|------|-------|------------|------------|----------------|-------------|
| **view** | 3,821 | 74.8% | No | Yes | User viewed restaurant details |
| **click** | 856 | 16.8% | Sometimes | Yes | User clicked for more info |
| **save** | 285 | 5.6% | Sometimes | No | User saved to favorites |
| **checkin** | 144 | 2.8% | No | No | User checked in at location |

### Temporal Distribution

**Time Period**: July 2025 - November 2025 (5 months)  
**Peak Activity**: September-October 2025  
**Daily Pattern**: Distributed across all hours  
**Seasonal Trends**: Consistent activity levels  

### Rating Distribution (for rated interactions)

| Rating Range | Count | Percentage | Avg Dwell Time |
|--------------|-------|------------|----------------|
| **4.5-5.0** | 245 | 43.2% | 275 seconds |
| **4.0-4.4** | 198 | 34.9% | 250 seconds |
| **3.5-3.9** | 89 | 15.7% | 225 seconds |
| **3.0-3.4** | 28 | 4.9% | 200 seconds |
| **1.0-2.9** | 7 | 1.2% | 175 seconds |

### User Engagement Patterns

| Metric | Average | Range | Notes |
|--------|---------|-------|-------|
| **Interactions per User** | 22.4 | 15-35 | Well-distributed activity |
| **Restaurants per User** | 18.7 | 12-28 | Good exploration breadth |
| **Dwell Time (views)** | 243 sec | 20-400 sec | Realistic engagement |
| **Rating Frequency** | 24.8% | - | Users rate ~1 in 4 interactions |

### Sample Interaction Records

```csv
i_000001,u_0001,p_0013,view,,169,2025-08-13T18:51:43
i_000007,u_0001,p_0004,click,4.6,286,2025-10-06T12:48:43
i_000013,u_0001,p_0011,save,3.1,,2025-08-25T01:19:43
i_000006,u_0001,p_0044,checkin,,,2025-10-24T07:58:43
```

---

## Data Relationships & Integrity

### Foreign Key Relationships
- `interactions.user_id` → `users.user_id` (Many-to-One)
- `interactions.place_id` → `places.place_id` (Many-to-One)
- **Referential Integrity**: 100% maintained (no orphaned records)

### Data Quality Metrics
- **Completeness**: 100% (no missing required values)
- **Consistency**: High (standardized formats and ranges)
- **Validity**: All values within expected ranges and formats
- **Uniqueness**: All IDs are unique within their respective files

### Cross-File Statistics
- **User Coverage**: All 228 users have interaction history
- **Restaurant Coverage**: 139 restaurants all have at least 20 interactions
- **Geographic Spread**: All 8 neighborhoods represented proportionally
- **Temporal Spread**: 5-month period with realistic patterns

---

## Usage Notes for Recommendation Algorithms

### Clustering Features
- **User Segments**: 8 distinct behavioral clusters for collaborative filtering
- **Restaurant Clusters**: 8 semantic location-cuisine clusters for content-based filtering
- **Interaction Patterns**: Diverse engagement types for implicit feedback analysis

### Machine Learning Applications
- **Collaborative Filtering**: Rich user-item interaction matrix (228×139)
- **Content-Based Filtering**: Multi-dimensional restaurant feature vectors
- **Hybrid Systems**: Combined user preferences + restaurant attributes
- **Temporal Analysis**: Time-based recommendation patterns
- **Cold Start**: New user/restaurant scenarios covered

### Data Preprocessing Notes
- **Categories**: Split comma-separated values for multi-label processing
- **Coordinates**: Normalize for distance calculations
- **Ratings**: Handle missing values appropriately (nullable fields)
- **Timestamps**: Convert to datetime objects for temporal analysis
- **Text Fields**: Consider case normalization for matching

---

**Dataset Generated**: November 2025  
**Format Version**: 1.0  
**Quality Assurance**: Validated against real-world Pune restaurant patterns  
**Recommended Use**: Algorithm development, testing, and benchmarking  
