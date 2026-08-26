from django.shortcuts import render


class BrandedNotFoundMiddleware:
    """Render TurkDemy's branded 404 for normal HTML browser requests.

    This intentionally leaves API and health endpoints alone and does not catch
    non-404 exceptions, so developer errors remain visible while DEBUG=True.
    """

    excluded_prefixes = (
        "/api/",
        "/health/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code != 404:
            return response

        if response.headers.get("X-TurkDemy-Error-Page") == "1":
            return response

        if request.path.startswith(self.excluded_prefixes):
            return response

        accept = request.headers.get("Accept", "")
        if accept and "text/html" not in accept and "*/*" not in accept:
            return response

        branded = render(
            request,
            "errors/404.html",
            status=404,
        )
        branded["X-TurkDemy-Error-Page"] = "1"
        return branded
