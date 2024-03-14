"""Module to hold legend support"""

from dataclasses import dataclass
from typing import Optional

from . import utils


@dataclass
class LegendLayer:
    """Define a legend item with color which can activate a layer from model in map."""

    name: str
    description: str
    layer_id: str
    color: Optional[str] = None

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
        return utils.get_color(self.layer_id)

    @property
    def style(self) -> dict:
        """
        Return layer style

        Returns
        -------
        dict
            layer style
        """
        return utils.get_layer_style(self.layer_id)
