"""Views and mixins in order to use mapengine"""

import itertools

from django.conf import settings
from django.http import JsonResponse
from django.views.generic.base import ContextMixin

from . import __version__, layers, sources


def index():
    """
    Placeholder to get app url from `urls.reverse()` function by calling `reverse("django_mapengine:index")`.

    Returns
    -------
    JsonResponse
        containing app name and current version
    """
    return JsonResponse({"app": "django_mapengine", "version": __version__})


# pylint:disable=R0903
class MapEngineMixin(ContextMixin):
    """This mixin defines map setup for maplibre"""

    def get_context_data(self, **kwargs) -> dict:
        """
        Overloads context with map specific data

        Parameters
        ----------
        kwargs : dict
            Optional kwargs from view

        Returns
        -------
        dict
            Holding context data from mapengine setup
        """
        context = super().get_context_data(**kwargs)
        context.update(
            **{
                "mapengine_setup": settings.MAP_ENGINE_SETUP,
                # Sources need valid URL (containing host and port), thus they have to be defined using request:
                "mapengine_sources": {
                    source.name: source.get_source(self.request) for source in sources.get_all_sources()
                },
                "mapengine_basemap_layers": [basemap.as_dict() for basemap in settings.MAP_ENGINE_BASEMAPS],
                "mapengine_layers": [layer.get_layer() for layer in layers.get_all_layers()],
                "mapengine_layers_at_startup": list(
                    itertools.chain.from_iterable(
                        [layer, f"{layer}_distilled"] for layer in settings.MAP_ENGINE_LAYERS_AT_STARTUP
                    )
                ),
                "mapengine_images": [image.as_dict() for image in settings.MAP_ENGINE_IMAGES],
            }
        )
        store = {
            "debugMode": settings.MAP_ENGINE_DEBUG,
            "popups": {popup.layer_id: popup.as_dict() for popup in settings.MAP_ENGINE_POPUPS},
            "hover_layers": list(
                itertools.chain.from_iterable(
                    [layer, f"{layer}_distilled"] for layer in settings.MAP_ENGINE_HOVER_LAYERS
                )
            ),
            "result_views": {},  # Placeholder for already downloaded results (used in results.js)
            "cluster_layers": [cluster.layer_id for cluster in settings.MAP_ENGINE_API_CLUSTERS],
            "choropleths": {choropleth.name: choropleth.as_dict() for choropleth in settings.MAP_ENGINE_CHOROPLETHS},
            "layer_switch_class": settings.MAP_ENGINE_LAYER_SWITCH_CLASS,
            "basemap": "default",
        }

        context["mapengine_store_cold_init"] = store

        return context
