# api_desktop/apps.py
from django.apps import AppConfig


class ApiDesktopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_desktop'
    verbose_name = 'API Desktop'
