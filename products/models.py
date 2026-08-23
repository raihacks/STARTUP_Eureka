from django.db import models
from django.conf import settings


class Product(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)

    category = models.CharField(max_length=100)

    description = models.TextField()

    rental_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    location = models.CharField(max_length=200)

    condition = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
