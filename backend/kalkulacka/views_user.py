from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm

@login_required
def profile_detail(request):
    """Показывает профиль текущего пользователя."""
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Профиль не найден.")
        return redirect("home")  # или на любую другую страницу
    return render(request, "kalkulacka/profile_detail.html", {"profile": profile})

@login_required
def profile_edit(request):
    """Редактирование профиля текущего пользователя."""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil byl úspěšně aktualizován ✅")
            return redirect("profile_detail")
        else:
            messages.error(request, "Ошибка при сохранении профиля. Проверьте данные.")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "kalkulacka/profile_edit.html", {"form": form})