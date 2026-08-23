from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for the rental marketplace.
    Extends Django's built-in user with role and KYC fields.
    """

    class Role(models.TextChoices):
        RENTER = "RENTER", "Renter"
        LENDER = "LENDER", "Lender"

    class KYCStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.RENTER,
    )
    phone = models.CharField(max_length=15, blank=True)
    kyc_status = models.CharField(
        max_length=10,
        choices=KYCStatus.choices,
        default=KYCStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class KYCSubmission(models.Model):
    """
    A single KYC submission attempt. A user can resubmit if rejected,
    so this keeps a history rather than overwriting in place.

    Security note: we deliberately do NOT store the full ID number, only
    the last 4 digits, so this table stays low-risk even if the DB is
    ever exposed. Do not add a full-number field here — if you need real
    identity verification, integrate a licensed KYC provider (e.g. via
    their hosted flow/API) instead of collecting raw documents yourself.
    """

    class IDType(models.TextChoices):
        AADHAAR = "AADHAAR", "Aadhaar"
        PAN = "PAN", "PAN Card"
        PASSPORT = "PASSPORT", "Passport"
        DRIVING_LICENSE = "DL", "Driving License"

    class Method(models.TextChoices):
        DOCUMENT = "DOCUMENT", "Document upload"
        AADHAAR_OTP = "AADHAAR_OTP", "Aadhaar OTP"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="kyc_submissions",
    )
    method = models.CharField(
        max_length=15,
        choices=Method.choices,
        default=Method.DOCUMENT,
    )
    id_type = models.CharField(max_length=10, choices=IDType.choices)
    id_last4 = models.CharField(
        max_length=4,
        help_text="Last 4 characters/digits of the ID number only. Never store the full number.",
    )
    document = models.FileField(
        upload_to="kyc/%Y/%m/",
        blank=True,
        null=True,
        help_text="Required for document-upload submissions. Not used for Aadhaar OTP.",
    )
    provider_reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="The KYC provider's transaction/reference ID for an Aadhaar OTP attempt (audit trail only).",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    rejection_reason = models.CharField(max_length=255, blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kyc_reviews",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.method == self.Method.DOCUMENT and not self.document:
            raise ValidationError("A document is required for document-upload KYC.")

    def __str__(self):
        return f"KYC for {self.user.username} ({self.status})"
