from collections import namedtuple
from dataclasses import dataclass

from django.templatetags.static import static


Zoom = namedtuple("MinMax", ["min", "max"])


@dataclass
class MapImage:
    name: str
    filename: str

    @property
    def path(self) -> str:
        return static(self.filename)
