from django.contrib.gis.db import models  # note: from gis.db instead of db
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

PLACE_TYPE_CHOICES = [
    ('restaurant', 'Restaurant'),
    ('cafe', 'Cafe'),
    ('hospital', 'Hospital'),
    ('store', 'Store'),
    ('washroom', 'Washroom'),
    ('mall', 'Mall'),
    ('other', 'Other'),
]

# ---------------------------------------------------------------------
# Base Model
# ---------------------------------------------------------------------
class BaseModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_updated"
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="%(class)s_deleted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------
class Profile(AbstractUser, BaseModel):
    role = models.CharField(max_length=10, default='user')
    points = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Recommendation attributes
    segment = models.CharField(max_length=100, blank=True, null=True)
    home_neighborhood = models.CharField(max_length=100, blank=True, null=True)
    preferred_categories = models.JSONField(blank=True, null=True)
    price_preference = models.PositiveSmallIntegerField(blank=True, null=True)
    distance_tolerance_km = models.FloatField(blank=True, null=True)
    ambience_preferences = models.JSONField(blank=True, null=True)
    explore_rate = models.FloatField(blank=True, null=True)
    age_group = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


# ---------------------------------------------------------------------
# Place Model (PostGIS-enabled)
# ---------------------------------------------------------------------
class Place(BaseModel):
    place_id = models.CharField(max_length=100, unique=True, db_index=True)  # from Google
    name = models.CharField(max_length=150, db_index=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    cluster_label = models.IntegerField(blank=True, null=True, db_index=True)
    categories = models.CharField(max_length=50, choices=PLACE_TYPE_CHOICES, default='other', db_index=True)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    location = models.PointField(geography=True, null=True, blank=True, srid=4326)  # PostGIS field

    rating = models.FloatField(default=0)
    user_rating_count = models.PositiveIntegerField(default=0)
    price_level = models.PositiveSmallIntegerField(blank=True, null=True)
    open_now = models.BooleanField(default=False)

    cuisine_type = models.CharField(max_length=100, blank=True, null=True)
    ambience = models.CharField(max_length=100, blank=True, null=True)
    veg_only = models.BooleanField(default=False)
    cat_list = models.JSONField(blank=True, null=True)

    distance_from_route = models.FloatField(blank=True, null=True)
    stop_nearby = models.CharField(max_length=100, blank=True, null=True)

    photo_reference = models.CharField(max_length=200, blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)

    reviews_text = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["cluster_label"], name="idx_place_cluster"),
            models.Index(fields=["name"], name="idx_place_name"),
            models.Index(fields=["neighborhood"], name="idx_place_neighborhood"),
            models.Index(fields=["latitude", "longitude"], name="idx_place_latlong"),
        ]

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------
# Review Model
# ---------------------------------------------------------------------
class Review(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, db_index=True)
    author_name = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=20, default="user")  # 'google' or 'user'
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    dwell_time_sec = models.PositiveIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ("user", "place")
        indexes = [
            models.Index(fields=["place"], name="idx_review_place"),
            models.Index(fields=["rating"], name="idx_review_rating"),
        ]

    def __str__(self):
        return f"{self.place.name} ({self.rating}★)"


# ---------------------------------------------------------------------
# Interaction Model
# ---------------------------------------------------------------------
class Interaction(BaseModel):
    TYPE_CHOICES = [
        ("visited", "Visited"),
        ("liked", "Liked"),
        ("reviewed", "Reviewed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    rating = models.FloatField(blank=True, null=True)
    dwell_time_sec = models.PositiveIntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "type"], name="idx_interaction_user_type"),
            models.Index(fields=["timestamp"], name="idx_interaction_time"),
        ]

    def __str__(self):
        return f"{self.user.username} {self.type} {self.place.name}"


# ---------------------------------------------------------------------
# Badges & Gamification
# ---------------------------------------------------------------------
class Badge(BaseModel):
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    points_required = models.PositiveIntegerField(default=0)
    icon_url = models.URLField(blank=True)

    def __str__(self):
        return self.title


class UserBadge(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, db_index=True)
    awarded_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = ("user", "badge")
        indexes = [
            models.Index(fields=["user", "active"], name="idx_userbadge_active"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.badge.title}"
