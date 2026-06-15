from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from typing import Callable

from django_audit.context import set_current_user, reset_current_user

User = get_user_model()


class CurrentUserMiddleware:
    """
    Middleware to automatically store the current user in contextvars.

    This ensures that models or other parts of the code can access the
    user performing the request without explicitly passing it.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Called for each HTTP request.

        Args:
            request: The incoming HTTP request object.

        Returns:
            response: The HTTP response returned by the next middleware or view.
        """
        user = getattr(request, "user")
        token = set_current_user(f"[{user.id}] {getattr(user, User.USERNAME_FIELD)}")
        try:
            response: HttpResponse = self.get_response(request)
        finally:
            reset_current_user(token)

        return response
