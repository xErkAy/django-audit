import pytest
from django_audit.db.models.store import StoreAudit
from django_audit.tests_app.models import TestModel


@pytest.mark.django_db
def test_testmodel_save_creates_storeaudit(monkeypatch):
    """Saving a TestModel instance should create a StoreAudit row and call hook."""

    hook_calls = []

    def fake_process_model_hook(*, obj, user, model_name, instance_id, action, changes=None):
        hook_calls.append({
            "obj_id": obj.pk,
            "user": user,
            "model_name": model_name,
            "instance_id": instance_id,
            "action": action,
            "changes": changes,
        })

    monkeypatch.setattr("django_audit.db.hook.process_model_hook", fake_process_model_hook)

    t = TestModel.objects.create(name="alpha", value=10)

    audits = StoreAudit.objects.filter(model_name="TestModel", instance_id=t.id)
    assert audits.exists()

    assert len(hook_calls) >= 1
    assert hook_calls[-1]["model_name"] == "TestModel"


@pytest.mark.django_db
def test_testmodel_update_records_changes(monkeypatch):
    hook_calls = []

    def fake_hook(*, obj, user, model_name, instance_id, action, changes=None):
        hook_calls.append({
            "action": action,
            "changes": changes,
        })

    monkeypatch.setattr("django_audit.db.hook.process_model_hook", fake_hook)

    t = TestModel.objects.create(name="beta", value=1)
    t.value = 42
    t.save()

    assert any(call["action"] != "" for call in hook_calls)
    audit = StoreAudit.objects.filter(model_name="TestModel", instance_id=t.id).order_by("-created_at").first()
    assert audit is not None
    assert isinstance(audit.changes, dict)


@pytest.mark.django_db
def test_delete_creates_audit(monkeypatch):
    hook_calls = []

    def fake_hook(*, obj, user, model_name, instance_id, action, changes=None):
        hook_calls.append(action)

    monkeypatch.setattr("django_audit.db.hook.process_model_hook", fake_hook)

    t = TestModel.objects.create(name="to_delete", value=3)
    pk = t.pk
    t.delete()

    assert StoreAudit.objects.filter(model_name="TestModel", instance_id=str(pk)).exists() or StoreAudit.objects.filter(model_name="TestModel", instance_id=pk).exists()
    assert any(a == "Удаление" or a == "Deletion" or a == "deleted" for a in hook_calls)

