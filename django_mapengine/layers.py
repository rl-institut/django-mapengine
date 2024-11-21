"""Defines layers in backend to use with maplibre in frontend."""

from __future__ import annotations

from dataclasses import dataclass
import pathlib
from typing import TYPE_CHECKING, List, Optional

from django.conf import settings

from django_mapengine.setup import BasemapLayer, MapLayer

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django_mapengine import setup


@dataclass
class ModelLayer:
    """Defines a layer by using a django model."""

    # pylint:disable=C0103
    id: str  # noqa: A003
    source: str
    source_layer: Optional[str] = None
    minzoom: Optional[int] = None
    maxzoom: Optional[int] = None

    def __post_init__(self):
        self.minzoom = self.minzoom if self.minzoom is not None else settings.MAP_ENGINE_MIN_ZOOM
        self.maxzoom = self.maxzoom if self.maxzoom is not None else settings.MAP_ENGINE_MAX_ZOOM + 1
        if self.minzoom < settings.MAP_ENGINE_MIN_ZOOM:
            raise ValueError(
                f"Error in ModelLayer '{self.id}': "
                f"Minimal zoom cannot be less than MAP_ENGINE_MIN_ZOOM={settings.MAP_ENGINE_MIN_ZOOM}."
            )
        if self.maxzoom > settings.MAP_ENGINE_MAX_ZOOM + 1:
            raise ValueError(
                f"Error in ModelLayer '{self.id}': "
                f"Maximal zoom cannot be more than MAP_ENGINE_MAX_ZOOM={settings.MAP_ENGINE_MAX_ZOOM}."
            )

    def get_source_layer(self) -> str:
        """By default, layer ID is used as source layer."""
        return self.source_layer if self.source_layer else self.id


@dataclass
class StaticModelLayer(ModelLayer):
    """Defines a static layer based on a model."""

    style: Optional[str] = None

    def get_min_zoom(self, *, distill: bool = False) -> int:
        """
        Return minimal zoom. Depends on whether distilling is activated or not.

        Parameters
        ----------
        distill : bool
            Whether or not distilling is activated.

        Returns
        -------
        int
            Minimal zoom
        """
        return max(
            settings.MAP_ENGINE_MAX_DISTILLED_ZOOM + 1
            if not distill and settings.MAP_ENGINE_USE_DISTILLED_MVTS
            else settings.MAP_ENGINE_MIN_ZOOM,
            self.minzoom,
        )

    def get_max_zoom(self, *, distill: bool = False) -> int:
        """
        Return maximal zoom. Depends on whether distilling is activated or not.

        If distilling is activated, distilled source is used until MAX_DISTILLED_ZOOM,
        otherwise zooming goes up to MAX_ZOOM.

        Parameters
        ----------
        distill : bool
            Whether or not distilling is activated.

        Returns
        -------
        int
            Maximal zoom
        """
        return min(
            settings.MAP_ENGINE_MAX_ZOOM + 1 if not distill else settings.MAP_ENGINE_MAX_DISTILLED_ZOOM + 1,
            self.maxzoom,
        )

    def get_style(self):
        """Return style from style name if set, otherwise use ID to get style."""
        if self.style:
            return get_layer_style(self.style)
        return get_layer_style(self.id)

    def get_map_layers(self) -> Iterable[MapLayer]:
        """
        Return map layers based on model and distill setting.

        Yields
        -------
        MapLayer
            Static map layer is always returned. Distilled map layer is returned if distilling is active.
        """
        yield MapLayer(
            id=self.id,
            source=self.source,
            source_layer=self.get_source_layer(),
            minzoom=self.get_min_zoom(),
            maxzoom=self.get_max_zoom(),
            style=self.get_style(),
        )
        if settings.MAP_ENGINE_USE_DISTILLED_MVTS:
            yield MapLayer(
                id=f"{self.id}_distilled",
                source=self.source if self.source in settings.MAP_ENGINE_REGIONS else f"{self.source}_distilled",
                source_layer=self.get_source_layer(),
                minzoom=self.get_min_zoom(distill=True),
                maxzoom=self.get_max_zoom(distill=True),
                style=self.get_style(),
            )


@dataclass
class ClusterModelLayer(ModelLayer):
    """Holds logic for clustered layers from django models."""

    def get_map_layers(self) -> Iterable[MapLayer]:
        """
        Return map layers for clustered model data.

        One for unclustered points (original data), one for drawing clustered points and
        one for writing number of clusterd points.

        Yields
        -------
        MapLayer
            To be shown in maplibre
        """
        yield MapLayer(
            id=self.id,
            source=self.source,
            style=get_layer_style(self.id),
        )
        yield MapLayer(
            id=f"{self.id}_cluster",
            source=self.source,
            style=get_layer_style(f"{self.id}_cluster"),
        )
        yield MapLayer(
            id=f"{self.id}_cluster_count",
            source=self.source,
            style=get_layer_style(f"{self.id}_cluster_count"),
        )


def get_basemap_layers() -> Iterable[BasemapLayer]:
    """Return basemap layers"""
    for basemap in settings.MAP_ENGINE_BASEMAPS:
        yield BasemapLayer(id=basemap.layer_id, source=basemap.layer_id, type=basemap.type)


def get_static_layers() -> Iterable[StaticModelLayer]:
    """
    Return model layers for static-based MVTs.

    As multiple layers can have same source (via source_layer), API_MVTs is a dict where key is used as parent source.
    Additionally, sources and source layers are reused if same model manager is used for multiple layers.

    Yields
    ------
    StaticModelLayer
        Static model layers to show models on map.
    """
    managers = {}
    for original_source, mvt_apis in settings.MAP_ENGINE_API_MVTS.items():
        for mvt_api in mvt_apis:
            source_layer = mvt_api.layer_id
            manager_reference = f"{mvt_api.model_name}.{mvt_api.manager_name}"
            if manager_reference in managers:
                # Add model managers only once and use source and source layer in multiple layers
                source, source_layer = managers[manager_reference]
            else:
                managers[manager_reference] = (original_source, source_layer)
                source = original_source
            yield StaticModelLayer(
                id=mvt_api.layer_id,
                source=source,
                source_layer=source_layer,
                minzoom=mvt_api.minzoom,
                maxzoom=mvt_api.maxzoom,
                style=mvt_api.style,
            )


def get_cluster_layers() -> Iterable[ClusterModelLayer]:
    """
    Return clustered model layers for preparing geojsons.

    Yields
    ------
    ClusterModelLayer
        Clustered model layers to show on map.
    """
    for cluster in settings.MAP_ENGINE_API_CLUSTERS:
        yield ClusterModelLayer(id=cluster.layer_id, source=cluster.layer_id)


def get_layer_by_id(layer_id: str) -> setup.ModelAPI:
    """
    Search for layer API defined in settings

    Parameters
    ----------
    layer_id : str
        ID/Name of the layer

    Returns
    -------
    ModelAPI
        API of a model source

    Raises
    ------
    KeyError
        if layer ID cannot be found
    """
    for cluster in settings.MAP_ENGINE_API_CLUSTERS:
        if cluster.layer_id == layer_id:
            return cluster
    for mvts in settings.MAP_ENGINE_API_MVTS.values():
        for mvt in mvts:
            if mvt.layer_id == layer_id:
                return mvt
    raise KeyError(f"Layer {layer_id=} not found.")


def get_all_layers() -> List[MapLayer]:
    """
    Return region, static and cluster layers as list

    Returns
    -------
    List[MapLayer]
        List of all region, static and cluster layers
    """
    # Order is important! Last items are shown on top!
    layers = []
    layers.extend(settings.MAP_ENGINE_LAYERS)
    for static_layer in get_static_layers():
        layers.extend(static_layer.get_map_layers())
    for cluster_layer in get_cluster_layers():
        layers.extend(cluster_layer.get_map_layers())
    return layers


def get_layer_style(layer_name: str) -> dict:
    """
    Return layer style for given layer name

    Parameters
    ----------
    layer_name: str
        Layer name to look up style for

    Returns
    -------
    dict
        Layer style for given layer name

    Raises
    ------
    KeyError
        if layer name is not found in layer styles file
    """
    if layer_name not in settings.MAP_ENGINE_LAYER_STYLES:
        raise KeyError(
            f"No style for {layer_name=} found. "
            f"Please add a related style in {pathlib.Path(settings.MAP_ENGINE_STYLES_FOLDER) / 'layer_styles.json'} "
            f"or adapt environment variable 'MAP_ENGINE_STYLES_FOLDER' if it points to wrong styles folder."
        )
    return settings.MAP_ENGINE_LAYER_STYLES[layer_name]
