"""
App configuration for the newsApp app.

Configures the application and ensures that signal handlers are
loaded when the app is ready.
"""

from django.apps import AppConfig


class NewsappConfig(AppConfig):
    """
    Configuration for the newsApp application.

    Attributes:
        default_auto_field (str): Specifies the type of auto-incrementing
        primary key to use.
        name (str): The name of the application.

    Methods:
        ready:
            Imports the signals module to ensure that signal handlers are
            registered.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "newsApp"

    def ready(self):
        # Import signals so that they are registered
        import newsApp.signals  # noqa: F401
