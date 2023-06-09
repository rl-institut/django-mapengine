"""Defines layers in backend to use with maplibre in frontend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from django.conf import settings
from django.contrib.gis.db.models import Model

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django_mapengine import setup


@dataclass
class MapLayer:
    """Default map layer used in maplibre."""

    # pylint:disable=C0103
    id: str  # noqa: A003
    source: str
    style: dict
    source_layer: Optional[str] = None
    minzoom: Optional[int] = None
    maxzoom: Optional[int] = None

    def get_layer(self) -> dict:
        """
        Build dict from layer settings and style.

        Returns
        -------
        dict
            to be used as layer in maplibre.
        """
        layer = {"id": self.id, "source": self.source, **self.style}
        if self.source_layer:
            layer["source-layer"] = self.source_layer
        for attr_name in ("minzoom", "maxzoom"):
            if attr := getattr(self, attr_name):
                layer[attr_name] = attr
        return layer


@dataclass
class ModelLayer:
    """Defines a layer by using a django model."""

    # pylint:disable=C0103
    id: str  # noqa: A003
    model: Model.__class__
    source: str


class StaticModelLayer(ModelLayer):
    """Defines a static layer based on a model."""

    @staticmethod
    def min_zoom(*, distill: bool = False) -> int:
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
        return (
            settings.MAP_ENGINE_MAX_DISTILLED_ZOOM + 1
            if not distill and settings.MAP_ENGINE_USE_DISTILLED_MVTS
            else settings.MAP_ENGINE_MIN_ZOOM
        )

    @staticmethod
    def max_zoom(*, distill: bool = False) -> int:
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
        return settings.MAP_ENGINE_MAX_ZOOM if not distill else settings.MAP_ENGINE_MAX_DISTILLED_ZOOM + 1

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
            source_layer=self.id,
            minzoom=self.min_zoom(),
            maxzoom=self.max_zoom(),
            style=settings.MAP_ENGINE_LAYER_STYLES[self.id],
        )
        if settings.MAP_ENGINE_USE_DISTILLED_MVTS:
            yield MapLayer(
                id=f"{self.id}_distilled",
                source=f"{self.source}_distilled",
                source_layer=self.id,
                minzoom=self.min_zoom(distill=True),
                maxzoom=self.max_zoom(distill=True),
                style=settings.MAP_ENGINE_LAYER_STYLES[self.id],
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
            style=settings.MAP_ENGINE_LAYER_STYLES[self.id],
        )
        yield MapLayer(
            id=f"{self.id}_cluster",
            source=self.source,
            style=settings.MAP_ENGINE_LAYER_STYLES[f"{self.id}_cluster"],
        )
        yield MapLayer(
            id=f"{self.id}_cluster_count",
            source=self.source,
            style=settings.MAP_ENGINE_LAYER_STYLES[f"{self.id}_cluster_count"],
        )


def get_region_layers() -> Iterable[MapLayer]:
    """
    Return map layers for region-based models.

    Returns three layers:
    - one for drawing region outline,
    - one for drawing region area and
    - one for drawing region name into center.

    Yields
    ------
    MapLayer
        Map layers to show regions on map.
    """
    for layer in settings.MAP_ENGINE_REGIONS:
        yield MapLayer(
            id=layer,
            source=layer,
            source_layer=layer,
            minzoom=settings.MAP_ENGINE_ZOOM_LEVELS[layer].min,
            maxzoom=settings.MAP_ENGINE_ZOOM_LEVELS[layer].max,
            style=settings.MAP_ENGINE_LAYER_STYLES["region-fill"],
        )
        yield MapLayer(
            id=f"{layer}-line",
            source=layer,
            source_layer=layer,
            minzoom=settings.MAP_ENGINE_ZOOM_LEVELS[layer].min,
            maxzoom=settings.MAP_ENGINE_ZOOM_LEVELS[layer].max,
            style=settings.MAP_ENGINE_LAYER_STYLES["region-line"],
        )
        yield MapLayer(
            id=f"{layer}-label",
            source=layer,
            source_layer=f"{layer}label",
            maxzoom=settings.MAP_ENGINE_ZOOM_LEVELS[layer].max,
            minzoom=settings.MAP_ENGINE_ZOOM_LEVELS[layer].min,
            style=settings.MAP_ENGINE_LAYER_STYLES["region-label"],
        )


def get_static_layers() -> Iterable[StaticModelLayer]:
    """
    Return model layers for static-based MVTs.

    As multiple layers can have same source (via source_layer), API_MVTs is a dict where key is used as parent source.

    Yields
    ------
    StaticModelLayer
        Static model layers to show models on map.
    """
    for source, mvt_apis in settings.MAP_ENGINE_API_MVTS.items():
        if source in settings.MAP_ENGINE_REGIONS:
            continue
        for mvt_api in mvt_apis:
            yield StaticModelLayer(id=mvt_api.layer_id, model=mvt_api.model, source=source)


def get_cluster_layers() -> Iterable[ClusterModelLayer]:
    """
    Return clustered model layers for preparing geojsons.

    Yields
    ------
    ClusterModelLayer
        Clustered model layers to show on map.
    """
    for cluster in settings.MAP_ENGINE_API_CLUSTERS:
        yield ClusterModelLayer(id=cluster.layer_id, model=cluster.model, source=cluster.layer_id)


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
    layers = list(get_region_layers())
    for static_layer in get_static_layers():
        layers.extend(static_layer.get_map_layers())
    for cluster_layer in get_cluster_layers():
        layers.extend(cluster_layer.get_map_layers())
    return layers
