from django.shortcuts import render


def page_not_found(request, exception=None):
    response = render(
        request,
        "errors/404.html",
        status=404,
    )
    response["X-TurkDemy-Error-Page"] = "1"
    return response
