from django.contrib.auth.decorators import user_passes_test
from django.contrib import admin

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Supervisor

def approved_required(view_func):
    decorated = user_passes_test(
        lambda u: u.is_authenticated and u.is_approved
    )
    return decorated(view_func)



@admin.action(description="Approve selected students")
def approve_students(self, request, queryset):
    queryset.update(
        is_active=True,
        is_approved=True,
    )



def supervisor_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not request.user.is_supervisor:
            messages.error(
                request,
                "You do not have permission to access the supervisor area."
            )
            return redirect("dashboard")
        
        try:
            Supervisor.objects.get(user=request.user)
        except Supervisor.DoesNotExist:
            messages.error(
                request,
                "Supervisor profile not found."
            )
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper