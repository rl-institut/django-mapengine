from collections import namedtuple
from dataclasses import dataclass

from django.conf import settings


Zoom = namedtuple("MinMax", ["min", "max"])


@dataclass
class MapImage:
    name: str
    filename: str

    @property
    def path(self) -> str:
        return f"{settings.STATIC_URL}{self.filename}"

    def as_dict(self):
        return {"name": self.name, "path": self.path}
