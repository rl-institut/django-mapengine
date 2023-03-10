import django_mapengine.core
from .conf import settings


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
                if layer in settings.REGIONS and django_mapengine.core.get_region_zooms()[z] != layer:
                    continue
                yield x, y, z
