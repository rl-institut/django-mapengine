"""Module holding helper functions for MVT destillation."""

import range_key_dict

from django.conf import settings


def get_region_zooms():
    """Create range-key-dict from regions and related zoom factors."""
    return range_key_dict.RangeKeyDict(
        {zoom: layer for layer, zoom in settings.MAP_ENGINE_ZOOM_LEVELS.items() if layer in settings.MAP_ENGINE_REGIONS}
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
    for z in range(settings.MIN_ZOOM, settings.MAX_DISTILLED_ZOOM + 1):
        z_factor = 2 ** (z - settings.MIN_ZOOM)
        for x in range(settings.X_AT_MIN_Z * z_factor, (settings.X_AT_MIN_Z + 1) * z_factor + settings.X_OFFSET):
            for y in range(settings.Y_AT_MIN_Z * z_factor, (settings.Y_AT_MIN_Z + 1) * z_factor + settings.Y_OFFSET):
                if layer in settings.REGIONS and get_region_zooms()[z] != layer:
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
