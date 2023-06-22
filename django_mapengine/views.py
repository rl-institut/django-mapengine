"""Views and mixins in order to use mapengine"""
from django.apps import apps
from django.conf import settings
from django.http import JsonResponse
from django.views.generic.base import ContextMixin

from django.core.exceptions import FieldDoesNotExist
from . import __version__, layers, sources


def index(request):
    """
    Placeholder to get app url from `urls.reverse()` function by calling `reverse("django_mapengine:index")`.

    Parameters
    ----------
    request
        Request is neglected

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
                "mapengine_zoom_levels": settings.MAP_ENGINE_ZOOM_LEVELS,
                # Sources need valid URL (containing host and port), thus they have to be defined using request:
                "mapengine_sources": {
                    source.name: source.get_source(self.request) for source in sources.get_all_sources()
                },
                "mapengine_layers": [layer.get_layer() for layer in layers.get_all_layers()],
                "mapengine_layers_at_startup": settings.MAP_ENGINE_LAYERS_AT_STARTUP + settings.MAP_ENGINE_REGIONS,
                "mapengine_images": [image.as_dict() for image in settings.MAP_ENGINE_IMAGES],
            }
        )
        store = {
            "debugMode": settings.MAP_ENGINE_DEBUG,
            "popups": {popup.layer_id: popup.as_dict() for popup in settings.MAP_ENGINE_POPUPS},
            "regions": settings.MAP_ENGINE_REGIONS,
            "result_views": {},  # Placeholder for already downloaded results (used in results.js)
            "zoom_levels": settings.MAP_ENGINE_ZOOM_LEVELS,
            "choropleths": {choropleth.name: choropleth.as_dict() for choropleth in settings.MAP_ENGINE_CHOROPLETHS},
        }

        if settings.MAP_ENGINE_MAPLAYER_MODEL:
            # get MapLayerModel from settings
            try:
                MapLayerModel = apps.get_model(app_label='map', model_name=settings.MAP_ENGINE_MAPLAYER_MODEL)
            except ImportError:
                raise LookupError("The MapLayerModel does not exist.")

            # get choropleth fields
            try:
                model_field = MapLayerModel._meta.get_field("choropleth_field")
            except FieldDoesNotExist:
                raise LookupError("Your MapLayerModel has no field named 'choropleth_field', which is mandatory.")
            choropleths = MapLayerModel.objects.exclude(choropleth_field="").filter(choropleth_field__isnull=False).values_list(
                "identifier", "geom_layer", "choropleth_unit", "name")
            store["choropleths"] = {
                item[0]: {
                    'layers': [item[1]],
                    'useFeatureState': True,
                    'unit': [item[2]],
                    'title': [item[3]]
                }
                for item in choropleths
            }

            # get popups
            try:
                model_field = MapLayerModel._meta.get_field("popup_fields")
            except FieldDoesNotExist:
                raise LookupError("Your MapLayerModel has no field named 'popup_fields', which is mandatory.")

            popups = MapLayerModel.objects.filter(popup_fields__isnull=False).values_list("identifier", "geom_layer")
            transformed_popups = {}
            for item in popups:
                layer_id = item[1]
                choropleth = item[0]

                if layer_id not in transformed_popups:
                    transformed_popups[layer_id] = {
                        'layerID': layer_id,
                        'atDefaultLayer': False,
                        'choropleths': []
                    }

                transformed_popups[layer_id]['choropleths'].append(choropleth)

            store["popups"] = transformed_popups

        context["mapengine_store_cold_init"] = store

        return context
