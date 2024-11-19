"""Module to handle choropleths."""

import json
import math
import pathlib
from typing import Optional, Union

from . import colorbrewer

MAX_COLORBREWER_STEPS = 9

DEFAULT_CHOROPLETH_CONFIG = {"color_palette": "YlGnBu", "num_colors": 6}


class ChoroplethError(Exception):
    """Raised if something is wrong with choropleth values or parameters."""


class Choropleth:
    """Class to define load choropleth config and define colors for static and dynamic choropleths."""

    def __init__(self, choropleth_styles_file: Union[str, pathlib.Path]) -> None:
        """Initialize choropleth.

        Parameters
        ----------
        choropleth_styles_file: str
            Name or path to choropleth style file
        """
        if pathlib.Path(choropleth_styles_file).exists():
            with pathlib.Path(choropleth_styles_file).open("r", encoding="utf-8") as cs_file:
                self.choropleths = json.load(cs_file)
        else:
            self.choropleths = {}

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
            min_value = self.__calculate_lower_limit(min(values))
            max_value = self.__calculate_upper_limit(max(values))
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
        """
        Calculate step size

        Algorithm tries to find nice step sizes instead of simply dividing range by number of steps.
        """
        return (max_value - min_value) / num

    @staticmethod
    def __calculate_lower_limit(number: float) -> int:
        """
        Calculate a significant number as lower limit for choropleth coloring

        Parameters
        ----------
        number: float
            find lower limit for this number

        Returns
        -------
        int
            rounded down value by meaningful amount

        Raises
        ------
        ValueError
            if lower limit cannot be found
        """
        if number == 0:
            return int(number)
        if number < 1:
            return int((number * 10) / 10)
        if number >= 1:
            digits = int(math.log10(number))
            return int(number / 10**digits) * 10**digits
        raise ValueError(f"Cannot find lower limit for {number=}")

    @staticmethod
    def __calculate_upper_limit(number: float) -> int:
        """Calculate a significant number as upper limit for choropleth coloring.

        Parameters
        ----------
        number: float
            find upper limit for this number

        Returns
        -------
        int
            rounded up value by meaningful amount, depending on the size of number

        Raises
        ------
        ValueError
            if upper limit cannot be found
        """
        if number <= 1:
            return math.ceil((number * 10) / 10)
        if number > 1:
            digits = int(math.log10(number))
            return math.ceil(number / 10**digits) * 10**digits
        raise ValueError(f"Cannot find upper limit for {number=}")
