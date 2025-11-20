from django.shortcuts import redirect
from django.urls import reverse

class RoleRedirectMiddleware:
    """
    Middleware для редиректа пользователей по их роли:
    - Админ → всегда в /admin/
    - Обычный пользователь → не пускаем в /admin/, редирект на профиль
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        path = request.path

        # Не трогаем анонимных пользователей
        if not user or not user.is_authenticated:
            return self.get_response(request)

        # Исключаем статику и медиа
        if path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)

        # URL админки и профиля через reverse
        admin_url = reverse("admin:index")
        profile_url = reverse("profile_detail")  # убедись, что это имя URL твоего профиля

        # Админ → только админка
        if user.is_staff or user.is_superuser:
            if not path.startswith(admin_url):
                return redirect(admin_url)

        # Обычный пользователь → не пускаем в админку
        else:
            if path.startswith(admin_url):
                return redirect(profile_url)

        return self.get_response(request)