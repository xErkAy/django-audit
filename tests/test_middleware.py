import pytest
from django.test import RequestFactory
from django_audit.middlewares import CurrentUserMiddleware
from django_audit.tests_app.models import TestModel


@pytest.mark.django_db
def test_current_user_middleware_sets_context(user, request_factory):
    rf = request_factory
    request = rf.get("/")
    request.user = user

    def get_response(req):
        t = TestModel.objects.create(name="mw-test", value=5)
        return t

    middleware = CurrentUserMiddleware(get_response)
    res = middleware(request)

    from django_audit.db.models.store import StoreAudit

    audits = StoreAudit.objects.filter(model_name="TestModel", instance_id=res.id)
    assert audits.exists()
    audit = audits.first()
    assert str(user.id) in (audit.user or "")

