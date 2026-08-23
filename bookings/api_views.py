from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Booking, BookingStateError
from .permissions import require_lender
from .serializers import BookingCreateSerializer, BookingSerializer
from .utils import OverlapError, create_booking_request, transition_booking


def error_response(code: str, message: str, http_status):
    """Consistent mobile error envelope across all endpoints in this app."""
    return Response({"error": {"code": code, "message": message}}, status=http_status)


class BookingCreateAPIView(APIView):
    """POST /api/bookings/create/"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = get_object_or_404(Product, pk=data["product_id"], available=True)

        try:
            booking = create_booking_request(
                product=product,
                renter=request.user,
                start_date=data["start_date"],
                end_date=data["end_date"],
            )
        except OverlapError as exc:
            return error_response("DATE_CONFLICT", str(exc), status.HTTP_409_CONFLICT)
        except ValueError as exc:
            return error_response("INVALID_REQUEST", str(exc), status.HTTP_400_BAD_REQUEST)

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class BookingDetailAPIView(APIView):
    """GET /api/bookings/<id>/ — used for polling fallback when a push/WS is missed."""

    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, public_id=booking_id)
        if request.user.id not in (booking.renter_id, booking.lender_id):
            raise PermissionDenied("Not a participant in this booking.")

        from bookings.utils import check_and_expire_booking
        check_and_expire_booking(booking)

        return Response(BookingSerializer(booking).data)


class BookingAcceptAPIView(APIView):
    """POST /api/bookings/<id>/accept/ — lender only."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, public_id=booking_id)
        require_lender(booking, request.user)
        try:
            with transaction.atomic():
                booking = transition_booking(
                    booking_id=booking.pk, new_status=Booking.Status.APPROVED, actor=request.user
                )
        except BookingStateError as exc:
            return error_response("INVALID_TRANSITION", str(exc), status.HTTP_409_CONFLICT)
        return Response(BookingSerializer(booking).data)


class BookingRejectAPIView(APIView):
    """POST /api/bookings/<id>/reject/ — lender only."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, public_id=booking_id)
        require_lender(booking, request.user)
        try:
            with transaction.atomic():
                booking = transition_booking(
                    booking_id=booking.pk, new_status=Booking.Status.REJECTED, actor=request.user
                )
        except BookingStateError as exc:
            return error_response("INVALID_TRANSITION", str(exc), status.HTTP_409_CONFLICT)
        return Response(BookingSerializer(booking).data)


class BookingHandoverAPIView(APIView):
    """POST /api/bookings/<id>/handover/ — lender only. PAID -> ACTIVE."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, public_id=booking_id)
        require_lender(booking, request.user)
        try:
            with transaction.atomic():
                booking = transition_booking(
                    booking_id=booking.pk, new_status=Booking.Status.ACTIVE, actor=request.user
                )
                Product.objects.filter(pk=booking.product_id).update(available=False)
        except BookingStateError as exc:
            return error_response("INVALID_TRANSITION", str(exc), status.HTTP_409_CONFLICT)
        return Response(BookingSerializer(booking).data)


class BookingReturnAPIView(APIView):
    """POST /api/bookings/<id>/return/ — lender only. ACTIVE -> COMPLETED + escrow refund."""

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        from payments.services import EscrowService, EscrowError

        booking = get_object_or_404(Booking, public_id=booking_id)
        require_lender(booking, request.user)
        try:
            with transaction.atomic():
                booking = transition_booking(
                    booking_id=booking.pk, new_status=Booking.Status.COMPLETED, actor=request.user
                )
                Product.objects.filter(pk=booking.product_id).update(available=True)
                EscrowService.release_deposit(booking_id=booking.pk, released_by=request.user)
        except BookingStateError as exc:
            return error_response("INVALID_TRANSITION", str(exc), status.HTTP_409_CONFLICT)
        except EscrowError as exc:
            return error_response("ESCROW_ERROR", str(exc), status.HTTP_409_CONFLICT)
        return Response(BookingSerializer(booking).data)
