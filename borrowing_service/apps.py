from django.apps import AppConfig


class BorrowingServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowing_service"

    def ready(self) -> None:
        import borrowing_service.handlers
