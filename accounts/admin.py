from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import KYCSubmission, User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Marketplace info", {"fields": ("role", "phone", "kyc_status")}),
    )
    list_display = ("username", "email", "role", "kyc_status", "is_staff")


admin.site.register(User, CustomUserAdmin)


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "id_type", "status", "submitted_at", "reviewed_by")
    list_filter = ("status", "id_type")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("submitted_at",)
    actions = ["approve_submissions", "reject_submissions"]

    @admin.action(description="Approve selected KYC submissions")
    def approve_submissions(self, request, queryset):
        updated = 0
        for submission in queryset:
            submission.status = KYCSubmission.Status.VERIFIED
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.save(update_fields=["status", "reviewed_by", "reviewed_at"])

            submission.user.kyc_status = User.KYCStatus.VERIFIED
            submission.user.save(update_fields=["kyc_status"])
            updated += 1
        self.message_user(request, f"{updated} submission(s) approved.")

    @admin.action(description="Reject selected KYC submissions")
    def reject_submissions(self, request, queryset):
        updated = 0
        for submission in queryset:
            submission.status = KYCSubmission.Status.REJECTED
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.save(update_fields=["status", "reviewed_by", "reviewed_at"])

            submission.user.kyc_status = User.KYCStatus.REJECTED
            submission.user.save(update_fields=["kyc_status"])
            updated += 1
        self.message_user(request, f"{updated} submission(s) rejected.")
