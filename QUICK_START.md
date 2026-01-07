# 🚀 AroundMe Quick Start Guide

## **30-Second Setup**

```bash
# 1. Install dependencies
pip install pandas numpy requests geopy folium

# 2. Test the system
python test_integrated_system.py

# 3. Launch interactive mode
python launch_aroundme.py
```

## **Immediate Usage Options**

### 🧪 **Development Mode** (No API Key Needed)
Perfect for testing and demonstrations
- Uses synthetic dataset (139 restaurants, 228 users, 5,106 interactions)
- All 6 AI algorithms work instantly
- Zero costs, works offline

### 🌍 **Production Mode** (Requires Google API Key)
Real restaurant data along shuttle routes
- Get API key: [Google Cloud Console](https://console.cloud.google.com/)
- Enable: Places API + Directions API
- Update key in `launch_aroundme.py`

## **Algorithm Quick Reference**

| Algorithm | Best For | Example Use |
|-----------|----------|-------------|
| ⏰ **Time-Based** | "What to eat right now?" | Lunch places at 1 PM |
| 📚 **History-Based** | "Based on my past likes" | More Italian if you love Italian |
| 👥 **Social** | "People like me enjoy..." | Users with similar taste |
| 🏢 **Cluster-Based** | "Similar restaurant vibes" | Same neighborhood + cuisine |
| 🤝 **Hybrid** | "Best of all algorithms" | Combined intelligence |
| 🎯 **Explore** | "Help me try something new!" | Safe adventures |

## **Example Session**

```python
# Quick programmatic usage
from integrated_aroundme_system import IntegratedAroundMeSystem

system = IntegratedAroundMeSystem(use_synthetic_data=True)  # Dev mode
system.initialize_synthetic_mode()

# Get recommendations
recommendations = system.get_recommendations(
    user_id="user_001", 
    algorithm="hybrid", 
    limit=5
)
```

## **File Priority**

**Start with these files:**
1. `launch_aroundme.py` - Interactive interface
2. `test_integrated_system.py` - Verify everything works
3. `integrated_aroundme_system.py` - Main system (for coding)
4. `config_template.py` - Customization

**Documentation:**
- `README_INTEGRATED_SYSTEM.md` - Complete guide (this file's big brother)
- `AroundMe_Algorithm_Flows.md` - How algorithms work

**You're ready to go! 🎉**