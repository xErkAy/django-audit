import contextvars
from typing import Optional, Any

current_user_var: contextvars.ContextVar[Optional[Any]] = contextvars.ContextVar("current_user", default=None)


def set_current_user(user: Any) -> contextvars.Token:
    """
    Set the current user in the context.

    Args:
        user: The user instance to set in the context.

    Returns:
        token: A contextvars token that can be used to reset the user later.
    """
    token: contextvars.Token = current_user_var.set(user)
    return token


def reset_current_user(token: contextvars.Token) -> None:
    """
    Reset the current user to the previous value.

    Args:
        token: The contextvars token returned by set_current_user().
    """
    current_user_var.reset(token)


def get_current_user() -> Optional[Any]:
    """
    Retrieve the current user from the context.

    Returns:
        The current user if set, otherwise None.
    """
    return current_user_var.get()
