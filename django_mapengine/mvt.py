"""Module containing functions for preparing MVT responses from model managers"""

from dataclasses import dataclass
from typing import List

from django.db import connection
from django.db.models import QuerySet

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.renderers import BaseRenderer

from rest_framework.schemas.openapi import AutoSchema


class MVTSchema(AutoSchema):
    """OpenAPI schema for MVT endpoints documenting the tile, limit, and offset query parameters."""

    def get_operation(self, path, method):
        """Add MVT-specific query parameters to the generated OpenAPI operation."""
        operation = super().get_operation(path, method)
        operation.setdefault("parameters", []).extend(
            [
                {
                    "name": "tile",
                    "in": "query",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "TMS coordinates of the requested tile. The format should be tile=z/x/y",
                },
                {
                    "name": "limit",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": "Number of results to return per page.",
                },
                {
                    "name": "offset",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": "The initial index from which to return the results.",
                },
            ]
        )
        return operation


class BinaryRenderer(BaseRenderer):
    media_type = "application/*"
    format = "binary"
    charset = None
    render_style = "binary"

    # pylint: disable=no-self-use,unused-argument
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


@dataclass
class MVTSourceLayer:
    """Source layer and related queryset used in MVTView"""

    name: str
    queryset: QuerySet


class MVTResponse(Response):
    """This class is needed in order to distill empty MVTs, as empty responses does not have a key "Content-Type"."""

    def render(self):
        retval = super().render()
        self["Content-Type"] = self.content_type
        return retval


class MVTView(APIView):
    """Use MVTView in urls.py to create MVTs from models"""

    model = None
    geom_col = None
    renderer_classes = (BinaryRenderer,)
    schema = MVTSchema()
    layers: List[MVTSourceLayer] = []

    def get(self, request, *args, **kwargs):
        params = request.GET.dict()
        mvt = b""
        status = 400

        try:
            mvt = self._create_mvt(filters=params, *args, **kwargs)
            status = 200 if mvt else 204
        except ValidationError:
            pass

        response = MVTResponse(mvt, content_type="application/vnd.mapbox-vector-tile", status=status)
        response["Content-Type"] = "application/vnd.mapbox-vector-tile"
        return response

    def _create_mvt(self, z, x, y, filters):
        if not self.layers:
            return None

        mvt_geom_queries = ", ".join(
            f"q{i} AS ({layer.queryset.get_mvt_query(x, y, z, filters)})" for i, layer in enumerate(self.layers)
        )

        mvt_select_queries = ", ".join(
            f"s{i} AS (SELECT {','.join(layer.queryset.get_columns())}, mvt_geom::geometry FROM q{i})"
            for i, layer in enumerate(self.layers)
        )

        mvt_query = " UNION ALL ".join(
            f"SELECT ST_AsMVT(s{i}.*, '{layer.name}') FROM s{i}" for i, layer in enumerate(self.layers)
        )

        query = f"WITH {mvt_geom_queries}, {mvt_select_queries} {mvt_query};".strip()
        with connection.cursor() as cursor:
            cursor.execute(query)
            mvt_rows = cursor.fetchall()
        return b"".join(map(lambda row: bytes(row[0]), mvt_rows))  # noqa: C417


def mvt_view_factory(classname, layers):
    """Factory method for creating MVT views from settings"""
    return type(
        f"{classname}MVTView",
        (MVTView,),
        {"layers": layers},
    ).as_view()
