from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Product
from .forms import ProductForm


@login_required
def products_page(request):

    products = Product.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(
        request,
        "products/product.html",
        {
            "products": products
        }
    )


@login_required
def add_product(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            product = form.save(commit=False)

            # VERY IMPORTANT
            # The user cannot choose the owner.
            # Django gets it from the logged-in account.

            product.owner = request.user

            product.save()

            return redirect("products_page")

    else:

        form = ProductForm()

    products = Product.objects.filter(
        owner=request.user
    )

    return render(
        request,
        "products/product.html",
        {
            "form": form,
            "products": products
        }
    )


@login_required
def edit_product(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        owner=request.user
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():

            form.save()

            return redirect("products_page")

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "products/product.html",
        {
            "form": form,
            "products": Product.objects.filter(
                owner=request.user
            ),
            "editing_product": product
        }
    )


@login_required
def view_product(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    return render(
        request,
        "products/product.html",
        {
            "products": Product.objects.filter(
                owner=request.user
            ),
            "selected_product": product
        }
    )