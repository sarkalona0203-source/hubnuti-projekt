from rest_framework import permissions

class IsAdminOrOwner(permissions.BasePermission):
    """
    Разрешает доступ:
    - Админам (is_staff / is_superuser) ко всем объектам
    - Обычным пользователям только к своим объектам:
        - obj.user == request.user
        - obj.profile.user == request.user
    """

    def has_permission(self, request, view):
        # Доступ разрешен только аутентифицированным пользователям
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Админ имеет доступ ко всем объектам
        if user.is_staff or user.is_superuser:
            return True

        # Проверка obj.user
        if getattr(obj, "user", None) == user:
            return True

        # Проверка obj.profile.user
        profile = getattr(obj, "profile", None)
        if profile and getattr(profile, "user", None) == user:
            return True

        return False