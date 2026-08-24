from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

def index(request):
    return JsonResponse({"project": "TurkDemy", "status": "ok"})

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("health/", include("apps.health.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
