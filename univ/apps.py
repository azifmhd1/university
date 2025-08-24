from django.apps import AppConfig

class UnivConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'univ'

    def ready(self):
        import univ.signals  # ✅ ensures signals.py is loaded
