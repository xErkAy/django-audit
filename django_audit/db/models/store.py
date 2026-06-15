from django.db import models


class StoreAudit(models.Model):
    # allow user to be null for system actions or when no user is present
    user = models.CharField(verbose_name="User", max_length=255, null=True, blank=True)
    model_name = models.CharField(verbose_name="Model name", max_length=255)
    instance_id = models.IntegerField(verbose_name="Instance ID")
    action = models.CharField(verbose_name="Action", max_length=255)
    changes = models.JSONField(verbose_name="Changes", default=dict)
    created_at = models.DateTimeField(verbose_name="Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Store Audit"
        verbose_name_plural = "Store Audit"
