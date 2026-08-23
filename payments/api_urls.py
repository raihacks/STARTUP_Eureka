from django.urls import path

from . import api_views

app_name = "payments_api"

urlpatterns = [
    path("<uuid:booking_id>/pay/", api_views.PayBookingAPIView.as_view(), name="pay"),
    path("wallet/", api_views.WalletMeAPIView.as_view(), name="wallet"),
    path("webhook/gateway/", api_views.gateway_webhook, name="gateway_webhook"),
]
