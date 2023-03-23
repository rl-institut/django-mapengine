"""Various function to be used in other modules"""
from typing import Union

from django.conf import settings


def get_color(layer_id: str) -> Union[str, dict]:
    """
    Return color of given layer

    Parameters
    ----------
    layer_id : str
        Layer ID to lookup up in layer styles

    Returns
    -------
    Union[str, dict]
        Color of given layer

    Raises
    ------
    LookupError
        if color is not found in layer style
    """
    style = get_layer_style(layer_id)
    for color_key in ("fill-color", "line-color", "circle-color"):
        try:
            return style["paint"][color_key]
        except KeyError:
            continue
    raise LookupError(f"Could not find color for {layer_id=}.")


def get_layer_style(layer_id: str) -> dict:
    """
    Return layer style of given layer ID

    Parameters
    ----------
    layer_id : str
        Layer ID to lookup style

    Returns
    -------
    dict
        Layer style of given ID

    Raises
    ------
    LookupError
        if layer ID is not found in styles file
    """
    if layer_id not in settings.MAP_ENGINE_LAYER_STYLES:
        raise LookupError(f"Could not find '{layer_id=}' in layer styles.")
    return settings.MAP_ENGINE_LAYER_STYLES[layer_id]
