"""Root URLconf for tests, mirroring how a host project includes django_mapengine."""

from django.urls import include, path

urlpatterns = [
    path("map/", include("django_mapengine.urls")),
]
