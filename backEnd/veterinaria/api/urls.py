from django.urls import path

from veterinaria.api.views_auth import CsrfView, LoginView, LogoutView, MeView

urlpatterns = [
    path("auth/csrf/", CsrfView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MeView.as_view()),
]