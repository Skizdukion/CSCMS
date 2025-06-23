from django.apps import AppConfig

class StoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' # type: ignore[attr-defined]
    name = 'backend.apps.stores'
    verbose_name = 'Convenience Stores' 