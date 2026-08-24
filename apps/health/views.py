from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})


def ready(request):
    return JsonResponse({"status": "ready"})
