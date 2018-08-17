from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve as static_serve
from app.views import page_not_found
from app.views import server_error
from app.views import forbidden
from . import well_known

urlpatterns = [
    url(r"^", include("app.urls")),
    url(r"^admin/", admin.site.urls),
    url(
        # management of well-known for LetsEncrypt
        r"^\.well-known/acme-challenge/(?P<filename>.*)/$",
        well_known.acme_challenge
    )
]

handler403 = "app.views.forbidden"
handler404 = "app.views.page_not_found"
handler500 = "app.views.server_error"

if settings.DEBUG:
    urlpatterns.append(
        url(
            r"^media/(?P<path>.*)$",
            static_serve,
            {"document_root": settings.MEDIA_ROOT}
        )
    )
    urlpatterns.append(
        url(
            r"^404/$",
            page_not_found
        )
    )
    urlpatterns.append(
        url(
            r"^500/$",
            server_error
        )
    )
    urlpatterns.append(
        url(
            r"^403/$",
            forbidden
        )
    )
