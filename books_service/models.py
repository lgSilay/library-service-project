import os
import uuid
from django.utils.text import slugify
from typing import Union

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


def image_file_path(instance: Union["Book", "Author"], filename: str) -> str:
    _, extension = os.path.splitext(filename)
    filename = ""
    if isinstance(instance, Book):
        filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"
    if isinstance(instance, Author):
        filename = f"{slugify(instance.full_name)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/books_service/", filename)


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    author_profile_image = models.ImageField(
        upload_to=image_file_path,
        null=True,
        blank=True,
        default=None,
    )
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Subscription",
        related_name="subscribers"
    )

    class Meta:
        unique_together = ("first_name", "last_name")
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Subscription(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription_started = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return (
            f"{self.user} subscribed to "
            f"{self.author.full_name} since "
            f"{self.subscription_started}"
        )


class Book(models.Model):
    COVER_CHOICES = (
        ("hard", "Hard"),
        ("soft", "Soft"),
    )
    title = models.CharField(max_length=255)
    title_image = models.ImageField(
        upload_to=image_file_path,
        null=True,
        blank=True,
        default=None,
    )
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
