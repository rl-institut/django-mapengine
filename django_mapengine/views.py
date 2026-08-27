"""Views in order to use mapengine"""

from django.http import JsonResponse

from . import __version__


def index():
    """
    Placeholder to get app url from `urls.reverse()` function by calling `reverse("django_mapengine:index")`.

    Returns
    -------
    JsonResponse
        containing app name and current version
    """
    return JsonResponse({"app": "django_mapengine", "version": __version__})
