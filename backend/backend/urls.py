from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from kalkulacka.views import VypocetAPIView, JidloViewSet, MealPlanViewSet

def root_view(request):
    return JsonResponse({"message": "API работает, используйте /api/"})

router = DefaultRouter()
router.register(r'jidlo', JidloViewSet)
router.register(r'mealplans', MealPlanViewSet)

urlpatterns = [
    path("", root_view),
    # path("admin/", admin.site.urls),  # убрали админ
    path("api/vypocet/", VypocetAPIView.as_view()),
    path("api/", include(router.urls)),
]