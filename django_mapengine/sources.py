"""Defines sources in backend to use with maplibre in frontend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from . import settings

if TYPE_CHECKING:
    from django.http import HttpRequest


# pylint: disable=R0902
@dataclass
class MapSource:
    """Default map source to be used in maplibre."""

    name: str
    type: str  # noqa: A003
    promote_id: str = "id"
    tiles: Optional[list[str]] = None
    url: Optional[str] = None
    minzoom: Optional[int] = None
    maxzoom: Optional[int] = None

    def get_source(self, request: HttpRequest) -> dict:
        """
        Return source data/tiles using current host and port from request.

        Parameters
        ----------
        request: HttpRequest
            Django request holding host and port

        Returns
        -------
        dict
            Containing source data for map

        Raises
        ------
        TypeError
            if type is not supported as map source type.
        """
        source = {"type": self.type, "promoteId": self.promote_id}
        if self.minzoom:
            source["minzoom"] = self.minzoom
        if self.maxzoom:
            source["maxzoom"] = self.maxzoom
        if self.type in ("vector", "raster"):
            source["tiles"] = [
                tile if tile.startswith("http") else f"{request.get_raw_uri()}{tile}" for tile in self.tiles
            ]
        elif self.type == "geojson":
            source["data"] = self.url if self.url.startswith("http") else f"{request.get_raw_uri()}{self.url}"
        else:
            raise TypeError(f"Unsupported source type '{self.type}'.")
        return source


@dataclass
class ClusterMapSource(MapSource):
    """Map source for clustered layers."""

    cluster_max_zoom: int = settings.DEFAULT_CLUSTER_ZOOM

    def get_source(self, request: HttpRequest) -> dict:
        """
        Return source data for clustering.

        Parameters
        ----------
        request: HttpRequest
            Django request holding host and port

        Returns
        -------
        dict
            Containing cluster source data for map
        """
        source = super().get_source(request)
        source["cluster"] = True
        source["clusterMaxZoom"] = self.cluster_max_zoom
        return source
