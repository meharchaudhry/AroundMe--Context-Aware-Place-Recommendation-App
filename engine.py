"""Wrapper RecommendationEngine for the main app.

This module delegates to the adapter `recommend_for_user` implemented
in `recommendations.logic`, which itself uses the friend's
`IntegratedAroundMeSystem` implementation so that the exact same
algorithmic logic (the `aroundme` implementation) is used.

The purpose of this lightweight wrapper is to provide a drop-in
replacement API (`RecommendationEngine.recommend(...)`) for callers
that previously used a local Django-only implementation.
"""

from typing import Any, List

from .logic import recommend_for_user


class RecommendationEngine:
    """Light wrapper that delegates to `recommend_for_user`.

    This preserves the same public method signature expected by the
    rest of the Django app while ensuring the core logic comes from
    `aroundme/integrated_aroundme_system.py` (no changes to that file).
    """

    def __init__(self, user: Any):
        self.user = user

    def recommend(self, algorithm: str = "time", limit: int = 10, user_location: tuple = None) -> List[dict]:
        """Return recommendations for `self.user`.

        Args:
            algorithm: one of 'time','history','cluster','hybrid','explore','popular'
            limit: number of results to return
            user_location: optional (lat, lng) tuple for distance-aware results
        """
        return recommend_for_user(self.user, algorithm=algorithm, limit=limit, user_location=user_location)

    # Backwards-compatible aliases (optional)
    def time_based(self, limit: int = 10):
        return self.recommend(algorithm="time", limit=limit)

    def history_based(self, limit: int = 10):
        return self.recommend(algorithm="history", limit=limit)

    def cluster_based(self, limit: int = 10):
        return self.recommend(algorithm="cluster", limit=limit)

    def hybrid(self, limit: int = 10):
        return self.recommend(algorithm="hybrid", limit=limit)

    def explore_mode(self, limit: int = 10):
        return self.recommend(algorithm="explore", limit=limit)

    def popular(self, limit: int = 10):
        return self.recommend(algorithm="popular", limit=limit)
