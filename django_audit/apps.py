from django.apps import AppConfig
from django.conf import settings


class DjangoAuditConfig(AppConfig):
    name = "django_audit"
    verbose_name = "Django Audit Framework"

    def ready(self):
        from django_audit.exceptions import NoTokenFoundException
        
        settings.MIDDLEWARE.append("django_audit.middlewares.CurrentUserMiddleware")
        #     if not getattr(settings, "MY_LIBRARY_TOKEN", None):
        #         raise NoTokenFoundException("MY_LIBRARY_TOKEN must be set in settings")