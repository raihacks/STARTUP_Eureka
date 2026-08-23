from django.contrib import admin

from .models import Booking, BookingEvent


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "renter", "lender", "status", "start_date", "end_date", "total_price")
    list_filter = ("status",)
    search_fields = ("product__name", "renter__username", "lender__username")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = ("booking", "from_status", "to_status", "actor", "created_at")
    list_filter = ("to_status",)
