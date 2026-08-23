from django.contrib import admin

from .models import Payment, Wallet, WalletTransaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "renter", "lender", "total_paid", "status", "deposit_status")
    list_filter = ("status", "deposit_status")
    search_fields = ("gateway_payment_id", "idempotency_key", "renter__username", "lender__username")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")
    search_fields = ("user__username",)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "kind", "amount", "balance_after", "created_at")
    list_filter = ("kind",)
