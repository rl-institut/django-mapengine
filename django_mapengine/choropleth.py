"""Module to handle choropleths."""

import json
import pathlib
import math
from typing import Optional, Union

import colorbrewer

MAX_COLORBREWER_STEPS = 9


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
        with pathlib.Path(choropleth_styles_file).open("r", encoding="utf-8") as cs_file:
            self.choropleths = json.load(cs_file)

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

    def __calculate_lower_limit(self,mini):
        if mini == 0:
            limit = mini
            return limit
        if mini > 1:
            new_mini = mini
            if isinstance(mini, float):
                new_mini = str(mini).split(".")[0]

            length = len(str(new_mini))
            first_number = int(str(new_mini)[:1])

            limit = first_number * (10 ** (length - 1))
        if mini < 1:
            mini = str(mini).split(".")[1]
            limit = int(mini[:1]) / 10

        return limit

    def __calculate_upper_limit(self,maxi):
        if maxi < 1:
            limit = math.ceil(maxi * 10) / 10
        if maxi > 1:
            if isinstance(maxi, float):
                maxi = int(str(maxi).split("."))
            length = 10 * len(str(maxi))
            intermediate = math.ceil(maxi / length * 10) / 10
            limit = intermediate * length

        return limit

    @staticmethod
    def __calculate_steps(self,choropleth_config: dict, values: Optional[list] = None) -> list[float]:
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
            If values are given, but no num_colors is set.
            If values are neither given nor set in config.
        """
        if values:
            if "num_colors" not in choropleth_config:
                error_msg = "Number of colors has to be set in choropleth style for dynamic choropleth composition."
                raise ChoroplethError(error_msg)
            if max(values) <= 0 or min(values) < 0:
                error_msg = "the given values are not valid"
                raise ChoroplethError(error_msg)
            min_value = self.__calculate_lower_limit(min(values))
            max_value = self.__calculate_upper_limit(max(values))
            num = choropleth_config["num_colors"]
            step = (max_value - min_value) / (num - 1)
            return [min_value + i * step for i in range(num - 1)] + [max_value]

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
            if either `num_colors` or `values` key is missing in choropleth style
        IndexError
            if values exceed colorbrewer steps
        """
        choropleth_config = self.choropleths[name]
        steps = self.__calculate_steps(self,choropleth_config, values)
        if choropleth_config["color_palette"] not in colorbrewer.sequential["multihue"]:
            error_msg = f"Invalid color palette for choropleth {name=}."
            raise ChoroplethError(error_msg)
        if len(steps) > MAX_COLORBREWER_STEPS:
            error_msg = f"Too many choropleth values given for {name=}."
            raise IndexError(error_msg)
        colors = colorbrewer.sequential["multihue"][choropleth_config["color_palette"]][len(steps)]
        fill_color = [
            "interpolate",
            ["linear"],
            ["feature-state", name],
        ]
        for value, color in zip(steps, colors):
            fill_color.append(value)
            rgb_color = f"rgb({color[0]}, {color[1]}, {color[2]})"
            fill_color.append(rgb_color)
        return fill_color
