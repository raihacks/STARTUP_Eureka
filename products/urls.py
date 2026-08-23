from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.products_page,
        name="products_page"
    ),

    path(
        "add/",
        views.add_product,
        name="add_product"
    ),

    path(
        "edit/<int:product_id>/",
        views.edit_product,
        name="edit_product"
    ),

    path(
        "view/<int:product_id>/",
        views.view_product,
        name="view_product"
    ),
    
    path('lender/products/', views.lender_products, name='lender_products'),
    
    # Customer Routes
    path('catalog/', views.customer_catalog, name='customer_catalog')

]




