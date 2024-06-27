"""Defines sources in backend to use with maplibre in frontend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from django import urls
from django.conf import settings

from django_mapengine.setup import MapSource

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.http import HttpRequest


# pylint: disable=R0902


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


def get_static_sources() -> Iterable[MapSource]:
    """
    Return sources for all MVTs other than region- or cluster-based

    If distilling is used, a second map source for each API is yield, regarding the distilled MVTs.

    Yields
    ------
    MapSource
        for each MVT API which is not a region
    """
    app_url = urls.reverse_lazy("django_mapengine:index")
    for source in settings.MAP_ENGINE_API_MVTS:
        yield MapSource(source, type="vector", tiles=[f"{app_url}{source}_mvt/{{z}}/{{x}}/{{y}}/"])
        if settings.MAP_ENGINE_USE_DISTILLED_MVTS:
            yield MapSource(
                f"{source}_distilled", type="vector", tiles=[f"/static/mvts{app_url}{{z}}/{{x}}/{{y}}/{source}.mvt"]
            )


def get_cluster_sources() -> Iterable[MapSource]:
    """
    Return geojson sources for all clusters

    Yields
    ------
    MapSource
        for each cluster
    """
    for cluster in settings.MAP_ENGINE_API_CLUSTERS:
        yield ClusterMapSource(
            cluster.layer_id, type="geojson", url=urls.reverse_lazy(f"django_mapengine:{cluster.layer_id}_cluster")
        )


def get_satellite_sources() -> Iterable[MapSource]:
    """
    Return source for satellite basemap

    Returns
    -------
    MapSource
        of satellite raster
    """
    for basemap in settings.MAP_ENGINE_BASEMAPS:
        yield MapSource(
            basemap.layer_id,
            type=basemap.type,
            tiles=[
                f"https://api.maptiler.com/maps/{basemap.source_id}/"
                f"{{z}}/{{x}}/{{y}}.{basemap.format}?key={settings.MAP_ENGINE_TILING_SERVICE_TOKEN}",
            ],
        )


def get_all_sources() -> List[MapSource]:
    """
    Return all map sources for regions, satellite, statics and clusters

    Returns
    -------
    List[MapSource]
        all map sources
    """
    sources = []
    sources.extend(get_satellite_sources())
    sources.extend(get_static_sources())
    sources.extend(get_cluster_sources())
    sources.extend(settings.MAP_ENGINE_SOURCES)
    return sources
