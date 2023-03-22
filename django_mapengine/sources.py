"""Defines sources in backend to use with maplibre in frontend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from django.conf import settings

if TYPE_CHECKING:
    from collections.abc import Iterable

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

    cluster_max_zoom: int = settings.MAP_ENGINE_CLUSTER_ZOOM

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


def get_region_sources() -> Iterable[MapSource]:
    """
    Return region sources from mapengine settings

    Yields
    ------
    MapSource
        (Distilled) map sources for all regions
    """
    if settings.MAP_ENGINE_USE_DISTILLED_MVTS:
        for region in settings.MAP_ENGINE_REGIONS:
            if settings.MAP_ENGINE_ZOOM_LEVELS[region].min >= settings.MAP_ENGINE_MAX_DISTILLED_ZOOM:
                yield MapSource(name=region, type="vector", tiles=[f"map/{region}_mvt/{{z}}/{{x}}/{{y}}/"])
            else:
                yield MapSource(
                    name=region,
                    type="vector",
                    tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{region}.mvt"],
                    maxzoom=settings.MAP_ENGINE_MAX_DISTILLED_ZOOM + 1,
                )
    else:
        for region in settings.MAP_ENGINE_REGIONS:
            yield MapSource(name=region, type="vector", tiles=[f"map/{region}_mvt/{{z}}/{{x}}/{{y}}/"])


def get_static_sources() -> Iterable[MapSource]:
    """
    Return sources for all MVTs other than region- or cluster-based

    If distilling is used, a second map source for each API is yield, regarding the distilled MVTs.

    Yields
    ------
    MapSource
        for each MVT API which is not a region
    """
    for source in settings.MAP_ENGINE_API_MVTS:
        if source in settings.MAP_ENGINE_REGIONS:
            continue
        yield MapSource(source, type="vector", tiles=[f"map/{source}_mvt/{{z}}/{{x}}/{{y}}/"])
        if settings.MAP_ENGINE_USE_DISTILLED_MVTS:
            yield MapSource(f"{source}_distilled", type="vector", tiles=[f"static/mvts/{{z}}/{{x}}/{{y}}/{source}.mvt"])


def get_cluster_sources() -> Iterable[MapSource]:
    """
    Return geojson sources for all clusters

    Yields
    ------
    MapSource
        for each cluster
    """
    for cluster in settings.MAP_ENGINE_API_CLUSTERS:
        yield ClusterMapSource(cluster.layer_id, type="geojson", url=f"map/clusters/{cluster.layer_id}.geojson")


def get_satellite_source() -> MapSource:
    """
    Return source for satellite basemap

    Returns
    -------
    MapSource
        of satellite raster
    """
    return MapSource(
        "satellite",
        type="raster",
        tiles=[
            "https://api.maptiler.com/tiles/satellite-v2/"
            f"{{z}}/{{x}}/{{y}}.jpg?key={settings.MAP_ENGINE_TILING_SERVICE_TOKEN}",
        ],
    )
