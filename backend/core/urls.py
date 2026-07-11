"""Root URL configuration for the Ticket Management project."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# ---------------------------------------------------------------------------
# API URL patterns
# App-level routers are plugged in here as each app is developed.
# ---------------------------------------------------------------------------
api_patterns = [
    path("auth/", include("apps.accounts.urls")),
    # path("tickets/",       include("apps.tickets.urls")),
    # path("notifications/", include("apps.notifications.urls")),
    # path("dashboard/",     include("apps.dashboard.urls")),
]

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
    # OpenAPI schema
    path("api/docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API
    path("api/", include(api_patterns)),
]
