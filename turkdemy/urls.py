from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

admin.site.site_header = "TurkDemy Administration"
admin.site.site_title = "TurkDemy Admin"
admin.site.index_title = "Operations"

handler404 = "apps.core.views.page_not_found"


urlpatterns: list[URLPattern | URLResolver] = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("health/", include("apps.health.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("admin-tools/", include("apps.core.urls")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("apps.public.urls")),
    path("", include("apps.agents.urls")),
    path("", include("apps.leads.urls")),
)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
