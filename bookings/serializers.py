from rest_framework import serializers

from .models import Booking


class BookingCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data["end_date"] < data["start_date"]:
            raise serializers.ValidationError("end_date cannot be before start_date.")
        return data


class BookingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    renter_id = serializers.IntegerField(read_only=True)
    lender_id = serializers.IntegerField(read_only=True)
    duration_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "product_id",
            "product_name",
            "renter_id",
            "lender_id",
            "start_date",
            "end_date",
            "duration_days",
            "rental_price",
            "deposit_amount",
            "total_price",
            "status",
            "approval_expires_at",
            "handed_over_at",
            "returned_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
