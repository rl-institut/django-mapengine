"""Setup module is used in settings of django projects to set up mapengine"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Any

from django.apps import apps
from django.conf import settings
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.db.models import Manager, Model


@dataclass
class MaptilerBasemap:
    """
    Base class for a basemap

    This is used to:
    - prepare basemap layers
    - prepare basemap sources
    """

    layer_id: str
    source_id: str
    description: str
    image: str
    type: str = "vector"  # noqa: A003
    format: str = "jpg"

    def as_dict(self):
        """Return maptilerBasemap as dict"""
        return {
            "layer_id": self.layer_id,
            "source_id": self.source_id,
            "description": self.description,
            "image": self.image,
            "type": self.type,
            "format": self.format,
        }


@dataclass
class ModelAPI:
    """
    Base class for API interface

    This is used to:
    - set up API point via URL
    - prepare map layers
    - prepare map sources
    """

    layer_id: str
    app_name: str
    model_name: str

    @property
    def model(self) -> "Model":
        """
        Return related model based on app_name and model_name

        Returns
        -------
        Model
            Model used to create cluster or MVTs from
        """
        return apps.get_model(self.app_name, self.model_name)


# pylint:disable=R0903
@dataclass
class ClusterAPI(ModelAPI):
    """Exists only to distinguish between "normal" and clustered API"""

    properties: list = field(default_factory=lambda: [])


@dataclass
class MVTAPI(ModelAPI):
    """API for MVT-based models, which are accessed via model manager"""

    layer_id: str
    app_name: str
    model_name: str
    manager_name: str = "vector_tiles"
    minzoom: Optional[int] = None
    maxzoom: Optional[int] = None
    style: Optional[str] = None

    @property
    def manager(self) -> "Manager":
        """
        Return manager based on related model and manager_name

        Returns
        -------
        Manager
            Manger used to get MVTs from database
        """
        return getattr(self.model, self.manager_name)


@dataclass
class MapImage:
    """Images used in map can be set up using this class"""

    name: str
    filename: str

    @property
    def path(self) -> str:
        """
        Return url path to image

        Returns
        -------
        str
            static path to image
        """
        return f"{settings.STATIC_URL}{self.filename}"

    def as_dict(self) -> dict:
        """
        Return name and path of image as dict

        Returns
        -------
        dict
            holding name and path of image
        """
        return {"name": self.name, "path": self.path}


@dataclass
class Choropleth:
    """Choropleth class used to set up choropleths in project settings"""

    name: str
    title: str
    unit: str
    layers: List[str]
    labels: Optional[List[str]] = None
    use_feature_state: bool = True

    def as_dict(self) -> dict:
        """
        Return layers and useFeatureState as dict for choropleths in map engine

        Returns
        -------
        dict
            holding choropleth values needed in map setups
        """
        data = {
            "title": self.title,
            "unit": self.unit,
            "layers": self.layers,
            "useFeatureState": self.use_feature_state,
        }
        if self.labels is not None:
            data["labels"] = self.labels
        return data


@dataclass
class Popup:
    """Popup class used to set up popups in project settings"""

    layer_id: str
    popup_at_default_layer: bool = True
    choropleths: Optional[List[str]] = None

    def as_dict(self) -> dict:
        """
        Return dict for popups in map engine

        Returns
        -------
        dict
            holding popup values needed in map setups
        """
        return {
            "layerID": self.layer_id,
            "atDefaultLayer": self.popup_at_default_layer,
            "choropleths": self.choropleths,
        }


@dataclass
class BasemapLayer:
    """Default map layer used in maplibre."""

    # pylint:disable=C0103
    id: str  # noqa: A003
    source: str
    type: str  # noqa: A003

    def get_layer(self):
        """
        Build dict from layer settings and style.

        Returns
        -------
        dict
            to be used as layer in maplibre.
        """
        return {"id": self.id, "source": self.source, "type": self.type}


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


# pylint:disable=R0902
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
    kwargs: Optional[dict[str, Any]] = None

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
        kwargs = self.kwargs or {}
        source = {"type": self.type, "promoteId": self.promote_id, **kwargs}
        if self.minzoom:
            source["minzoom"] = self.minzoom
        if self.maxzoom:
            source["maxzoom"] = self.maxzoom
        if self.type in ("vector", "raster"):
            source["tiles"] = [
                tile if tile.startswith("http") else f"{request.scheme}://{request.get_host()}{tile}"
                for tile in self.tiles
            ]
        elif self.type == "geojson":
            source["data"] = (
                self.url if self.url.startswith("http") else f"{request.scheme}://{request.get_host()}{self.url}"
            )
        else:
            raise TypeError(f"Unsupported source type '{self.type}'.")
        return source
