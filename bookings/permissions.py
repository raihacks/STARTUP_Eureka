from django.core.exceptions import PermissionDenied


def require_lender(booking, user):
    """Only the product owner (lender) may accept/reject/handover/return."""
    if booking.lender_id != user.id and booking.product.owner_id != user.id:
        raise PermissionDenied("Only the lender for this listing can perform this action.")


def require_renter(booking, user):
    """Only the renter may pay / cancel their own request."""
    if booking.renter_id != user.id:
        raise PermissionDenied("Only the renter on this booking can perform this action.")
