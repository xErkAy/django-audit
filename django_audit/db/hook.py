from django_audit.db.models.store import StoreAudit


def process_model_hook(*, obj: StoreAudit, user: str, model_name: str, instance_id: int, action: str, changes: dict | None = None):
    """
    Hook for sending or logging changes.

    Args:
        :param obj: StoreAudit object
        :param user: Current user making the change.
        :param model_name: Name of the model.
        :param instance_id: ID of the affected instance.
        :param action: Action type (created, changed, deleted).
        :param changes: Dict of field changes.
    """
    print(obj, user, model_name, instance_id, action, changes)