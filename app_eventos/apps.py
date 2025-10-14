from django.apps import AppConfig

class AppEventosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_eventos"

    def ready(self):
        import app_eventos.signals
        import app_eventos.signals_notificacoes
        import app_eventos.signals_documentos  # Signals do sistema de documentos

