from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from kalkulacka.views import vypocet, ulozeny_plan, ulozit_z_existujiciho, vsechna_jidla
from django.conf import settings
from django.conf.urls.static import static

def root_view(request):
    return JsonResponse({"message": "✅ API běží. Použijte /api/vypocet/ nebo /api/ulozeny-plan/."})

urlpatterns = [
    path("", root_view),
    path("admin/", admin.site.urls),
    path("api/vypocet/", vypocet, name="vypocet"),
    path("api/ulozeny_plan/", ulozeny_plan, name="ulozeny_plan"),
    path("api/ulozit_z_existujiciho/", ulozit_z_existujiciho, name="ulozit_z_existujiciho"),
    path("api/vsechna_jidla/", vsechna_jidla, name="vsechna_jidla"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)