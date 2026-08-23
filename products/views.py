from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm
from bookings.models import Booking
from bookings.utils import check_and_expire_booking

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
def lender_products(request):
    # 1. Fetch all products owned by the logged-in user ("demo")
    user_products = Product.objects.filter(owner=request.user)
    
    # 2. Query bookings whose product belongs to the user's products
    lender_bookings = Booking.objects.filter(
        product__in=user_products
    ).select_related('renter', 'product').order_by('-created_at')

    context = {
        'products': user_products,
        'lender_bookings': lender_bookings,
    }
    return render(request, 'products/product.html', context)
@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, product__lender=request.user)
    booking.status = 'APPROVED'
    booking.save()
    return redirect('lender_dashboard')

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, product__lender=request.user)
    booking.status = 'REJECTED'
    booking.save()
    return redirect('lender_dashboard')

@login_required
def confirm_handover(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, product__lender=request.user)
    booking.status = 'ACTIVE'
    booking.save()
    return redirect('lender_dashboard')

@login_required
def confirm_return(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, product__lender=request.user)
    booking.status = 'COMPLETED'
    booking.save()
    return redirect('lender_dashboard')
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
    
    


def customer_catalog(request):
    products = Product.objects.filter(available=True)
    
    # CRITICAL: Only query user bookings/profile if the user is logged in
    user_bookings = []
    if request.user.is_authenticated:
        user_bookings = Booking.objects.filter(
        renter=request.user
        ).select_related('product', 'lender').order_by('-created_at')
        for booking in user_bookings:
            check_and_expire_booking(booking)
        context = {
            'products': products,
            'user_bookings': user_bookings,
        }

        
        # If you have a Customer/Profile model lookup, wrap it here too:
        # customer_profile = Customer.objects.get(user=request.user)

    context = {
        'products': products,
        'user_bookings': user_bookings,
    }
    return render(request, 'customer_catalog.html', context)


