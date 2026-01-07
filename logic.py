"""Adapter that uses the friend's IntegratedAroundMeSystem.

This adapter converts Django `Place` and `Interaction` models to pandas
DataFrames expected by the friend's implementation and returns serialized
`Place` dicts (using `PlaceSerializer`) augmented with engine metadata.
"""

from django.conf import settings
from aroundme_recommendation.integrated_aroundme_system import IntegratedAroundMeSystem
import pandas as pd

from api.models import Place, Interaction
from api.serializers import PlaceSerializer


ALGO_MAP = {
    "time": "time_based",
    "history": "history_based",
    "cluster": "cluster_based",
    "hybrid": "hybrid",
    "explore": "explore_mode",
    "popular": "popular"
}


def _places_queryset_to_df(qs):
    rows = []
    for p in qs:
        types = []
        if p.cat_list:
            try:
                # cat_list may be stored as list or JSON
                if isinstance(p.cat_list, (list, tuple)):
                    types = p.cat_list
                else:
                    # attempt to parse if it's a string representation
                    types = list(p.cat_list) if isinstance(p.cat_list, str) else [p.categories]
            except Exception:
                types = [p.categories]
        else:
            types = [p.categories] if p.categories else []

        rows.append({
            "place_id": p.place_id,
            "name": p.name,
            "neighborhood": p.neighborhood or "",
            "cluster_label": p.cluster_label or "",
            "categories": p.categories or "",
            "types": ",".join(types) if types else "",
            "lat": float(p.latitude) if p.latitude is not None else 0.0,
            "lng": float(p.longitude) if p.longitude is not None else 0.0,
            "rating": float(p.rating or 0.0),
            "price_level": int(p.price_level) if p.price_level is not None else 2,
            "user_rating_count": int(p.user_rating_count or 0),
            "ambience": p.ambience or "",
            "veg_only": int(bool(p.veg_only)),
            "cat_list": str(p.cat_list) if p.cat_list is not None else "",
            "open_now": bool(p.open_now),
        })
    return pd.DataFrame(rows)


def _interactions_to_df(qs):
    rows = []
    for i in qs:
        rows.append({
            "interaction_id": str(i.id),
            "user_id": str(i.user.id) if i.user else None,  # Convert to string for consistent filtering
            "place_id": i.place.place_id if i.place else None,
            "type": i.type,
            "rating": i.rating,
            "dwell_sec": i.dwell_time_sec,
            "timestamp": i.timestamp,
        })
    return pd.DataFrame(rows)


def recommend_for_user(user, algorithm="time", limit=10, user_location=None):
    # Build system and populate DataFrames from DB
    # If a Google API key is set in Django settings, pass it to the
    # integrated system so route-aware features can be used. Otherwise
    # we'll avoid calling route-aware methods and use non-route fallbacks.
    google_key = getattr(settings, 'AROUNDME_GOOGLE_API_KEY', '')
    sys = IntegratedAroundMeSystem(google_api_key=google_key or "", use_synthetic_data=False)

    places_qs = Place.objects.filter(is_deleted=False)
    sys.places = _places_queryset_to_df(places_qs)

    interactions_qs = Interaction.objects.select_related('user', 'place').all()
    sys.interactions = _interactions_to_df(interactions_qs)

    # users DataFrame is optional for most algorithms; construct minimal version
    try:
        users_rows = []
        from django.contrib.auth import get_user_model
        User = get_user_model()
        for u in User.objects.all():
            users_rows.append({
                "user_id": u.id,
                "segment": getattr(u, 'segment', ''),
                "home_neighborhood": getattr(u, 'home_neighborhood', ''),
                "pref_categories": ','.join(u.preferred_categories) if getattr(u, 'preferred_categories', None) else getattr(u, 'preferred_categories', '') or '',
                "price_preference": getattr(u, 'price_preference', 2),
                "distance_tolerance_km": getattr(u, 'distance_tolerance_km', 5.0),
                "ambience_prefs": ','.join(u.ambience_preferences) if getattr(u, 'ambience_preferences', None) else getattr(u, 'ambience_preferences', '') or '',
                "explore_rate": getattr(u, 'explore_rate', 0.3),
            })
        sys.users = pd.DataFrame(users_rows)
    except Exception:
        sys.users = pd.DataFrame()

    # Build the user_data dict expected by the friend's algorithms
    user_data = {
        'user_id': str(user.id),  # Convert to string for consistent filtering in history/explore algorithms
        'home_neighborhood': getattr(user, 'home_neighborhood', '') or '',
        'pref_categories': ','.join(user.preferred_categories) if getattr(user, 'preferred_categories', None) else getattr(user, 'preferred_categories', '') or '',
        'price_preference': getattr(user, 'price_preference', 2) or 2,
        'ambience_prefs': ','.join(user.ambience_preferences) if getattr(user, 'ambience_preferences', None) else getattr(user, 'ambience_preferences', '') or '',
        'explore_rate': getattr(user, 'explore_rate', 0.3) or 0.3,
    }

    # Map simple algorithm names to the friend's algorithm names
    algo_name = ALGO_MAP.get(algorithm, algorithm)

    # Call the friend's route-aware recommendation entrypoint if a Google key
    # is available. Otherwise call internal non-route algorithms to avoid
    # network calls and printed route errors.
    recs = []
    if google_key:
        try:
            recs = sys.get_route_aware_recommendations(user_data=user_data, algorithm=algo_name, limit=limit,
                                                       current_location_coords=user_location)
        except Exception:
            # If route-aware call fails for any reason, fall back quietly
            recs = []

    if not recs:
        # Fallback to internal implementations
        if algo_name == 'time_based':
            recs = sys._get_time_based_recommendations_internal(user_data, limit)
        elif algo_name == 'history_based':
            recs = sys._get_history_based_recommendations_internal(user_data, limit)
        elif algo_name == 'cluster_based':
            recs = sys._get_cluster_recommendations_internal(user_data, limit)
        elif algo_name == 'hybrid':
            recs = sys._get_hybrid_recommendations_internal(user_data, limit)
        elif algo_name == 'explore_mode':
            recs = sys._get_explore_recommendations_internal(user_data, limit)
        else:
            recs = sys._get_popular_recommendations_internal(user_data, limit)

    # Serialize results using PlaceSerializer where possible and attach metadata
    results = []
    for r in recs:
        pid = r.get('place_id')
        place = Place.objects.filter(place_id=pid).first()
        if place:
            ser = PlaceSerializer(place).data
        else:
            ser = {
                'place_id': r.get('place_id'),
                'name': r.get('name'),
                'neighborhood': r.get('neighborhood'),
                'categories': r.get('categories'),
                'rating': r.get('rating'),
                'price_level': r.get('price_level'),
                'lat': r.get('lat'),
                'lng': r.get('lng'),
            }

        ser['score'] = r.get('score') or r.get('final_score') or 0
        ser['algorithm'] = r.get('algorithm') or algo_name
        # preserve any extra metadata the algorithm provided
        for extra in ('distance_from_current', 'route_convenience', 'novelty_score', 'reasoning'):
            if extra in r:
                ser[extra] = r[extra]

        results.append(ser)

    return results
