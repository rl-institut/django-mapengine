"""Module holding helper functions for MVT destillation."""

import range_key_dict

from django.conf import settings


def get_region_layer_for_zoom_level(zoom_level):
    """Return region layer for zoom level."""
    zoom_layers = range_key_dict.RangeKeyDict(
        {zoom: layer for layer, zoom in settings.MAP_ENGINE_ZOOM_LEVELS.items() if layer in settings.MAP_ENGINE_REGIONS}
    )
    try:
        return zoom_layers[zoom_level]
    except KeyError:
        # pylint: disable = W0707
        raise KeyError(
            f"Cannot detect region layer for zoom level '{zoom_level}'. "
            f"You must probably add layer for zoom level '{zoom_level + 1}' "
            f"(Note: upper bound zoom level is not included) in MAP_ENGINE_ZOOM_LEVELS "
            f"or adapt zoom level for existing region layer accordingly. "
        )


def get_coordinates_for_distilling(layer: str) -> tuple[int, int, int]:
    """Return x,y,z coordinates for each layer in order to distill it.

    Parameters
    ----------
    layer: str
        Layer to get tile coordinates for

    Yields
    ------
    tuple[int, int, int]
        Holding x,y,z
    """
    for z in range(settings.MAP_ENGINE_MIN_ZOOM, settings.MAP_ENGINE_MAX_DISTILLED_ZOOM + 1):
        z_factor = 2 ** (z - settings.MAP_ENGINE_MIN_ZOOM)
        for x in range(
            settings.MAP_ENGINE_X_AT_MIN_Z * z_factor,
            (settings.MAP_ENGINE_X_AT_MIN_Z + 1) * z_factor + settings.MAP_ENGINE_X_OFFSET * z_factor,
        ):
            for y in range(
                settings.MAP_ENGINE_Y_AT_MIN_Z * z_factor,
                (settings.MAP_ENGINE_Y_AT_MIN_Z + 1) * z_factor + settings.MAP_ENGINE_Y_OFFSET * z_factor,
            ):
                if layer in settings.MAP_ENGINE_REGIONS and get_region_layer_for_zoom_level(z) != layer:
                    continue
                yield x, y, z


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
    for x, y, z in get_coordinates_for_distilling(view_name):
        yield z, x, y
