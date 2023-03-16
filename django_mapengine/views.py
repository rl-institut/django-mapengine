from typing import List

from django.conf import settings
from django.views.generic.base import ContextMixin

from . import layers, sources


class MapEngineMixin(ContextMixin):
    def get_mapengine_context(self, map_sources: List[sources.MapSource], map_layers: List[layers.MapLayer]) -> dict:
        context = {
            "mapengine_setup": settings.MAP_ENGINE_SETUP,
            "mapengine_zoom_levels": settings.MAP_ENGINE_ZOOM_LEVELS,
            # Sources need valid URL (containing host and port), thus they have to be defined using request:
            "mapengine_sources": {source.name: source.get_source(self.request) for source in map_sources},
            "mapengine_layers": [layer.get_layer() for layer in map_layers],
            "mapengine_layers_at_startup": settings.MAP_ENGINE_LAYERS_AT_STARTUP,
            "mapengine_images": [image.as_dict() for image in settings.MAP_ENGINE_IMAGES],
            "mapengine_popups": settings.MAP_ENGINE_POPUPS,
        }
        store = {
            "popup_layers": settings.MAP_ENGINE_POPUPS,
            "region_layers": settings.MAP_ENGINE_REGIONS,
            "result_views": {},  # Placeholder for already downloaded results (used in results.js)
            "zoom_levels": settings.MAP_ENGINE_ZOOM_LEVELS,
        }

        context["mapengine_store_cold_init"] = store

        return context
