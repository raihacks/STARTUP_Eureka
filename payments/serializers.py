from rest_framework import serializers

from .models import Payment, Wallet


class PayBookingSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=100)
    gateway_payment_id = serializers.CharField(max_length=120)
    gateway_signature = serializers.CharField(max_length=255, allow_blank=True, required=False)
    # Raw payload as returned by the gateway SDK on the client, forwarded
    # here for server-side signature + amount verification.
    raw_payload = serializers.DictField()


class PaymentSerializer(serializers.ModelSerializer):
    booking_id = serializers.UUIDField(source="booking.public_id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "booking_id",
            "rental_fee",
            "security_deposit",
            "total_paid",
            "status",
            "deposit_status",
            "gateway_payment_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["balance", "updated_at"]
        read_only_fields = fields
