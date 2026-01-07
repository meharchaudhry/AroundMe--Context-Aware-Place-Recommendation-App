## 🍜 AroundMe Project - File Guide

### 🚀 **TO RUN THE PROGRAM:**
```bash
python enhanced_aroundme_v2.py
```
**This is your MAIN file** - Enhanced AroundMe System v2.0

---

### ✅ **KEEP THESE FILES:**

1. **`enhanced_aroundme_v2.py`** - ⭐ **MAIN PROGRAM** 
   - Complete AroundMe system with all features
   - Multi-neighborhood support
   - Advanced explore mode with filters
   - Real-time database management
   - **Run this file to start the app**

2. **`generate_expanded_data.py`** - 🔧 **DATA GENERATOR**
   - Creates synthetic restaurant data (305+ places, 12 neighborhoods)
   - Run this if you want to regenerate/expand the database
   - Already executed - data is in `aroundme_synth/`

3. **`aroundme_synth/`** - 📁 **DATABASE FOLDER**
   - `places.csv` - 305+ restaurants across Pune
   - `users.csv` - 300+ user profiles
   - `interactions.csv` - 8940+ user interactions
   - **Keep this folder - it's your data!**

---

### ❌ **DELETE THESE FILES** (Redundant/Outdated):

1. **`aroundme_recommender_demo.py`** - Old version, superseded by v2.0
2. **`custom_test.py`** - Old testing, covered by v2.0 explore mode
3. **`test_enhanced.py`** - Tests old version, not v2.0
4. **`test_explore_mode.py`** - Testing file, not needed for production
5. **`README_CLEANUP.md`** - Outdated file list
6. **`__pycache__/`** - Python cache folder (auto-generated)

---

### 🎯 **FINAL CLEAN PROJECT STRUCTURE:**
```
aroundme/
├── enhanced_aroundme_v2.py     ← RUN THIS MAIN FILE
├── generate_expanded_data.py   ← Data generator (if needed)
└── aroundme_synth/            ← Database folder
    ├── places.csv
    ├── users.csv
    └── interactions.csv
```

---

### 🔧 **HOW TO USE:**

1. **Start the system:**
   ```bash
   python enhanced_aroundme_v2.py
   ```

2. **Menu options:**
   - **Option 1:** Create your user profile (multiple neighborhoods)
   - **Option 2:** Get personalized recommendations
   - **Option 3:** Explore mode (filter by food/location/price/mood)
   - **Option 4:** Add new restaurants to database
   - **Option 5:** View database statistics

3. **Explore mode examples:**
   - Want ice cream in Balewadi? ✅
   - Asian food under ₹2? ✅  
   - Date night spots in KP & Camp? ✅
   - Family restaurants with 4+ stars? ✅

---

### 📊 **CURRENT DATABASE:**
- **305+ places** across **12 neighborhoods**
- **16+ food categories** (asian, italian, ice_cream, etc.)
- **4 price levels** (₹1-₹4)
- **300+ users** with realistic preferences
- **8940+ interactions** for social recommendations

---

**🎉 You're ready to run your complete AroundMe recommendation system!**