from django.urls import path

from . import api_views

app_name = "bookings_api"

urlpatterns = [
    path("create/", api_views.BookingCreateAPIView.as_view(), name="create"),
    path("<uuid:booking_id>/", api_views.BookingDetailAPIView.as_view(), name="detail"),
    path("<uuid:booking_id>/accept/", api_views.BookingAcceptAPIView.as_view(), name="accept"),
    path("<uuid:booking_id>/reject/", api_views.BookingRejectAPIView.as_view(), name="reject"),
    path("<uuid:booking_id>/handover/", api_views.BookingHandoverAPIView.as_view(), name="handover"),
    path("<uuid:booking_id>/return/", api_views.BookingReturnAPIView.as_view(), name="return"),
]
