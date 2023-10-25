from django.db import models
from django.core.exceptions import ValidationError


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    COVER_CHOICES = (
        ("hard", "Hard"),
        ("soft", "Soft"),
    )
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="books"
    )
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("title", "author", "cover")
        ordering = ["title"]

    @staticmethod
    def validate_inventory_field(
        value: int, error_to_raise: Exception
    ) -> None:
        if value < 0:
            raise error_to_raise(
                {"inventory": ["Inventory cannot be negative"]}
            )

    def clean(self):
        self.validate_inventory_field(self.inventory, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"'{self.title}' written by {self.author}"
