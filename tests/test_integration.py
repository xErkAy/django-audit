import pytest
from django.test import RequestFactory
from django_audit.middlewares import CurrentUserMiddleware
from django_audit.tests_app.models import TestModel
from django_audit.db.models.store import StoreAudit


@pytest.mark.django_db
def test_full_request_cycle_creates_audit(user, request_factory):
    rf = request_factory
    request = rf.post("/create/")
    request.user = user

    def view_create(req):
        return TestModel.objects.create(name="from-view", value=99)

    middleware = CurrentUserMiddleware(view_create)
    obj = middleware(request)

    audit = StoreAudit.objects.filter(model_name="TestModel", instance_id=obj.id).first()
    assert audit is not None
    assert "TestModel" in audit.model_name
    assert str(user.id) in (audit.user or "")
    assert audit.action in ("Создание", "created", "Creation")

