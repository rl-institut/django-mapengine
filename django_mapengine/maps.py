"""Registry and context-building for (possibly multiple) maps in a project."""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from django.conf import settings

from django_mapengine import layers, setup, sources

if TYPE_CHECKING:
    from django.http import HttpRequest


def get_map_config(name: str = "default") -> setup.MapConfig:
    """
    Return the MapConfig for the given map name.

    If 'MAP_ENGINE_MAPS' is set, the named config is looked up from it. Otherwise only
    the 'default' map exists, synthesized from the flat 'MAP_ENGINE_*' settings, so
    single-map projects keep working without defining 'MAP_ENGINE_MAPS'.

    Parameters
    ----------
    name : str
        Name of the map to look up.

    Returns
    -------
    MapConfig
        Configuration of the requested map.

    Raises
    ------
    KeyError
        if no map with the given name is configured.
    """
    configured_maps = settings.MAP_ENGINE_MAPS
    if configured_maps:
        try:
            return configured_maps[name]
        except KeyError as error:
            raise KeyError(
                f"No map config found for map name {name!r}. Known maps: {sorted(configured_maps)}."
            ) from error
    if name != "default":
        raise KeyError(
            f"No map config found for map name {name!r}. "
            "'MAP_ENGINE_MAPS' is not set, so only the 'default' map is available."
        )
    return setup.MapConfig(
        name="default",
        center=settings.MAP_ENGINE_CENTER_AT_STARTUP,
        zoom=settings.MAP_ENGINE_ZOOM_AT_STARTUP,
        min_zoom=settings.MAP_ENGINE_MIN_ZOOM,
        max_zoom=settings.MAP_ENGINE_MAX_ZOOM,
        max_bounds=settings.MAP_ENGINE_MAX_BOUNDS,
        layers=None,
        layers_at_startup=settings.MAP_ENGINE_LAYERS_AT_STARTUP,
        hover_layers=settings.MAP_ENGINE_HOVER_LAYERS,
        choropleths=settings.MAP_ENGINE_CHOROPLETHS,
        popups=settings.MAP_ENGINE_POPUPS,
    )


def _with_distilled(layer_ids: list[str]) -> list[str]:
    """
    Expand a list of layer IDs with their distilled counterparts.

    Parameters
    ----------
    layer_ids : list[str]
        Base layer IDs.

    Returns
    -------
    list[str]
        Each layer ID immediately followed by its '_distilled' counterpart.
    """
    return list(itertools.chain.from_iterable([layer_id, f"{layer_id}_distilled"] for layer_id in layer_ids))


def build_map_context(map_config: setup.MapConfig, request: "HttpRequest") -> dict:
    """
    Build the full template context (setup, sources, layers, store) for one map.

    Parameters
    ----------
    map_config : MapConfig
        Configuration of the map to build context for.
    request : HttpRequest
        Current request, needed to build absolute source/tile URLs.

    Returns
    -------
    dict
        Context to render the map's templates (container, JSON data, store) with.
    """
    cluster_layers = [
        cluster.layer_id
        for cluster in settings.MAP_ENGINE_API_CLUSTERS
        if map_config.layers is None or cluster.layer_id in map_config.layers
    ]
    store_cold_init = {
        "debugMode": settings.MAP_ENGINE_DEBUG,
        "popups": {popup.layer_id: popup.as_dict() for popup in map_config.popups},
        "hover_layers": _with_distilled(map_config.hover_layers),
        "result_views": {},
        "cluster_layers": cluster_layers,
        "choropleths": {choropleth.name: choropleth.as_dict() for choropleth in map_config.choropleths},
        "basemap": map_config.basemap,
    }
    dom_id_names = (
        "mapengine_setup",
        "mapengine_sources",
        "mapengine_basemap_layers",
        "mapengine_layers",
        "mapengine_images",
        "mapengine_layers_at_startup",
        "mapengine_store_cold_init",
    )
    dom_ids = {f"{name}_id": f"{name}_{map_config.name}" for name in dom_id_names}
    return {
        "map_name": map_config.name,
        "mapengine_setup": map_config.get_setup(),
        "mapengine_sources": {source.name: source.get_source(request) for source in sources.get_all_sources()},
        "mapengine_basemap_layers": [basemap.as_dict() for basemap in settings.MAP_ENGINE_BASEMAPS],
        "mapengine_layers": [layer.get_layer() for layer in layers.get_all_layers(map_config)],
        "mapengine_layers_at_startup": _with_distilled(map_config.layers_at_startup),
        "mapengine_images": [image.as_dict() for image in settings.MAP_ENGINE_IMAGES],
        "mapengine_store_cold_init": store_cold_init,
        **dom_ids,
    }
