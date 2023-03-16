from django.views.generic.base import ContextMixin


class MapEngineMixin(ContextMixin):
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context["mapengine_setup"] = settings.MAP_ENGINE_SETUP
        context["mapengine_zoom_levels"] = settings.MAP_ENGINE_ZOOM_LEVELS

        # Sources need valid URL (containing host and port), thus they have to be defined using request:
        context["mapengine_sources"] = {
            map_source.name: map_source.get_source(self.request) for map_source in map_config.SOURCES
        }

        context["mapengine_layers"] = [layer.get_layer() for layer in map_config.ALL_LAYERS]
        context["mapengine_layers_at_startup"] = map_config.LAYERS_AT_STARTUP

        context["mapengine_images"] = [image.as_dict() for image in settings.MAP_ENGINE_IMAGES]

        context["mapengine_popups"] = map_config.POPUPS

        store = {
            "popup_layers": map_config.POPUPS,
            "region_layers": [
                layer.id for layer in map_config.REGION_LAYERS if layer.id.startswith("fill")
            ],
            "result_views": {},  # Placeholder for already downloaded results (used in results.js)
            "zoom_levels": map_settings.ZOOM_LEVELS,
            "region_filter_layers": REGION_FILTER_LAYERS,
        }

        context["mapengine_store_cold_init"] = store

        return context