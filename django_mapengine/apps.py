"""Config for django app"""

from django.apps import AppConfig


class DjangoMapengineConfig(AppConfig):
    """Config for django-mapengine app"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_mapengine"
