from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class _CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return reason  # devolvemos el motivo en vez de una respuesta HTTP


def enforce_csrf(request):
    """Falla con 403 si falta o no coincide el header X-CSRFToken."""
    check = _CSRFCheck(lambda req: None)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied(f"CSRF falló: {reason}")


class CookieTokenAuthentication(TokenAuthentication):
    """El token viaja en una cookie HttpOnly, no en un header Authorization."""

    def authenticate(self, request):
        key = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if not key:
            return None
        usuario, token = self.authenticate_credentials(key)
        enforce_csrf(request)  # solo bloquea POST/PUT/PATCH/DELETE
        return (usuario, token)