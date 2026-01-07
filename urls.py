from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    PlaceViewSet,
    ReviewViewSet,
    BadgeViewSet,
    UserBadgeViewSet,
    SignupView,
    LoginView,
    UserVisitedPlacesViewSet,
    MyBadgesView,
    AdminBadgeViewSet,
    recommendations_view,
    map_demo_view,
    route_coordinates_view,
)

# -----------------------------
# Router for all ViewSets
# -----------------------------
router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'places', PlaceViewSet)       # <-- this handles listing/creating places
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'badges', BadgeViewSet)
router.register(r'admin/badges', AdminBadgeViewSet, basename='admin-badge')
router.register(r'userbadges', UserBadgeViewSet)
router.register(r'visited-places', UserVisitedPlacesViewSet, basename='visitedplaces')
router.register(r"user/visited", UserVisitedPlacesViewSet, basename="visited")



# -----------------------------
# URL patterns
# -----------------------------
urlpatterns = [
    path('', include(router.urls)),             # all viewset routes
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('my-badges/', MyBadgesView.as_view(), name='my-badges'),
    path("recommendations/", recommendations_view),
    path("route/coordinates/", route_coordinates_view, name='route-coordinates'),
    path("map/aroundme/", map_demo_view, name='map-demo'),
] + router.urls


