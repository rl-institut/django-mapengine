"""Module to handle choropleths."""

import json
import math
import pathlib
from typing import Optional, Union

from . import colorbrewer

MAX_COLORBREWER_STEPS = 9

DEFAULT_CHOROPLETH_CONFIG = {"color_palette": "YlGnBu", "num_colors": 6}

DEFAULT_ZERO_ANCHOR_RATIO = 0.6


class ChoroplethError(Exception):
    """Raised if something is wrong with choropleth values or parameters."""


class Choropleth:
    """Class to define load choropleth config and define colors for static and dynamic choropleths."""

    def __init__(
        self,
        choropleth_styles_file: Union[str, pathlib.Path],
        zero_anchor_ratio: float = DEFAULT_ZERO_ANCHOR_RATIO,
    ) -> None:
        """Initialize choropleth.

        Parameters
        ----------
        choropleth_styles_file: str
            Name or path to choropleth style file
        zero_anchor_ratio: float
            If `min_value / max_value` of the dynamic values is below this ratio, the lower bound
            of the color range is anchored at zero instead of being rounded to a nice number near
            the actual minimum.
        """
        if pathlib.Path(choropleth_styles_file).exists():
            with pathlib.Path(choropleth_styles_file).open("r", encoding="utf-8") as cs_file:
                self.choropleths = json.load(cs_file)
        else:
            self.choropleths = {}
        self.zero_anchor_ratio = zero_anchor_ratio

    def get_config(self, name: str) -> dict:
        """
        Reads config for given name

        Return s default config if name is not found.

        Parameters
        ----------
        name: str
            Name of choropleth to look up in choropleth config file

        Returns
        -------
        dict
            containing choropleth config
        """
        if name in self.choropleths:
            return self.choropleths[name]
        return DEFAULT_CHOROPLETH_CONFIG

    def get_static_styles(self) -> dict[str, list]:
        """Return choropleth styles for static (fixed values) choropleths.

        Returns
        -------
        Dict[str, list]
            Dictionary of fill colors for each static choropleth
        """
        static_choropleths: dict = {}
        for name in self.choropleths:
            try:
                static_choropleths[name] = self.get_fill_color(name)
            except ChoroplethError:
                continue
        return static_choropleths

    def __calculate_steps(self, choropleth_config: dict, values: Optional[list] = None) -> list[float]:
        """
        Calculate needed steps, either from given values or from static values in choropleth config.

        Parameters
        ----------
        choropleth_config : dict
            holding choropleth config
        values : Optional[list]
            List with dynamic values (i.e. from simulation)

        Returns
        -------
        list[float]
            Steps to use in choropleth color style

        Raises
        ------
        ChoroplethError
            If values are out of range or invalid.
            If values are neither given nor set in config.
        """
        if values:
            if min(values) < 0 or max(values) <= 0:
                error_msg = "the given values are not valid or out of range"
                raise ChoroplethError(error_msg)
            min_value, max_value = self.__calculate_nice_bounds(min(values), max(values))
            if choropleth_config["num_colors"]:
                num = choropleth_config["num_colors"]
            else:
                num = 6
            step_size = self.__calculate_step_size(min_value, max_value, num)
            return [min_value + i * step_size for i in range(num)] + [max_value]

        if "values" not in choropleth_config:
            error_msg = "Values have to be set in style file in order to composite choropleth colors."
            raise ChoroplethError(error_msg)
        return choropleth_config["values"]

    def get_fill_color(self, name: str, values: Optional[list] = None) -> list:
        """Return fill_color in choropleth style for setPaintProperty of maplibre.

        Parameters
        ----------
        name: str
            Name of choropleth
        values: Optional
            Values must be given either dynamically as parameter or must be present as static values in choropleths

        Returns
        -------
        dict:
            Dictionary which can be used as fill_color in maplibre layer

        Raises
        ------
        ChoroplethError
            if `color_palette` key is invalid
        IndexError
            if values exceed colorbrewer steps
        """
        choropleth_config = self.get_config(name)
        steps = self.__calculate_steps(choropleth_config, values)
        if choropleth_config["color_palette"] not in colorbrewer.sequential["multihue"]:
            error_msg = f"Invalid color palette for choropleth {name=}."
            raise ChoroplethError(error_msg)
        if len(steps) > MAX_COLORBREWER_STEPS:
            error_msg = f"Too many choropleth values given for {name=}."
            raise IndexError(error_msg)
        colors = colorbrewer.sequential["multihue"][choropleth_config["color_palette"]][len(steps) - 1]
        fill_color = [
            "interpolate-hcl",
            ["linear"],
            ["feature-state", name],
        ]
        for value, color in zip(steps, colors):
            fill_color.append(value)
            rgb_color = f"rgb({color[0]}, {color[1]}, {color[2]})"
            fill_color.append(rgb_color)
        return fill_color

    @staticmethod
    def __calculate_step_size(min_value: float, max_value: float, num: int) -> float:
        """Calculate step size by dividing the (already nice) value range into equal bins."""
        return (max_value - min_value) / num

    def __calculate_nice_bounds(self, min_value: float, max_value: float) -> tuple[float, float]:
        """Calculate a nice-looking lower and upper bound around the given values.

        The upper bound is always rounded up to a nice number (1, 2, 5 or 10 times a power of
        ten) covering the value range. The lower bound is anchored at zero unless the values are
        clustered far enough from zero (see `zero_anchor_ratio`), in which case it is rounded down
        to a nice number instead.

        Parameters
        ----------
        min_value: float
            Smallest value to cover
        max_value: float
            Largest value to cover

        Returns
        -------
        tuple[float, float]
            Nice lower and upper bound
        """
        if min_value == max_value:
            step = self.__calculate_nice_step(min_value if min_value > 0 else 1.0)
            lower = math.floor(min_value / step) * step
            return lower, lower + step

        step = self.__calculate_nice_step(max_value - min_value)
        upper = math.ceil(max_value / step) * step
        if max_value == 0 or min_value / max_value < self.zero_anchor_ratio:
            return 0.0, upper
        return math.floor(min_value / step) * step, upper

    @staticmethod
    def __calculate_nice_step(value: float) -> float:
        """Calculate a nice step size (1, 2, 5 or 10 times a power of ten) covering the value.

        Parameters
        ----------
        value: float
            Value the step size must cover

        Returns
        -------
        float
            Nice step size
        """
        exponent = math.floor(math.log10(value))
        fraction = value / 10**exponent
        if fraction <= 1:
            nice_fraction = 1
        elif fraction <= 2:
            nice_fraction = 2
        elif fraction <= 5:
            nice_fraction = 5
        else:
            nice_fraction = 10
        return nice_fraction * 10**exponent
