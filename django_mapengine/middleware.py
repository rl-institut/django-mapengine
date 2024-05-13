"""Mapengine middleware"""

from django.http import HttpResponse


class MapEngineMiddleware:  # pylint: disable=R0903
    """Catches non-existing MVTs and returns empty HTTPResponses instead"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Checks if request is for a distilled MVT and if response is okay.
        Otherwise, it returns empty 204 response.
        """
        response = self.get_response(request)
        if request.path.startswith("/static/mvts") and response.status_code == 404:
            return HttpResponse(status=204)
        return response
