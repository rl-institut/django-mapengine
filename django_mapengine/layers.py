"""Defines layers in backend to use with maplibre in frontend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from django.contrib.gis.db.models import Model

from . import settings

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass
class MapLayer:
    """Default map layer used in maplibre."""

    id: str  # noqa: A003
    type: str  # noqa: A003
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
        layer = {"id": self.id, "type": self.type, "source": self.source, **self.style}
        if self.source_layer:
            layer["source-layer"] = self.source_layer
        for attr_name in ("minzoom", "maxzoom"):
            if attr := getattr(self, attr_name):
                layer[attr_name] = attr
        return layer


@dataclass
class ModelLayer:
    """Defines a layer by using a django model."""

    id: str  # noqa: A003
    model: Model.__class__
    type: str  # noqa: A003
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
        return settings.MAX_DISTILLED_ZOOM + 1 if not distill and settings.USE_DISTILLED_MVTS else settings.MIN_ZOOM

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
        return settings.MAX_ZOOM if not distill else settings.MAX_DISTILLED_ZOOM + 1

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
            type=self.type,
            source=self.source,
            source_layer=self.id,
            minzoom=self.min_zoom(),
            maxzoom=self.max_zoom(),
            style=settings.LAYER_STYLES[self.id],
        )
        if settings.USE_DISTILLED_MVTS:
            yield MapLayer(
                id=f"{self.id}_distilled",
                type=self.type,
                source=f"{self.source}_distilled",
                source_layer=self.id,
                minzoom=self.min_zoom(distill=True),
                maxzoom=self.max_zoom(distill=True),
                style=settings.LAYER_STYLES[self.id],
            )


@dataclass
class ClusterModelLayer(ModelLayer):
    """Holds logic for clustered layers from django models."""

    def get_map_layers(self) -> MapLayer:
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
            type=self.type,
            source=self.source,
            style=settings.LAYER_STYLES[self.id],
        )
        yield MapLayer(
            id=f"{self.id}_cluster",
            type="circle",
            source=self.source,
            style=settings.LAYER_STYLES[f"{self.id}_cluster"],
        )
        yield MapLayer(
            id=f"{self.id}_cluster_count",
            type="symbol",
            source=self.source,
            style=settings.LAYER_STYLES[f"{self.id}_cluster_count"],
        )


def get_region_layers() -> list[MapLayer]:
    """
    Return map layers for region-based models.

    Returns three layers:
    - one for drawing region outline,
    - one for drawing region area and
    - one for drawing region name into center.

    Returns
    -------
    list[MapLayer]
        Map layers to sow regions on map.
    """
    return (
        [
            MapLayer(
                id=f"line-{layer}",
                type="line",
                source=layer,
                source_layer=layer,
                minzoom=settings.ZOOM_LEVELS[layer].min,
                maxzoom=settings.ZOOM_LEVELS[layer].max,
                style=settings.LAYER_STYLES["region-line"],
            )
            for layer in settings.REGIONS
        ]
        + [
            MapLayer(
                id=f"fill-{layer}",
                type="fill",
                source=layer,
                source_layer=layer,
                minzoom=settings.ZOOM_LEVELS[layer].min,
                maxzoom=settings.ZOOM_LEVELS[layer].max,
                style=settings.LAYER_STYLES["region-fill"],
            )
            for layer in settings.REGIONS
        ]
        + [
            MapLayer(
                id=f"label-{layer}",
                type="symbol",
                source=layer,
                source_layer=f"{layer}label",
                maxzoom=settings.ZOOM_LEVELS[layer].max,
                minzoom=settings.ZOOM_LEVELS[layer].min,
                style=settings.LAYER_STYLES["region-label"],
            )
            for layer in settings.REGIONS
        ]
    )
