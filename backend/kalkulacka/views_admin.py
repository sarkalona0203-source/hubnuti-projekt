from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Profile

@staff_member_required
def admin_dashboard(request):
    profiles = Profile.objects.all()
    return render(request, "admin_dashboard.html", {"profiles": profiles})