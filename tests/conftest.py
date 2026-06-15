import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory


@pytest.fixture
def user(db):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password123")
    return user


@pytest.fixture
def request_factory():
    return RequestFactory()

