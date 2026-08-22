from django.urls import path
from . import views

app_name = 'payments'  # Optional app namespace

urlpatterns = [
    path('pay/<int:booking_id>/', views.pay_booking, name='pay_booking'),
]