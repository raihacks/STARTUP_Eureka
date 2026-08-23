from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            "name",
            "category",
            "description",
            "rental_price",
            "security_deposit",
            "location",
            "condition",
            "image",
        ]