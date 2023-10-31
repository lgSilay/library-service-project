from django.apps import AppConfig


class BooksServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "books_service"

    def ready(self) -> None:
        from books_service import signals
