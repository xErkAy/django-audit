from __future__ import annotations

from django.db import transaction
from django.db.models import QuerySet as DjangoQuerySet

from django_audit.db.models.store import StoreAudit
from django_audit.db import hook
from django_audit.db.models.base import BaseModel
from django_audit.constants import ChangeStatus
from django_audit.context import get_current_user


class QuerySet(DjangoQuerySet):
    """Custom QuerySet that tracks creation and bulk creation."""

    def bulk_create(self, objs, **kwargs) -> list[BaseModel]:
        try:
            with transaction.atomic():
                result = super().bulk_create(objs, **kwargs)
                for obj in objs:
                    obj.send_changes(
                        user=get_current_user(),
                        model_name=obj.__class__.__name__,
                        instance_id=str(obj.id),
                        action=ChangeStatus.created,
                    )
                return result
        except:
            raise

    def bulk_update(self, objs, fields, **kwargs) -> int:
        """
        Overrides bulk_update to track changes for the specified fields.

        Args:
            objs: list of model instances to update
            fields: list of field names to update
        """
        try:
            with transaction.atomic():
                object_ids = [i.id for i in objs]
                old_states = list(self.filter(id__in=object_ids).values(*fields))

                result = super().bulk_update(objs, fields, **kwargs)

                for obj, old_state in zip(objs, old_states):
                    changes = obj._get_model_difference(old_state, obj._as_dict(), fields=fields)
                    if changes:
                        obj.send_changes(
                            user=get_current_user(),
                            model_name=obj.__class__.__name__,
                            instance_id=str(obj.id),
                            action=ChangeStatus.updated,
                            changes=changes,
                        )

                return result
        except:
            raise

    def delete(self) -> tuple[int, dict[str, int]]:
        try:
            with transaction.atomic():
                if len(self):
                    model_name = self[0].__class__.__name__

                objs = [i.id for i in self]
                result = super().delete()

                for obj in objs:
                    data = {
                        "user": get_current_user(),
                        "model_name": model_name,
                        "instance_id": obj,
                        "action": ChangeStatus.deleted,
                    }
                    obj = StoreAudit.objects.create(**data)
                    hook.process_model_hook(obj=obj, **data)

                return result
        except:
            raise



