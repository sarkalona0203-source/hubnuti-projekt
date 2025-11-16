from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from kalkulacka.views_api import (
    vypocet, ulozeny_plan, ulozit_z_existujiciho,
    vsechna_jidla, get_progress, add_progress, delete_progress, register
)
from kalkulacka.views_user import profile_detail, profile_edit
from django.conf import settings
from django.conf.urls.static import static
from kalkulacka.views_admin import admin_dashboard
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token

def root_view(request):
    return JsonResponse({"message": "✅ API běží."})

urlpatterns = [
    path("", root_view, name="root"),
    path("admin/", admin.site.urls),

    # API
    path("api/vypocet/", vypocet, name="vypocet"),
    path("api/ulozeny_plan/", ulozeny_plan, name="ulozeny_plan"),
    path("api/ulozit_z_existujiciho/", ulozit_z_existujiciho, name="ulozit_z_existujiciho"),
    path("api/vsechna_jidla/", vsechna_jidla, name="vsechna_jidla"),
    path("api/get_progress/", get_progress, name="get_progress"),
    path("api/add_progress/", add_progress, name="add_progress"),
    path("api/delete_progress/<int:pk>/", delete_progress, name="delete_progress"),

    # Пользовательские страницы
    path("profile/", profile_detail, name="profile_detail"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    path("api/token/", obtain_auth_token, name="api-token"),
    path("api/register/", register, name="register"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
