from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    re_path(r"^rosetta/", include("rosetta.urls"))
]

urlpatterns += i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path(
        "api/borrowing_service/",
        include("borrowing_service.urls", namespace="borrowing_service")
    ),
    path("api/books/", include("books_service.urls")),
    path("api/user/", include("user.urls", namespace="user")),
    path(
        "api/payments/",
        include("payments_service.urls", namespace="payments")
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui"
    ),
    path(
        "api/doc/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc"
    ),
)

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
