from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("<int:booking_id>/pay/", views.pay_booking, name="pay_booking"),
]
