import json
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking

from .gateway import GatewayError
from .models import Wallet
from .serializers import PayBookingSerializer, PaymentSerializer, WalletSerializer
from .services import EscrowError, EscrowService

logger = logging.getLogger(__name__)


def error_response(code: str, message: str, http_status):
    return Response({"error": {"code": code, "message": message}}, status=http_status)


class PayBookingAPIView(APIView):
    """
    POST /api/payments/<booking_id>/pay/

    Body:
    {
        "idempotency_key": "client-generated-uuid",
        "gateway_payment_id": "pay_xxx",
        "gateway_signature": "hex...",
        "raw_payload": {"order_id": "order_xxx", "amount": "2500.00"}
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, public_id=booking_id)

        serializer = PayBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            payment = EscrowService.process_payment(
                booking_id=booking.pk,
                payer=request.user,
                idempotency_key=data["idempotency_key"],
                gateway_payment_id=data["gateway_payment_id"],
                gateway_signature=data.get("gateway_signature", ""),
                raw_payload=data["raw_payload"],
            )
        except EscrowError as exc:
            return error_response("PAYMENT_FAILED", str(exc), status.HTTP_409_CONFLICT)

        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)


class WalletMeAPIView(APIView):
    """GET /api/payments/wallet/ — current user's spendable balance."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)


@csrf_exempt
def gateway_webhook(request):
    """
    POST /api/payments/webhook/gateway/

    Server-to-server callback from the payment gateway (independent of the
    mobile app round-trip) — the safety net that guarantees a payment gets
    recorded even if the app crashes/loses connectivity right after paying.
    Verifies signature, then delegates to the same idempotent EscrowService
    call, so double-processing is impossible.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    signature = request.headers.get("X-Gateway-Signature", "")
    booking_public_id = payload.get("notes", {}).get("booking_id")
    gateway_payment_id = payload.get("payment_id")
    idempotency_key = payload.get("idempotency_key") or gateway_payment_id

    if not (booking_public_id and gateway_payment_id):
        return HttpResponse(status=400)

    try:
        booking = Booking.objects.get(public_id=booking_public_id)
    except Booking.DoesNotExist:
        logger.warning("Webhook referenced unknown booking %s", booking_public_id)
        return HttpResponse(status=404)

    try:
        EscrowService.process_payment(
            booking_id=booking.pk,
            payer=booking.renter,
            idempotency_key=idempotency_key,
            gateway_payment_id=gateway_payment_id,
            gateway_signature=signature,
            raw_payload=payload,
        )
    except EscrowError as exc:
        logger.warning("Webhook payment processing failed for booking %s: %s", booking.pk, exc)
        # Still 200 so the gateway doesn't hammer us with retries for a
        # permanently-invalid payload; genuine transient failures should be
        # retried via the gateway's own backoff on non-2xx responses instead.
        return HttpResponse(status=200)

    return HttpResponse(status=200)
