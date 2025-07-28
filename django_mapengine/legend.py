"""Module to hold legend support"""

import json
import pathlib
from dataclasses import dataclass
from typing import Optional, Union

from django.conf import settings

from . import utils


@dataclass
class LegendItem:
    """Define a legend item."""

    layer_name: str
    title: Optional[str] = None
    color: Optional[str] = None
    shape: Optional[str] = None
    tooltip: Optional[str] = None
    checked: Optional[bool] = None

    def __post_init__(self):
        """Set color from the layer name if not set."""
        if self.color is None:
            # Get color from layer styles
            self.color = utils.get_color(self.layer_name)
        if self.title is None:
            # Set up a title from layer name
            self.title = " ".join(map(lambda x: x.capitalize(), self.layer_name.split("_")))
        if self.shape is None:
            # Check if layer is cluster or not
            if self.layer_name in [cluster.layer_id for cluster in settings.MAP_ENGINE_API_CLUSTERS]:
                self.shape = "circle"
            else:
                self.shape = "square"
        if self.checked is None:
            # Check if the layer is in startup layers
            if self.layer_name in settings.MAP_ENGINE_LAYERS_AT_STARTUP:
                self.checked = True
            else:
                self.checked = False


class Legend:
    """Define a legend."""

    def __init__(self, categories: dict[str, list[Union[LegendItem, str]]]):
        """Initialize a legend with multiple categories and items."""
        self.categories = {
            category: [item if isinstance(item, LegendItem) else LegendItem(item) for item in items]
            for category, items in categories.items()
        }

    @classmethod
    def from_items(cls, title: str, items: list[Union[LegendItem, str]]):
        """Initialize legend from items."""
        return cls({title: [item if isinstance(item, LegendItem) else LegendItem(item) for item in items]})

    @classmethod
    def from_layer_names(cls, title: str, layer_names: list[str]):
        """Create legend items from layer names."""
        return cls({title: layer_names})

    @classmethod
    def from_json(cls, json_file: Union[pathlib.Path, str]):
        """Create legend from JSON file."""
        if isinstance(json_file, str):
            json_file = pathlib.Path(json_file)
        with json_file.open("r", encoding="utf-8") as file:
            json_data = json.load(file)
        return cls(
            {
                category: [LegendItem(**item) if isinstance(item, dict) else item for item in items]
                for category, items in json_data.items()
            }
        )

    def items(self):
        """Return legend items grouped by categories."""
        return self.categories.items()
