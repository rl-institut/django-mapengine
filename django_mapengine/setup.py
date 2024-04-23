"""Setup module is used in settings of django projects to set up mapengine"""

from collections import namedtuple
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from django.apps import apps
from django.conf import settings

if TYPE_CHECKING:
    from django.db.models import Manager, Model

Zoom = namedtuple("MinMax", ("min", "max"))


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
    use_feature_state: bool = True

    def as_dict(self) -> dict:
        """
        Return layers and useFeatureState as dict for choropleths in map engine

        Returns
        -------
        dict
            holding choropleth values needed in map setups
        """
        return {
            "title": self.title,
            "unit": self.unit,
            "layers": self.layers,
            "useFeatureState": self.use_feature_state,
        }


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
