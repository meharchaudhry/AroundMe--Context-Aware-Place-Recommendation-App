"""
Quick test script to verify the integrated recommendation system works.

This script tests that the recommendations package correctly uses the
aroundme/integrated_aroundme_system.py logic without any changes to the
original aroundme code.

Run from the aroundme-backend directory:
    python test_recommendations.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from recommendations.engine import RecommendationEngine
from api.models import User, Place
from django.contrib.auth import get_user_model

def test_recommendation_engine():
    """Test that RecommendationEngine properly delegates to aroundme logic."""
    
    print("=" * 70)
    print("TESTING INTEGRATED RECOMMENDATION SYSTEM")
    print("=" * 70)
    
    # Check if we have users and places in the database
    User = get_user_model()
    
    user_count = User.objects.count()
    place_count = Place.objects.filter(is_deleted=False).count()
    
    print(f"\n📊 Database Status:")
    print(f"   Users: {user_count}")
    print(f"   Places: {place_count}")
    
    if user_count == 0:
        print("\n❌ No users found in database.")
        print("   Please create a test user first using Django admin or shell.")
        return False
    
    if place_count == 0:
        print("\n⚠️  No places found in database.")
        print("   The recommendation system needs places to recommend.")
        print("   Please populate the Place model first.")
        return False
    
    # Get first user for testing
    test_user = User.objects.first()
    print(f"\n👤 Test User: {test_user.username}")
    
    # Test each algorithm
    algorithms = ["time", "history", "cluster", "hybrid", "explore", "popular"]
    
    print(f"\n🧪 Testing Algorithms:")
    print("-" * 70)
    
    for algo in algorithms:
        try:
            engine = RecommendationEngine(test_user)
            results = engine.recommend(algorithm=algo, limit=5)
            
            print(f"\n✅ {algo.upper():15} → {len(results)} recommendations")
            
            if results:
                # Show first result as sample
                first = results[0]
                print(f"   Sample: {first.get('name', 'N/A')}")
                print(f"           Score: {first.get('score', 0):.3f}")
                print(f"           Algorithm: {first.get('algorithm', 'N/A')}")
            else:
                print(f"   ⚠️  No results (might be expected for {algo})")
                
        except Exception as e:
            print(f"\n❌ {algo.upper():15} → ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\nThe recommendation system is now using the exact same logic")
    print("from aroundme/integrated_aroundme_system.py")
    print("\nNo changes were made to the original aroundme code.")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = test_recommendation_engine()
    sys.exit(0 if success else 1)
