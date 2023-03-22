"""Setup module is used in settings of django projects to set up mapengine"""

from collections import namedtuple
from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings

if TYPE_CHECKING:
    from django.db.models import Manager, Model

Zoom = namedtuple("MinMax", ("min", "max"))


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
class ClusterAPI(ModelAPI):
    """Exists only to distinguish between "normal" and clustered API"""


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