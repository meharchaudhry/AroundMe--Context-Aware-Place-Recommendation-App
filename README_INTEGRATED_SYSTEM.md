# 🍽️ AroundMe Integrated Recommendation System

## 🚀 **Overview**

The **AroundMe Integrated System** combines sophisticated AI recommendation algorithms with real-world restaurant data from Google Places API. This system bridges the gap between development (synthetic data) and production (real Google Places data) while maintaining the same intelligent recommendation capabilities.

## ✨ **Key Features**

### 🧠 **AI Recommendation Algorithms**
- **Time-Based Recommendations**: Context-aware suggestions based on current time
- **History-Based Learning**: Learns from user's past dining experiences
- **Social Collaborative Filtering**: Finds users with similar multi-dimensional tastes
- **Cluster-Based Intelligence**: Groups restaurants by semantic similarities
- **Hybrid Social+Cluster**: Combines social signals with cluster analysis
- **Explore Mode**: Adventure recommendations for trying new experiences

### 🌍 **Data Sources**
- **Development Mode**: Uses synthetic dataset (139 restaurants, 228 users, 5,106 interactions)
- **Production Mode**: Fetches real restaurant data via Google Places API along shuttle routes
- **Seamless Transition**: Same algorithms work with both synthetic and real data

### 📍 **Route-Aware Intelligence**
- **Shuttle Route Integration**: Recommendations prioritize restaurants along your commute route
- **GPS Proximity Scoring**: Considers walking distance from shuttle stops
- **Multiple Route Support**: Pre-configured routes (FLAME to FC Road, Camp, etc.)

---

## 📁 **File Structure**

```
aroundme/
├── integrated_aroundme_system.py    # Main integrated system class
├── launch_aroundme.py              # Interactive user interface
├── config_template.py              # Configuration template
├── test_integrated_system.py       # System testing
├── aroundme_main.py                # Original AI system (synthetic only)
├── places_api_(with_more_features).py  # Original Google Places integration
├── aroundme_synth/                 # Synthetic dataset
│   ├── places.csv                  # Restaurant data
│   ├── users.csv                   # User profiles
│   └── interactions.csv            # User-restaurant interactions
└── Documentation files...
```

---

## 🔧 **Setup Instructions**

### 1. **Install Dependencies**
```bash
pip install pandas numpy requests geopy folium
```

### 2. **Configure Google Places API** (For Production Mode)
1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable these APIs:
   - Places API
   - Directions API
3. Update the API key in `launch_aroundme.py`:
```python
GOOGLE_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
```

### 3. **Quick Start**
```bash
# Test the system
python test_integrated_system.py

# Launch interactive interface
python launch_aroundme.py
```

---

## 🎮 **Usage Guide**

### **Interactive Mode**
Run `python launch_aroundme.py` for a guided experience:

1. **Choose Data Mode**:
   - Development Mode: Uses synthetic data (no API key needed)
   - Production Mode: Uses real Google Places data (requires API key)

2. **Select Route** (Production Mode):
   - FLAME to FC Road
   - FLAME to Camp  
   - FLAME to Hinjawadi
   - FLAME to Koregaon Park

3. **Try Different Algorithms**:
   - Time-Based (⏰): "What should I eat right now?"
   - History-Based (📚): "Based on my past preferences"
   - Social (👥): "People like me also enjoy..."
   - Cluster-Based (🏢): "Similar restaurant vibes"
   - Hybrid (🤝): "Best of all algorithms"
   - Explore (🎯): "Help me try something new!"

### **Programmatic Usage**
```python
from integrated_aroundme_system import IntegratedAroundMeSystem

# Initialize system
system = IntegratedAroundMeSystem(
    google_api_key="your_api_key",
    use_synthetic_data=False  # True for development, False for production
)

# For real data mode
system.initialize_real_data_mode("flame_to_fc_road")

# Create user profile
user_preferences = {
    'home_neighborhood': 'Koregaon Park',
    'preferred_cuisines': 'italian,pizza,cafe',
    'price_preference': 2,
    'ambience_preference': 'date,cozy',
    'explore_rate': 0.3
}
user_data = system.create_user_for_real_data(user_preferences)

# Get recommendations
recommendations = system.get_route_aware_recommendations(
    user_data=user_data,
    route_name="flame_to_fc_road",
    algorithm="hybrid",
    limit=5
)

# Display results
system.display_recommendations(recommendations, "flame_to_fc_road")
```

---

## 🧪 **Development vs Production**

### **Development Mode** (Synthetic Data)
- ✅ **No API costs**: Works offline with synthetic dataset
- ✅ **Fast testing**: Instant algorithm validation
- ✅ **Reproducible**: Same data every time
- ✅ **Rich interactions**: 5,106 user interactions for ML training
- 🎯 **Use for**: Algorithm development, testing, demonstrations

### **Production Mode** (Real Google Places Data)
- ✅ **Real restaurants**: Current, accurate restaurant information
- ✅ **GPS integration**: Actual coordinates and route optimization  
- ✅ **Live data**: Real ratings, photos, reviews from Google
- ✅ **Route awareness**: True proximity to shuttle routes
- 🎯 **Use for**: Real-world deployment, actual recommendations

---

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────┐
│          User Interface             │
│      (launch_aroundme.py)          │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│    IntegratedAroundMeSystem         │
│  (integrated_aroundme_system.py)    │
├─────────────────────────────────────┤
│  🧠 AI Recommendation Algorithms    │
│  📍 Route Integration               │
│  🔄 Data Source Abstraction         │
└─────┬───────────────────────┬───────┘
      │                       │
┌─────▼────────┐    ┌────────▼──────┐
│ Synthetic    │    │ Google Places │
│ Dataset      │    │ API           │
│ (CSV files)  │    │ (Live data)   │
└──────────────┘    └───────────────┘
```

---

## 🎯 **Algorithm Details**

### **1. Time-Based Recommendations** ⏰
**What it does**: Suggests restaurants perfect for current time and context
**Scoring**:
```
Score = Base(rating×0.3) + Time_Bonus(1.1-1.5) + Price_Match(0.4) + Category_Match(0.5) + Quality_Bonus(0.2)
```
**Example**: At 2 PM → recommends lunch places, cafes get bonus at 4 PM

### **2. History-Based Learning** 📚  
**What it does**: Learns patterns from user's past high-rated experiences
**Scoring**:
```
Score = Base(rating×0.4) + Category_Overlap(×0.3) + Neighborhood_Bonus(0.5) + Price_Alignment(0.4) + Quality_Bonus(0.3)
```
**Example**: If you love Italian in KP → suggests new Italian places in KP

### **3. Social Collaborative Filtering** 👥
**What it does**: Finds users with similar multi-dimensional tastes
**Similarity Calculation**:
```
Similarity = Cuisine_Jaccard(40%) + Price_Overlap(20%) + Location_Overlap(15%) + Context_Match(15%) + Dietary_Match(10%)
```
**Example**: Users with 70% similarity → their 4.5★ places become your recommendations

### **4. Cluster-Based Intelligence** 🏢
**What it does**: Groups restaurants by semantic patterns (location + cuisine + price + vibe)
**Clusters**:
- "KP date-night & Italian"
- "Baner upscale dining"  
- "FC Road student hangouts"
- "Viman Nagar malls & cafes"
**Example**: Love cluster A → get unvisited places from cluster A

### **5. Hybrid Social+Cluster** 🤝
**What it does**: Combines social intelligence with cluster analysis
**Process**:
1. Find similar users (taste twins)
2. Analyze what clusters they love
3. Recommend from socially-preferred clusters
**Example**: Similar users love "Baner upscale" → suggests Baner restaurants

### **6. Explore Mode** 🎯
**What it does**: Safe adventures based on your exploration comfort level
**Novelty Factors**:
- New neighborhoods (+1.0)
- New cuisines (+0.8)  
- Slight price stretch (+0.5)
- Quality assurance (min 3.5★)
**Example**: Adventure level 80% → suggests highly-rated new experiences

---

## 📊 **Data Flow**

### **Real Data Mode Process**
1. **Route Extraction**: Google Directions API → coordinate points
2. **Restaurant Discovery**: Google Places API → restaurants near route
3. **Data Conversion**: Google format → internal restaurant format
4. **AI Processing**: Apply recommendation algorithms
5. **Route Scoring**: Add proximity convenience scores
6. **Final Ranking**: Combined AI + route convenience

### **Learning Loop** (Real Mode)
1. **User Interaction**: Visit restaurant, provide rating
2. **Data Recording**: Store interaction in local database
3. **Pattern Recognition**: Update user preferences
4. **Algorithm Improvement**: Better future recommendations

---

## 🔧 **Configuration Options**

Edit `config_template.py` to customize:

### **Route Configuration**
```python
SHUTTLE_ROUTES = {
    "your_custom_route": {
        "origin": "Starting Point",
        "waypoints": ["Stop 1", "Stop 2"],
        "destination": "End Point"
    }
}
```

### **Algorithm Weights**
```python
ALGORITHM_SETTINGS = {
    "time_based": {
        "weight_base_score": 0.3,
        "weight_time_bonus": 1.5,
        # ... customize scoring weights
    }
}
```

### **API Settings**
```python
GOOGLE_PLACES_SETTINGS = {
    "search_radius": 500,  # meters
    "max_results_per_location": 20,
    "route_sampling_interval": 5
}
```

---

## 📈 **Performance & Scaling**

### **API Usage Optimization**
- **Route Sampling**: Only queries every 5th coordinate point
- **Caching**: 30-minute cache for Google Places results  
- **Deduplication**: Removes duplicate restaurants automatically
- **Rate Limiting**: Configurable API call limits

### **Algorithm Complexity**
- **Time-Based**: O(n) - Linear with restaurant count
- **History-Based**: O(n) - Linear with unvisited places
- **Social Collaborative**: O(u²) - Quadratic with user count
- **Cluster-Based**: O(n) - Linear with cluster size
- **Hybrid**: O(n log n) - Dominated by sorting

### **Memory Usage**
- **Synthetic Mode**: ~5MB (139 restaurants, full dataset)
- **Real Mode**: ~2-10MB (depends on route length and API results)

---

## 🎯 **Use Cases**

### **🎓 Academic/Research**
- **Algorithm Development**: Test new recommendation approaches
- **Comparison Studies**: Benchmark different algorithms
- **User Behavior Analysis**: Study interaction patterns
- **Machine Learning Research**: Rich dataset for training

### **🏢 Real-World Deployment**
- **Campus Shuttle Systems**: Route-aware dining recommendations
- **Tourism Apps**: Discover restaurants along travel routes  
- **Corporate Cafeterias**: Personalized food suggestions
- **Food Delivery**: Smart restaurant discovery

### **👨‍💻 Development**
- **Rapid Prototyping**: Test ideas with synthetic data
- **API Integration**: Seamless transition to real data
- **A/B Testing**: Compare algorithm performance
- **User Experience**: Interactive recommendation interface

---

## 🔮 **Future Enhancements**

### **Planned Features**
- [ ] **Machine Learning Models**: Neural collaborative filtering
- [ ] **Real-Time Learning**: Dynamic preference updates
- [ ] **Social Network Integration**: Friend recommendation influences  
- [ ] **Weather Context**: Weather-aware suggestions (indoor/outdoor)
- [ ] **Event Integration**: Festival/event-based recommendations
- [ ] **Multi-City Support**: Expandable to other cities
- [ ] **Mobile App Integration**: Native mobile interface

### **Advanced AI Features**
- [ ] **Deep Learning Embeddings**: Restaurant and user embeddings
- [ ] **Reinforcement Learning**: Learn from click-through rates
- [ ] **Natural Language Processing**: Review sentiment analysis
- [ ] **Computer Vision**: Food image recognition
- [ ] **Graph Neural Networks**: Social network recommendations

---

## 🐛 **Troubleshooting**

### **Common Issues**

**❌ "ModuleNotFoundError"**
```bash
pip install pandas numpy requests geopy folium
```

**❌ "Google Places API Error"**
- Check API key is correct
- Ensure Places API and Directions API are enabled
- Verify billing is set up (Google requires it even for free tier)

**❌ "No restaurants found"**  
- Route might be in area with limited restaurant data
- Try increasing search radius in config
- Check if route coordinates are valid

**❌ "No recommendations returned"**
- User preferences might be too restrictive
- Try "explore_mode" algorithm for broader suggestions
- Check if interaction history exists (for history-based)

### **Debug Mode**
Set `DEBUG_SETTINGS["enable_detailed_logging"] = True` for verbose output

---

## 📚 **Documentation Files**

- `AroundMe_Algorithm_Flows.md` - Detailed algorithm explanations
- `AroundMe_Scoring_Documentation.md` - Scoring formula breakdowns
- `AroundMe_Dataset_Description.md` - Synthetic dataset documentation

---

## 🤝 **Contributing**

### **Adding New Algorithms**
1. Implement algorithm in `integrated_aroundme_system.py`
2. Add to algorithm mapping in `launch_aroundme.py`
3. Update configuration in `config_template.py`
4. Add tests in `test_integrated_system.py`

### **Adding New Routes**
1. Update `SHUTTLE_ROUTES` in configuration
2. Test with Google Directions API
3. Verify restaurant discovery works along route

---

## 📄 **License**

This project is developed for academic/research purposes. Please ensure Google Places API usage complies with Google's terms of service.

---

## 🙏 **Acknowledgments**

- **Original AroundMe System**: Advanced AI recommendation algorithms
- **Google Places API Integration**: Real-world restaurant data access
- **FLAME University**: Academic project support
- **Pune Restaurant Ecosystem**: Real-world testing environment

---

**🚀 Ready to discover amazing restaurants with AI-powered recommendations!**

*For questions or support, check the troubleshooting section or review the algorithm documentation files.*