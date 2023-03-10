import json
import pathlib
from collections import namedtuple

import environ
from django.conf import settings
from range_key_dict import RangeKeyDict

from . import choropleth

env = environ.Env()

# If given, use local PROJ_LIB environment variable
if env("PROJ_LIB", default=False):
    PROJ_LIB = env("PROJ_LIB")

DISTILL = env.bool("DISTILL", False)
USE_DISTILLED_MVTS = env.bool("USE_DISTILLED_MVTS", True)

TILING_SERVICE_TOKEN = env.str("TILING_SERVICE_TOKEN", default=None)
TILING_SERVICE_STYLE_ID = env.str("TILING_SERVICE_STYLE_ID", default=None)

STYLES_DIR = pathlib.Path(env.path("MAP_ENGINE_STYLES_FOLDER"))

# STYLES
CHOROPLETHS = choropleth.Choropleth(STYLES_DIR / "choropleths.json")

with pathlib.Path(STYLES_DIR / "layer_styles.json").open("r", encoding="utf-8") as layer_styles_file:
    LAYER_STYLES = json.load(layer_styles_file)
LAYER_STYLES.update(CHOROPLETHS.get_static_styles())

# REGIONS
MIN_ZOOM = getattr(settings, "MAP_ENGINE_MIN_ZOOM", 8)
MAX_ZOOM = getattr(settings, "MAP_ENGINE_MAX_ZOOM", 22)
MAX_DISTILLED_ZOOM = getattr(settings, "MAP_ENGINE_MAX_DISTILLED_ZOOM", 10)
DEFAULT_CLUSTER_ZOOM = getattr(settings, "MAP_ENGINE_CLUSTER_ZOOM", 11)

Zoom = namedtuple("MinMax", ["min", "max"])

ZOOM_LEVELS = {}
REGIONS = []


def get_region_zooms():
    return RangeKeyDict({zoom: layer for layer, zoom in ZOOM_LEVELS.items() if layer in REGIONS})
