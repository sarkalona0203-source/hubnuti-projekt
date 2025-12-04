from django.contrib import admin
from django.urls import path, re_path
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from kalkulacka.views_api import (
    vypocet, ulozeny_plan, ulozit_z_existujiciho,
    vsechna_jidla, get_progress, add_progress,
    delete_progress, register
)
from kalkulacka.views_user import profile_detail, profile_edit
from kalkulacka.views_admin import admin_dashboard
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token
from pathlib import Path


def root_view(request):
    return JsonResponse({"message": "API běží"})


def serve_react(request):
    index_file = settings.BASE_DIR.parent / "frontend" / "build" / "index.html"
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            return HttpResponse(f.read())
    except FileNotFoundError:
        return HttpResponse("❌ React build not found", status=404)


urlpatterns = [
    # === API ===
    path("api/", root_view),
    path("api/vypocet/", vypocet),
    path("api/ulozeny_plan/", ulozeny_plan),
    path("api/ulozit_z_existujiciho/", ulozit_z_existujiciho),
    path("api/vsechna_jidla/", vsechna_jidla),
    path("api/get_progress/", get_progress),
    path("api/add_progress/", add_progress),
    path("api/delete_progress/<int:pk>/", delete_progress),
    path("api/register/", register),
    path("api/token/", obtain_auth_token),

    # === User pages ===
    path("profile/", profile_detail),
    path("profile/edit/", profile_edit),
    path("admin-dashboard/", admin_dashboard),
    path("login/", auth_views.LoginView.as_view(template_name="login.html")),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/")),

    # === Django admin ===
    path("admin/", admin.site.urls),
]


# === 1) СТАТИКА REACT ===
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.BASE_DIR.parent / "frontend" / "build" / "static"
    )

# === 2) МЕДИА (Очень важно!) ===
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# === 3) ВСЁ ОСТАЛЬНОЕ — REACT SPA ===
urlpatterns += [
    re_path(r"^(?!api|admin).*", serve_react),
]