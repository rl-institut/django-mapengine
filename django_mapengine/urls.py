"""URLs for MVTs and cluster geojsons"""

from django.conf import settings
from django.urls import path

from djgeojson.views import GeoJSONLayerView

from . import distill, mvt, views

app_name = "django_mapengine"  # noqa: C0103

urlpatterns = [
    path("", views.index, name="index"),
]

urlpatterns += [
    path(
        f"clusters/{cluster.layer_id}.geojson",
        GeoJSONLayerView.as_view(model=cluster.model, properties=cluster.properties),
        name=f"{cluster.layer_id}_cluster",
    )
    for cluster in settings.MAP_ENGINE_API_CLUSTERS
]

managers = []
for source, mvt_apis in settings.MAP_ENGINE_API_MVTS.items():
    source_layers = []
    for mvt_api in mvt_apis:
        manager_reference = f"{mvt_api.model_name}.{mvt_api.manager_name}"
        if manager_reference in managers:
            # Add model managers only once and use source layer in multiple layers
            continue
        managers.append(manager_reference)
        source_layers.append(mvt.MVTSourceLayer(mvt_api.layer_id, queryset=mvt_api.manager))
    urlpatterns.append(
        path(
            f"{source}_mvt/<int:z>/<int:x>/<int:y>/",
            mvt.mvt_view_factory(source, source_layers),
        )
    )

# Distill MVT-urls:
if settings.MAP_ENGINE_DISTILL:
    try:
        from django_distill import distill_path
    except ImportError as ie:
        raise ImportError(
            "You set env variable 'MAP_ENGINE_DISTILL', but django-distill package cannot be found."
        ) from ie
    urlpatterns += [
        distill_path(
            f"<int:z>/<int:x>/<int:y>/{name}.mvt",
            mvt.mvt_view_factory(
                name, [mvt.MVTSourceLayer(mvt_api.layer_id, queryset=mvt_api.manager) for mvt_api in mvt_apis]
            ),
            name=name,
            distill_func=distill.get_all_statics_for_state_lod,
            distill_status_codes=(200, 204, 400),
        )
        for name, mvt_apis in settings.MAP_ENGINE_API_MVTS.items()
    ]
