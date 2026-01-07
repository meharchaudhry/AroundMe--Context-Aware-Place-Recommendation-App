from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404
from django.conf import settings
from pathlib import Path

from .models import Place, Review, Badge, UserBadge, Interaction
from .serializers import (
    ProfileSerializer, PlaceSerializer, ReviewSerializer,
    BadgeSerializer, UserBadgeSerializer, UserVisitedPlacesSerializer,
    UserSignupSerializer, CustomTokenObtainPairSerializer
)

# ⬅️ import your recommendation logic (update later if file name differs)
from recommendations.logic import recommend_for_user
from aroundme_recommendation.integrated_aroundme_system import IntegratedAroundMeSystem

User = get_user_model()



# ------------------------------
# Base ViewSet (shared config)
# ------------------------------
class BaseViewSet(viewsets.ModelViewSet):
    """Applies global authentication and permission logic."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# ------------------------------
# Profile / User
# ------------------------------
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]  # users can update their own profile
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]  # only admins can delete users
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if kwargs['pk'] != str(user.id):
            return Response({"detail": "You cannot edit other users' profiles."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# ------------------------------
# Places
# ------------------------------
class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.filter(is_deleted=False)
    serializer_class = PlaceSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]



# ------------------------------
# Reviews
# ------------------------------
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return Review.objects.all()
        return Review.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        user = request.user
        review = self.get_object()
        
        if user.is_staff or getattr(user, "role", None) == "admin":
            return Response({"detail": "Admins cannot edit reviews."}, status=status.HTTP_403_FORBIDDEN)
        elif review.user != user:
            return Response({"detail": "You can only edit your own reviews."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
        serializer.save(user=self.request.user)


# ------------------------------
# Badges
# ------------------------------
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    All logged-in users can view badges.
    No creation, update, or delete allowed.
    """
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


# ------------------------------
# Badges for admins (full CRUD)
# ------------------------------
class AdminBadgeViewSet(viewsets.ModelViewSet):
    """
    Admins can create, update, or delete badges.
    """
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAdminUser]

# ------------------------------
# User Badges
# ------------------------------
from .models import UserBadge
from .serializers import UserBadgeSerializer
from rest_framework.permissions import IsAdminUser

class UserBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.select_related('user', 'badge')
    serializer_class = UserBadgeSerializer
    permission_classes = [IsAdminUser]  # only admins can view/edit


# ------------------------------
# User Signup
# ------------------------------
class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]  # anyone can sign up

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })


# ------------------------------
# User Login (JWT)
# ------------------------------
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    
    
# ------------------------------
# My Badges
# ------------------------------
class MyBadgesView(generics.ListAPIView):
    serializer_class = UserBadgeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserBadge.objects.none()
        return UserBadge.objects.filter(user=self.request.user)
# ------------------------------
# User Visited Places
# ------------------------------
class UserVisitedPlacesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interaction.objects.none()  # dummy queryset
    serializer_class = UserVisitedPlacesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Interaction.objects.none()
        user = self.request.user
        return Interaction.objects.filter(user=user)
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recommendations_view(request):
    try:
        # allow clients to pass algorithm and limit as query params
        algorithm = request.query_params.get('algorithm', 'time')
        try:
            limit = int(request.query_params.get('limit', 10))
        except ValueError:
            limit = 10

        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        user_location = None
        if lat is not None and lng is not None:
            try:
                user_location = (float(lat), float(lng))
            except ValueError:
                user_location = None

        results = recommend_for_user(request.user, algorithm=algorithm, limit=limit, user_location=user_location)
        return Response({"status": "success", "results": results}, status=200)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def route_coordinates_view(request):
    """Fetch real shuttle route coordinates from Google Maps API using friend's system.
    
    Query params:
        - route: route name (default: 'flame_to_fc_road')
    
    Returns:
        - status: 'success' or 'error'
        - coordinates: list of [lat, lng] tuples representing the route
        - waypoints: list of waypoint names
    """
    try:
        google_key = getattr(settings, 'AROUNDME_GOOGLE_API_KEY', '')
        if not google_key:
            return Response({
                "status": "error",
                "message": "Google API key not configured. Set AROUNDME_GOOGLE_API_KEY environment variable."
            }, status=400)
        
        # Initialize the integrated system to get route coordinates
        system = IntegratedAroundMeSystem(google_api_key=google_key, use_synthetic_data=False)
        
        route_name = request.query_params.get('route', 'flame_to_fc_road')
        
        # Get route coordinates from Google Maps API
        coordinates = system.get_route_coordinates(route_name)
        
        if not coordinates:
            return Response({
                "status": "error",
                "message": f"Could not fetch route '{route_name}'. Check API key and internet connection."
            }, status=400)
        
        # Get waypoint names from the route definition
        route_info = system.shuttle_routes.get(route_name, {})
        waypoints = [route_info.get('origin', '')] + route_info.get('waypoints', []) + [route_info.get('destination', '')]
        
        return Response({
            "status": "success",
            "route_name": route_name,
            "coordinates": coordinates,  # List of (lat, lng) tuples
            "waypoints": waypoints,
            "num_points": len(coordinates)
        }, status=200)
    
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)


def map_demo_view(request):
    """Serve the static Leaflet map demo HTML file so it can be opened at
    `/map/aroundme/` within the running Django server. This returns a
    FileResponse reading the demo file from the repository.
    """
    # Build path relative to the project root (backend)
    base = Path(__file__).resolve().parent.parent
    demo_path = base / 'recommendations' / 'static' / 'recommendations' / 'map_demo.html'
    if not demo_path.exists():
        raise Http404("Map demo not found")
    return FileResponse(open(demo_path, 'rb'), content_type='text/html')
