"""
Thin adapter boundary around whichever payment gateway you integrate
(Razorpay, Stripe, PayU, etc). Keeping this isolated means EscrowService
never depends on a specific SDK — swap the implementation here only.
"""

import hashlib
import hmac
from decimal import Decimal

from django.conf import settings


class GatewayError(Exception):
    pass


class GatewayClient:
    @staticmethod
    def create_order(*, amount: Decimal, currency: str, receipt: str) -> dict:
        """
        Called when the mobile app opens the payment sheet, BEFORE the user
        pays — creates a gateway order and returns its id + a short-lived
        client token/key for the mobile SDK to render the checkout UI.

        Example (Razorpay):
            client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
            order = client.order.create({
                "amount": int(amount * 100),  # paise
                "currency": currency,
                "receipt": receipt,
            })
            return {"order_id": order["id"], "key": KEY_ID, "amount": order["amount"]}
        """
        raise NotImplementedError("Wire up your gateway SDK's order-create call here.")

    @staticmethod
    def verify_payment(*, gateway_payment_id: str, signature: str, expected_amount: Decimal, raw_payload: dict):
        """
        Verifies the webhook/callback signature and that the amount charged
        matches what we quoted, so a tampered client can't under-pay.

        Example (Razorpay HMAC-SHA256 signature check):
            generated = hmac.new(
                key=settings.RAZORPAY_KEY_SECRET.encode(),
                msg=f"{raw_payload['order_id']}|{gateway_payment_id}".encode(),
                digestmod=hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(generated, signature):
                raise GatewayError("Signature mismatch")
        """
        secret = getattr(settings, "PAYMENT_GATEWAY_WEBHOOK_SECRET", None)
        if not secret:
            # Development fallback — DO NOT ship to production without a
            # real signature check wired up above.
            return True

        order_id = raw_payload.get("order_id", "")
        generated = hmac.new(
            key=secret.encode(),
            msg=f"{order_id}|{gateway_payment_id}".encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(generated, signature or ""):
            raise GatewayError("Payment signature verification failed.")

        charged_amount = Decimal(str(raw_payload.get("amount", "0")))
        if charged_amount != expected_amount:
            raise GatewayError(
                f"Charged amount {charged_amount} does not match quoted total {expected_amount}."
            )
        return True
