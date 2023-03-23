"""Module to hold legend support"""

from dataclasses import dataclass
from typing import Optional

from . import layers, utils


@dataclass
class LegendLayer:
    """Define a legend item with color which can activate a layer from model in map."""

    name: str
    description: str
    layer: layers.ModelLayer = None
    layer_id: str = None
    color: Optional[str] = None

    def __post_init__(self):
        if self.layer is None and self.layer_id is None:
            raise ValueError("You must either set layer or layer_id.")

    def get_color(self) -> str:
        """
        Return color to show on legend. If color is not set, color is tried to be read from layer style.

        Returns
        -------
        str
            Color string (name/rgb/hex/etc.) to be used on legend in frontend.
        """
        if self.color:
            return self.color
        return utils.get_color(self.get_layer_id())

    @property
    def style(self) -> dict:
        """
        Return layer style

        Returns
        -------
        dict
            layer style
        """
        return utils.get_layer_style(self.get_layer_id())

    def get_layer_id(self) -> str:
        """
        Return layer id either from layer or from user input

        Returns
        -------
        str
            Layer ID used in maplibre
        """
        if self.layer_id:
            return self.layer_id
        return self.layer.id

    @property
    def model(self):
        """
        Return related model

        Either from stored layer or by looking up layer id in registered layers

        Returns
        -------
        models.Model
            Model related to current legend layer
        """
        if self.layer:
            return self.layer.model
        return layers.get_layer_by_id(self.get_layer_id()).model
