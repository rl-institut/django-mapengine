"""Provides base classes for popups"""

from abc import ABC, abstractmethod
from typing import Optional

from django.http import response
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string


class Popup(ABC):
    """Base class for popups"""

    def __init__(self, lookup: str, selected_id: int, map_state: Optional[dict] = None, template: Optional[str] = None):
        self.lookup = lookup
        self.selected_id = selected_id
        self.map_state = map_state
        self.template = template or f"popups/{lookup}.html"

    def render(self) -> response.JsonResponse:
        """
        Renders everything and returns JsonResponse

        Returns
        -------
        response.JsonResponse
            containing html for popup
        """
        return response.JsonResponse(self.prepare_data())

    def prepare_data(self) -> dict:
        """
        Prepares html data for popup

        Returns
        -------
        dict
            containing html for popup
        """
        data = self.get_context_data()
        try:
            html = render_to_string(self.template, context=data)
        except TemplateDoesNotExist:
            html = render_to_string("popups/default.html", context=data)
        return {"html": html}

    @abstractmethod
    def get_context_data(self) -> dict:
        """
        Prepares data to be rendered in popup template

        Returns
        -------
        dict
            containing template context data
        """


class ChartPopup(Popup):
    """Base class for popups containing a chart"""

    def prepare_data(self) -> dict:
        """
        Prepares html and chart data

        Returns
        -------
        dict
            containing html and chart data for popup
        """
        data = super().prepare_data()
        data["chart"] = self.get_chart_options()
        return data

    @abstractmethod
    def get_chart_options(self) -> dict:
        """
        Returns chart options to be used in chart library in frontend

        Returns
        -------
        dict
            containing chart options
        """
