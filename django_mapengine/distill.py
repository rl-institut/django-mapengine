"""Module holding helper functions for MVT destillation."""


from django.conf import settings


def get_coordinates_for_distilling() -> tuple[int, int, int]:
    """Return x,y,z coordinates for each layer in order to distill it.

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
                yield x, y, z


def get_all_statics_for_state_lod() -> tuple[int, int, int]:
    """Return distill coordinates for given layer.

    Yields
    ------
    tuple[int, int, int]
        Holding x,y,z
    """
    for x, y, z in get_coordinates_for_distilling():
        yield z, x, y
