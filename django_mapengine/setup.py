from collections import namedtuple
from dataclasses import dataclass

from django.conf import settings
from django.apps import apps


Zoom = namedtuple("MinMax", ("min", "max"))

@dataclass
class ModelAPI:
    layer_id: str
    app_name: str
    model_name: str

    @property
    def model(self):
        return apps.get_model(self.app_name, self.model_name)

class ClusterAPI(ModelAPI):
    pass


@dataclass
class MVTAPI(ModelAPI):
    layer_id: str
    app_name: str
    model_name: str
    manager_name: str = "vector_tiles"

    @property
    def manager(self):
        return getattr(self.model, self.manager_name)


@dataclass
class MapImage:
    name: str
    filename: str

    @property
    def path(self) -> str:
        return f"{settings.STATIC_URL}{self.filename}"

    def as_dict(self):
        return {"name": self.name, "path": self.path}
