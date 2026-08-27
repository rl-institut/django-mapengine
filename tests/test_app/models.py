"""Fake django models used in tests"""

from django.db import models

from django_mapengine.managers import MVTManager


class Municipality(models.Model):
    """Test region"""

    name = models.CharField(max_length=255)

    vector_tiles = MVTManager()
    label_tiles = MVTManager()


class WindTurbine(models.Model):
    """Test cluster/MVT model"""

    name = models.CharField(max_length=255)

    vector_tiles = MVTManager()


class PVRoof(models.Model):
    """Test cluster/MVT model"""

    name = models.CharField(max_length=255)

    vector_tiles = MVTManager()
