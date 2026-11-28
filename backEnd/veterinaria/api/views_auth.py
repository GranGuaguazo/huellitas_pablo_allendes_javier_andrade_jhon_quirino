from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from veterinaria.api.authentication import enforce_csrf


def datos_usuario(user):
    if user.is_superuser:
        rol = "superusuario"
    else:
        rol = user.groups.values_list("name", flat=True).first()
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "rol": rol,
        "grupos": list(user.groups.values_list("name", flat=True)),
    }


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    """GET: entrega la cookie csrftoken al frontend."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "Cookie CSRF establecida."})


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        enforce_csrf(request)
        usuario = authenticate(
            username=request.data.get("username", ""),
            password=request.data.get("password", ""),
        )
        if usuario is None:
           return Response({"detail": "Usuario o contraseña incorrectos."}, status=400)

        token, _ = Token.objects.get_or_create(user=usuario)
        respuesta = Response(datos_usuario(usuario))  # el token NO va en el JSON
        respuesta.set_cookie(
            settings.AUTH_COOKIE_NAME,
            token.key,
            max_age=settings.AUTH_COOKIE_MAX_AGE,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="Lax",
        )
        return respuesta


class LogoutView(APIView):
    def post(self, request):
        request.auth.delete()  # invalida el token en el servidor
        respuesta = Response(status=204)
        respuesta.delete_cookie(settings.AUTH_COOKIE_NAME, samesite="Lax")
        return respuesta


class MeView(APIView):
    def get(self, request):
        return Response(datos_usuario(request.user))