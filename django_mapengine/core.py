from collections import namedtuple

from range_key_dict import RangeKeyDict

from .conf import settings

MapImage = namedtuple("MapImage", ["name", "path"])
Zoom = namedtuple("MinMax", ["min", "max"])


def get_region_zooms():
    return RangeKeyDict({zoom: layer for layer, zoom in settings.ZOOM_LEVELS.items() if layer in settings.REGIONS})
