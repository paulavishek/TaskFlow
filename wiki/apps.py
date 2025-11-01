from django.apps import AppConfig


class WikiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wiki'
    verbose_name = 'Wiki & Knowledge Base'
    
    def ready(self):
        """Perform app initialization"""
        import wiki.signals  # noqa
