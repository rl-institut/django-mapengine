"""Fake django models used in tests"""

from django.db import models


class Municipality(models.Model):
    """Test region"""

    name = models.CharField(max_length=255)


class WindTurbine(models.Model):
    """Test cluster/MVT model"""

    name = models.CharField(max_length=255)


class PVRoof(models.Model):
    """Test cluster/MVT model"""

    name = models.CharField(max_length=255)
