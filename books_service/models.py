from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self) -> str:
        return str(self)

    @property
    def count_books(self) -> int:
        return Book.objects.filter(author=self).count()

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
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("title", "author", "cover")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"'{self.title}' written by {self.author}"
