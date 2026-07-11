"""Root URL configuration for the Ticket Management project."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# ---------------------------------------------------------------------------
# API v1 URL patterns
# App-level routers are plugged in here as each app is developed.
# ---------------------------------------------------------------------------
api_v1_patterns = [
    # path("auth/",          include("apps.accounts.urls")),
    # path("tickets/",       include("apps.tickets.urls")),
    # path("notifications/", include("apps.notifications.urls")),
    # path("dashboard/",     include("apps.dashboard.urls")),
]

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # OpenAPI schema + interactive docs
    path("api/schema/",            SpectacularAPIView.as_view(),                       name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/",      SpectacularRedocView.as_view(url_name="schema"),    name="redoc"),

    # Versioned API
    path("api/v1/", include(api_v1_patterns)),
]
