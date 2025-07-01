"""Module which holds MVTManager to use in models.py."""

from __future__ import annotations


import django.db.models
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.geos import Polygon
from django.core.exceptions import FieldError
from django.db import connection
from rest_framework.serializers import ValidationError
from rest_framework_gis.tilenames import tile_edges


# pylint: disable=W0223, R0901
class AsMVTGeom(models.functions.GeomOutputGeoFunc):  # noqa: D101
    """Add postgis class for function ST_AsMVTGeom."""

    function = "ST_AsMVTGeom"
    geom_param_pos = (0, 1)


class MVTManager(models.Manager):
    """Manager to get MVTs from model geometry using postgres MVT abilities."""

    def __init__(
        self,
        *args,  # noqa: ANN002
        geo_col: str = "geom",
        columns: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Init."""
        super().__init__(*args, **kwargs)
        self.geo_col = geo_col
        self.columns = columns

    def get_mvt_query(self, x: int, y: int, z: int, filters: dict | None = None) -> tuple:
        """Build MVT query; might be overwritten in child class."""
        filters = filters or {}
        return self._build_mvt_query(x, y, z, filters)

    def get_columns(self) -> list[str]:
        """Return columns to use as features in MVT."""
        return self.columns or self._get_non_geom_columns()

    # pylint: disable=W0613,R0913
    def _filter_query(  # noqa: PLR0913
        self,
        query: django.db.models.QuerySet,
        x: int,  # noqa: ARG002
        y: int,  # noqa: ARG002
        z: int,  # noqa: ARG002
        filters: dict,
    ) -> django.db.models.QuerySet:
        """
        Filter queryset for given filters.

        Might be overwritten in child class
        """
        return query.filter(**filters)

    def _get_mvt_geom_query(self, x: int, y: int, z: int) -> django.db.models.QuerySet:
        """Intersect bbox from given coordinates and return related MVT."""
        bbox = Polygon.from_bbox(tile_edges(x, y, z))
        bbox.srid = 4326
        query = self.annotate(
            mvt_geom=AsMVTGeom(Transform(self.geo_col, 3857), Transform(bbox, 3857), 4096, 0, False),  # noqa: FBT003
        )
        intersect = {f"{self.geo_col}__intersects": bbox}
        return query.filter(**intersect)

    def _build_mvt_query(self, x: int, y: int, z: int, filters: dict) -> str:
        """
        Create MVT query.

        Parameters
        ----------
        x : int
            x-coordinate of tile
        y : int
            y-coordinate of tile
        z : int
            z-coordinate of tile
        filters : dict
            keys represent column names and values represent column values to filter on.

        Returns
        -------
        tuple
            A tuple of length two.  The first element is a string representing a
            parameterized SQL query WHERE clause.  The second element is a list
            of parameters used as inputs to the WHERE clause.

        Raises
        ------
        ValidationError
            if sql query cannot be build with given parameters

        """
        query = self._get_mvt_geom_query(x, y, z)
        query = self._filter_query(query, x, y, z, filters)

        try:
            sql, params = query.query.sql_with_params()
        except FieldError as error:
            raise ValidationError(str(error)) from error
        with connection.cursor() as cursor:
            return cursor.mogrify(sql, params)

    def _get_non_geom_columns(self) -> list[str]:
        """
        Retrieve all table columns that are NOT the defined geometry column.

        Returns
        -------
        list-of-str
            List of column names (excluding geom)

        """
        columns = []
        for field in self.model._meta.get_fields():  # noqa: SLF001
            if hasattr(field, "get_attname_column"):
                column_name = field.get_attname_column()[1]
                if column_name != self.geo_col:
                    columns.append(column_name)
        return columns
