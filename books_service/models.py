from django.db import models


class Book(models.Model):
    COVER_CHOICES = (
        ("hard", "Hard"),
        ("soft", "Soft"),
    )
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        "Author", on_delete=models.CASCADE, related_name="books"
    )
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ("title", "author", "cover")
        ordering = ["title"]
