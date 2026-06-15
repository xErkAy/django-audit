from __future__ import annotations

import json
from typing import Iterable

from django.contrib.auth.base_user import AbstractBaseUser as DjangoAbstractBaseUser
from django.db import models, transaction
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Field

from django_audit.db import hook
from django_audit.constants import ChangeStatus
from django_audit.context import get_current_user
from django_audit.db.models.manager import CustomObjectManager


class BaseModel(models.Model):
    """
    Abstract base model with change tracking for creation, update, and deletion.
    """

    objects = CustomObjectManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_state = self._as_dict()

    def _as_dict(self) -> dict:
        """
        Returns a dictionary {field_name: value} for all model fields.
        Converts complex fields (ForeignKey, JSONField) to serializable values.
        """
        data = {}
        for field in self._meta.get_fields():
            if field.many_to_many:
                data[field.name] = list(getattr(self, field.name).values_list("pk", flat=True))
            elif field.one_to_many:
                continue
            elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
                related_obj = getattr(self, field.name)
                data[field.name] = related_obj.pk if related_obj else None
            else:
                value = getattr(self, field.name)
                try:
                    json.dumps(value, cls=DjangoJSONEncoder)
                    data[field.name] = value
                except TypeError:
                    data[field.name] = str(value)
        return data

    def _get_model_difference(self, old_instance: dict, new_instance: dict, fields: Iterable = None) -> dict:
        """
        Compares old and new state and returns differences.
        Format:
            {field_verbose_name: [old_value, new_value]}
        """

        def find_field_by_name(field_name: str) -> Field:
            for _field in self._meta.fields:
                if _field.name == field_name:
                    return _field

        if fields is None:
            fields = self._meta.fields

        diff = {}
        for field in fields:
            _field = find_field_by_name(field) if not hasattr(field, "name") else field
            old_value = old_instance.get(_field.name)
            new_value = new_instance.get(_field.name)
            if old_value != new_value:
                diff[_field.verbose_name] = [old_value, new_value]

        return diff

    # @staticmethod
    # def send_changes(*, user: str, model_name: str, instance_id: int, action: str, changes: dict | None = None):
    #     """
    #     Hook for sending or logging changes.
    #
    #     Args:
    #         user: Current user making the change.
    #         model_name: Name of the model.
    #         instance_id: ID of the affected instance.
    #         action: Action type (created, changed, deleted).
    #         changes: Dict of field changes.
    #     """
    #     print(user, model_name, instance_id, action, changes or {})

    def save(self, *args, **kwargs) -> None:
        """
        Overrides save to track creation and updates.
        """
        try:
            with transaction.atomic():
                old_instance = getattr(self, "_original_state", {})
                super().save(*args, **kwargs)
                new_instance = self._as_dict()

                is_created = old_instance.get("id") is None
                if is_created:
                    changes = {}
                else:
                    changes = self._get_model_difference(old_instance, new_instance)

                from django_audit.db.models.store import StoreAudit

                data = {
                    "user": get_current_user(),
                    "model_name": self.__class__.__name__,
                    "instance_id": new_instance.get("id"),
                    "action": ChangeStatus.created if is_created else ChangeStatus.updated,
                    "changes": changes,
                }
                obj = StoreAudit.objects.create(**data)
                hook.process_model_hook(obj=obj, **data)

                # Update the original state after saving
                self._original_state = new_instance
        except:
            raise

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """
        Overrides delete to track deletion.
        """
        try:
            with transaction.atomic():
                result = super().delete(*args, **kwargs)
                from django_audit.db.models.store import StoreAudit

                data = {
                    "user": get_current_user(),
                    "model_name": self.__class__.__name__,
                    "instance_id": self._original_state.get("id"),
                    "action": ChangeStatus.deleted,
                }
                obj = StoreAudit.objects.create(**data)
                hook.process_model_hook(obj=obj, **data)
                return result
        except:
            raise


class AbstractBaseUser(DjangoAbstractBaseUser, BaseModel):
    """
    Abstract base user that inherits BaseModel for change tracking.
    """

    class Meta:
        abstract = True
