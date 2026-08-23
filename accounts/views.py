from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .forms import AadhaarNumberForm, AadhaarOTPVerifyForm, KYCSubmissionForm, RegisterForm
from .models import KYCSubmission, User
from .services import get_aadhaar_otp_provider


class RegisterView(CreateView):
    """Handles new user sign-up and logs the user in immediately after."""

    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CustomLoginView(LoginView):
    """Handles login with a custom template."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def dashboard(request):
    """Simple placeholder landing page after login/registration."""
    return render(request, "accounts/dashboard.html", {"user": request.user})


@login_required
def kyc_submit(request):
    """
    Lets a user upload KYC documents.

    - Verified: read-only status, no form.
    - A submission already under review: read-only "pending" status, no form
      (prevents spamming new submissions while one is being reviewed).
    - Never submitted, or last submission was rejected: shows the form.
    """
    latest = request.user.kyc_submissions.first()
    under_review = latest is not None and latest.status == KYCSubmission.Status.PENDING
    can_submit = request.user.kyc_status != User.KYCStatus.VERIFIED and not under_review

    if request.method == "POST":
        if not can_submit:
            # Nothing to do - either verified already or a review is in flight.
            return redirect("accounts:kyc_submit")

        form = KYCSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()

            request.user.kyc_status = User.KYCStatus.PENDING
            request.user.save(update_fields=["kyc_status"])

            messages.success(request, "KYC documents submitted. We'll review them shortly.")
            return redirect("accounts:dashboard")
    else:
        form = KYCSubmissionForm() if can_submit else None

    return render(
        request,
        "accounts/kyc.html",
        {"form": form, "latest": latest, "can_submit": can_submit, "under_review": under_review},
    )


SESSION_KEY_AADHAAR_REF = "aadhaar_otp_reference_id"
SESSION_KEY_AADHAAR_LAST4 = "aadhaar_otp_last4"


@login_required
def aadhaar_otp_request(request):
    """
    Step 1 of Aadhaar eKYC: collect the Aadhaar number and ask the
    provider to send an OTP. The full number is used only for this one
    call and is never saved anywhere.
    """
    latest = request.user.kyc_submissions.first()
    under_review = latest is not None and latest.status == KYCSubmission.Status.PENDING
    can_submit = request.user.kyc_status != User.KYCStatus.VERIFIED and not under_review

    if not can_submit:
        return redirect("accounts:kyc_submit")

    if request.method == "POST":
        form = AadhaarNumberForm(request.POST)
        if form.is_valid():
            aadhaar_number = form.cleaned_data["aadhaar_number"]
            provider = get_aadhaar_otp_provider()
            result = provider.send_otp(aadhaar_number)

            if result.success:
                request.session[SESSION_KEY_AADHAAR_REF] = result.reference_id
                request.session[SESSION_KEY_AADHAAR_LAST4] = aadhaar_number[-4:]
                messages.success(request, "OTP sent to your Aadhaar-linked mobile number.")
                return redirect("accounts:aadhaar_otp_verify")

            form.add_error(None, result.error or "Could not send OTP. Please try again.")
    else:
        form = AadhaarNumberForm()

    return render(request, "accounts/aadhaar_request.html", {"form": form})


@login_required
def aadhaar_otp_verify(request):
    """Step 2 of Aadhaar eKYC: verify the OTP the user received."""
    reference_id = request.session.get(SESSION_KEY_AADHAAR_REF)
    last4 = request.session.get(SESSION_KEY_AADHAAR_LAST4)

    if not reference_id:
        messages.error(request, "Please request an OTP first.")
        return redirect("accounts:aadhaar_otp_request")

    if request.method == "POST":
        form = AadhaarOTPVerifyForm(request.POST)
        if form.is_valid():
            provider = get_aadhaar_otp_provider()
            result = provider.verify_otp(reference_id, form.cleaned_data["otp"])

            if result.success:
                KYCSubmission.objects.create(
                    user=request.user,
                    method=KYCSubmission.Method.AADHAAR_OTP,
                    id_type=KYCSubmission.IDType.AADHAAR,
                    id_last4=last4,
                    provider_reference_id=reference_id,
                    status=KYCSubmission.Status.VERIFIED,
                    reviewed_at=timezone.now(),
                )
                request.user.kyc_status = User.KYCStatus.VERIFIED
                request.user.save(update_fields=["kyc_status"])

                # Clear the one-time session data now that verification is done.
                request.session.pop(SESSION_KEY_AADHAAR_REF, None)
                request.session.pop(SESSION_KEY_AADHAAR_LAST4, None)

                messages.success(request, "Aadhaar verified successfully.")
                return redirect("accounts:dashboard")

            form.add_error(None, result.error or "OTP verification failed. Please try again.")
    else:
        form = AadhaarOTPVerifyForm()

    return render(request, "accounts/aadhaar_verify.html", {"form": form, "last4": last4})
