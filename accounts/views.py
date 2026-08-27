from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, ProfileForm
from .models import Profile


def login_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():

        login(request, form.get_user())

        return redirect("accounts:dashboard")

    return render(
        request,
        "accounts/login.html",
        {"form": form}
    )


def logout_view(request):

    logout(request)

    return redirect("accounts:login")


def register_view(request):

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        user = form.save(commit=False)

        user.set_password(
            form.cleaned_data["password"]
        )

        user.save()

        Profile.objects.create(
            user=user,
            role=form.cleaned_data["role"]
        )

        return redirect("accounts:login")

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )


@login_required
def dashboard_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "accounts/role_dashboard.html",
        {"profile": profile}
    )


@login_required
def profile_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    form = ProfileForm(
        request.POST or None,
        instance=profile
    )

    if request.method == "POST" and form.is_valid():

        form.save()

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "profile": profile,
        }
    )