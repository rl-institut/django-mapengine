
from django.conf import settings
from django.urls import path
from django_distill import distill_path
from djgeojson.views import GeoJSONLayerView
from django.apps import apps

from . import views, distill, mvt, registry

app_name = "django_mapengine"

urlpatterns = [
    path(f"clusters/{name}.geojson", GeoJSONLayerView.as_view(model=model))
    for name, model in registry.cluster_registry.items()
]

urlpatterns += [
    path(f"{name}_mvt/<int:z>/<int:x>/<int:y>/", mvt.mvt_view_factory(name, layers))
    for name, layers in registry.mvt_registry.items()
]


def get_all_statics_for_state_lod(view_name: str) -> tuple[int, int, int]:
    """Return distill coordinates for given layer.

    Parameters
    ----------
    view_name: str
        Layer name

    Yields
    ------
    tuple[int, int, int]
        Holding x,y,z
    """
    for x, y, z in distill.get_coordinates_for_distilling(view_name):
        yield z, x, y


# Distill MVT-urls:
if settings.MAP_ENGINE_DISTILL:
    urlpatterns += [
        distill_path(
            f"<int:z>/<int:x>/<int:y>/{name}.mvt",
            mvt.mvt_view_factory(name, layers),
            name=name,
            distill_func=get_all_statics_for_state_lod,
            distill_status_codes=(200, 204, 400),
        )
        for name, layers in registry.mvt_registry.items()
    ]