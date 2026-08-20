"""Module to hold legend support"""

import json
import pathlib
from dataclasses import dataclass
from typing import Optional, Union

from django.conf import settings

from . import maps, utils


@dataclass
class LegendItem:
    """Define a legend item."""

    layer_name: str
    title: Optional[str] = None
    color: Optional[str] = None
    shape: Optional[str] = None
    tooltip: Optional[str] = None
    checked: Optional[bool] = None
    map_name: str = "default"

    def __post_init__(self):
        """Set color from the layer name if not set."""
        layer_name_pure = self.layer_name.removesuffix("_distilled")
        if self.color is None:
            # Get color from layer styles
            self.color = utils.get_color(layer_name_pure)
        if self.title is None:
            # Set up a title from layer name
            self.title = " ".join(map(lambda x: x.capitalize(), layer_name_pure.split("_")))
        if self.shape is None:
            # Check if layer is cluster or not
            if layer_name_pure in [cluster.layer_id for cluster in settings.MAP_ENGINE_API_CLUSTERS]:
                self.shape = "circle"
            else:
                self.shape = "square"
        if self.checked is None:
            # Check if the layer is in this map's startup layers
            map_config = maps.get_map_config(self.map_name)
            self.checked = layer_name_pure in map_config.layers_at_startup


class Legend:
    """Define a legend. Belongs to exactly one named map (see 'MAP_ENGINE_MAPS' setting)."""

    def __init__(
        self,
        categories: dict[str, list[Union[LegendItem, str]]],
        html_in_tooltips: bool = False,
        map_name: str = "default",
    ):
        """
        Initialize a legend with multiple categories and items.

        Parameters
        ----------
        categories : dict[str, list[Union[LegendItem, str]]]
            Legend items (or plain layer names) grouped by category title.
        html_in_tooltips : bool
            Whether tooltips may contain raw HTML.
        map_name : str
            Name of the map (see 'MAP_ENGINE_MAPS' setting) this legend belongs to.
        """
        self.map_name = map_name
        self.categories = {
            category: [item if isinstance(item, LegendItem) else LegendItem(item, map_name=map_name) for item in items]
            for category, items in categories.items()
        }
        self.html_in_tooltips = html_in_tooltips

    @classmethod
    def from_items(cls, title: str, items: list[Union[LegendItem, str]], **kwargs):
        """
        Initialize legend from items.

        Parameters
        ----------
        title : str
            Title of the (single) category holding these items.
        items : list[Union[LegendItem, str]]
            Legend items, or plain layer names to build them from.
        kwargs
            Passed through to the 'Legend' constructor (e.g. 'map_name', 'html_in_tooltips').

        Returns
        -------
        Legend
            Legend holding a single category with the given items.
        """
        return cls({title: items}, **kwargs)

    @classmethod
    def from_layer_names(cls, title: str, layer_names: list[str], **kwargs):
        """
        Create legend items from layer names.

        Parameters
        ----------
        title : str
            Title of the (single) category holding these items.
        layer_names : list[str]
            Layer names to build legend items from.
        kwargs
            Passed through to the 'Legend' constructor (e.g. 'map_name', 'html_in_tooltips').

        Returns
        -------
        Legend
            Legend holding a single category built from the given layer names.
        """
        return cls({title: layer_names}, **kwargs)

    @classmethod
    def from_json(cls, json_file: Union[pathlib.Path, str], **kwargs):
        """
        Create legend from JSON file.

        Parameters
        ----------
        json_file : Union[pathlib.Path, str]
            Path to a JSON file holding legend categories/items.
        kwargs
            Passed through to the 'Legend' constructor (e.g. 'map_name', 'html_in_tooltips').
            'map_name' is also used as the default for any item that doesn't specify its own.

        Returns
        -------
        Legend
            Legend built from the JSON file's categories/items.
        """
        if isinstance(json_file, str):
            json_file = pathlib.Path(json_file)
        with json_file.open("r", encoding="utf-8") as file:
            json_data = json.load(file)
        map_name = kwargs.get("map_name", "default")
        return cls(
            {
                category: [
                    LegendItem(**{"map_name": map_name, **item}) if isinstance(item, dict) else item for item in items
                ]
                for category, items in json_data.items()
            },
            **kwargs,
        )

    def items(self):
        """
        Return legend items grouped by categories.

        Returns
        -------
        ItemsView
            Legend items grouped by category title.
        """
        return self.categories.items()
