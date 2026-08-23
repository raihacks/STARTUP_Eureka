from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:product_id>/', views.create_booking, name='create_booking'),
path('booking/<int:booking_id>/accept/', views.accept_booking, name='accept_booking'),
path('booking/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
    path('handover/<int:booking_id>/', views.confirm_handover, name='confirm_handover'),
    path('return/<int:booking_id>/', views.confirm_return, name='confirm_return'),
]