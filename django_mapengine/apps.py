"""Config for django app"""

import json
import pathlib
from typing import Dict, List, Tuple

import environ
from appconf import AppConf
from django.conf import settings

from . import choropleth, setup

env = environ.Env()


class MapEngineConf(AppConf):
    """Config for django-mapengine app"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_mapengine"

    DEBUG = getattr(settings, "DEBUG", False)

    # If given, use local PROJ_LIB environment variable
    if env("PROJ_LIB", default=False):
        PROJ_LIB = env("PROJ_LIB")

    DISTILL = env.bool("MAP_ENGINE_DISTILL", False)
    USE_DISTILLED_MVTS = env.bool("MAP_ENGINE_USE_DISTILLED_MVTS", True)

    TILING_SERVICE_TOKEN = env.str("MAP_ENGINE_TILING_SERVICE_TOKEN", default=None)
    TILING_SERVICE_STYLE_ID = env.str("MAP_ENGINE_TILING_SERVICE_STYLE_ID", default=None)

    # STYLES
    if not hasattr(settings, "MAP_ENGINE_STYLES_FOLDER"):
        raise RuntimeError("'MAP_ENGINE_STYLES_FOLDER' has to be set for django-mapengine.")
    CHOROPLETH_STYLES = choropleth.Choropleth(pathlib.Path(settings.MAP_ENGINE_STYLES_FOLDER) / "choropleths.json")

    with (pathlib.Path(settings.MAP_ENGINE_STYLES_FOLDER) / "layer_styles.json").open(
        "r", encoding="utf-8"
    ) as layer_styles_file:
        LAYER_STYLES = json.load(layer_styles_file)
    LAYER_STYLES.update(CHOROPLETH_STYLES.get_static_styles())

    # MAP
    # Must use getattr for constants which are used directly!
    MIN_ZOOM: int = getattr(settings, "MAP_ENGINE_MIN_ZOOM", 8)
    MAX_ZOOM: int = getattr(settings, "MAP_ENGINE_MAX_ZOOM", 22)
    MAX_DISTILLED_ZOOM: int = 10
    CLUSTER_ZOOM: int = 11
    CENTER_AT_STARTUP: Tuple[int, int] = settings.MAP_ENGINE_CENTER_AT_STARTUP
    ZOOM_AT_STARTUP: int = settings.MAP_ENGINE_ZOOM_AT_STARTUP
    MAX_BOUNDS = getattr(settings, "MAP_ENGINE_MAX_BOUNDS", None)
    SETUP = {
        "container": "map",
        "style": f"https://api.maptiler.com/maps/{TILING_SERVICE_STYLE_ID}/style.json?key={TILING_SERVICE_TOKEN}",
        "center": CENTER_AT_STARTUP,
        "zoom": ZOOM_AT_STARTUP,
        "minZoom": MIN_ZOOM,
        "maxZoom": MAX_ZOOM,
    }
    if MAX_BOUNDS:
        SETUP["maxBounds"] = MAX_BOUNDS

    LAYER_SWITCH_CLASS = "layer__switch"

    # MVTS and CLUSTERS

    BASEMAPS = [
        setup.MaptilerBasemap(
            "dataviz-light",
            source_id="dataviz-light",
            type="raster",
            format="png",
            image="django_mapengine/images/layer_ctrl_light.svg",
            description="Light basemap for data visualization",
        ),
        setup.MaptilerBasemap(
            "dataviz-dark",
            source_id="dataviz-dark",
            type="raster",
            format="png",
            image="django_mapengine/images/layer_ctrl_dark.svg",
            description="Dark basemap for data visualization",
        ),
        setup.MaptilerBasemap(
            "satellite",
            source_id="satellite",
            type="raster",
            image="django_mapengine/images/layer_ctrl_satellite.svg",
            description="Satellite basemap view",
        ),
    ]
    API_MVTS = {}
    API_CLUSTERS = []

    SOURCES = []
    LAYERS = []

    # LAYERS
    LAYERS_AT_STARTUP: List[str] = []

    # IMAGES
    IMAGES: List[Dict[str, str]] = []

    # CHOROPLETHS
    CHOROPLETHS = []

    # POPUPS
    POPUPS: List[str] = []

    # DISTILL
    X_AT_MIN_Z = 136
    Y_AT_MIN_Z = 84
    X_OFFSET = 1  # Defines how many tiles to the right are added at first level
    Y_OFFSET = 1  # Defines how many tiles to the bottom are added at first level

    HOVER_LAYERS = getattr(settings, "MAP_HOVER_LAYERS", [])

    # pylint:disable=R0903
    class Meta:
        """
        App config meta

        Sets prefix to be used in settings, so that i.e. "POPUPS" becomes "MAP_ENGINE_POPUPS".
        """

        prefix = "MAP_ENGINE"
