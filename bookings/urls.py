from django.urls import path

from . import views

urlpatterns = [
    path("create/<int:product_id>/", views.create_booking, name="create_booking"),
    path("<int:booking_id>/accept/", views.accept_booking, name="accept_booking"),
    path("<int:booking_id>/reject/", views.reject_booking, name="reject_booking"),
    path("<int:booking_id>/handover/", views.confirm_handover, name="confirm_handover"),
    path("<int:booking_id>/return/", views.confirm_return, name="confirm_return"),
]
