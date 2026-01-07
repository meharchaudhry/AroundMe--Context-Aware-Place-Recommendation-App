"""
Simple import test to verify the recommendation system integration works.

This test verifies that:
1. The recommendations package can import successfully
2. The logic.py adapter can find integrated_aroundme_system.py
3. The RecommendationEngine wrapper is properly set up

Run from anywhere:
    python simple_import_test.py
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, backend_path)

print("=" * 70)
print("TESTING RECOMMENDATION SYSTEM INTEGRATION - IMPORT TEST")
print("=" * 70)

print("\n1. Testing IntegratedAroundMeSystem import...")
try:
    from aroundme_recommendation.integrated_aroundme_system import IntegratedAroundMeSystem
    print("   ✅ IntegratedAroundMeSystem imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import IntegratedAroundMeSystem: {e}")
    sys.exit(1)

print("\n2. Testing recommendations.engine import...")
try:
    from recommendations.engine import RecommendationEngine
    print("   ✅ RecommendationEngine imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import RecommendationEngine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Testing recommendations.logic import...")
try:
    from recommendations.logic import recommend_for_user, ALGO_MAP
    print("   ✅ recommend_for_user imported successfully")
    print(f"   ✅ Algorithm mappings: {list(ALGO_MAP.keys())}")
except Exception as e:
    print(f"   ❌ Failed to import logic module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Verifying IntegratedAroundMeSystem can be instantiated...")
try:
    # Create instance with dummy API key
    system = IntegratedAroundMeSystem(
        google_api_key="test_key",
        use_synthetic_data=False  # Won't actually load data without Django
    )
    print("   ✅ IntegratedAroundMeSystem instantiated successfully")
    
    # Check that methods exist
    methods = [
        '_get_time_based_recommendations_internal',
        '_get_history_based_recommendations_internal',
        '_get_cluster_recommendations_internal',
        '_get_hybrid_recommendations_internal',
        '_get_explore_recommendations_internal',
    ]
    
    for method in methods:
        if hasattr(system, method):
            print(f"   ✅ Method exists: {method}")
        else:
            print(f"   ❌ Method missing: {method}")
            sys.exit(1)
            
except Exception as e:
    print(f"   ❌ Failed to instantiate system: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL IMPORT TESTS PASSED!")
print("=" * 70)
print("\nThe recommendation system integration is correctly set up:")
print("  • aroundme/integrated_aroundme_system.py → available")
print("  • recommendations/logic.py → adapter works")
print("  • recommendations/engine.py → wrapper works")
print("\nThe system is ready to use with Django once database is configured.")
print("=" * 70)
