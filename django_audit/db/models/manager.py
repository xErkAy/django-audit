from django.db import models


class CustomObjectManager(models.Manager):
    """Custom Manager that uses modified QuerySet."""

    def get_queryset(self):
        from django_audit.db.models import QuerySet

        return QuerySet(self.model, using=self._db)
