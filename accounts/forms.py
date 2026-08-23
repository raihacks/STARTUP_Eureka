from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import KYCSubmission, User

ALLOWED_DOCUMENT_TYPES = ["image/jpeg", "image/png", "application/pdf"]
MAX_DOCUMENT_SIZE_MB = 5


class RegisterForm(UserCreationForm):
    """Registration form: username, email, phone, password, and role."""

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    role = forms.ChoiceField(choices=User.Role.choices, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "role", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone", "")
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


class KYCSubmissionForm(forms.ModelForm):
    """Form for a user to submit (or resubmit) KYC documents."""

    id_last4 = forms.CharField(
        max_length=4,
        min_length=4,
        label="Last 4 characters of ID number",
        help_text="For your safety, only enter the last 4 characters — never the full number.",
    )

    class Meta:
        model = KYCSubmission
        fields = ["id_type", "id_last4", "document"]

    def clean_document(self):
        document = self.cleaned_data["document"]
        if document.content_type not in ALLOWED_DOCUMENT_TYPES:
            raise forms.ValidationError("Upload a JPEG, PNG, or PDF file.")
        if document.size > MAX_DOCUMENT_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"File must be under {MAX_DOCUMENT_SIZE_MB}MB.")
        return document


class AadhaarNumberForm(forms.Form):
    """Step 1: collect the Aadhaar number to request an OTP for."""

    aadhaar_number = forms.CharField(
        label="Aadhaar number",
        min_length=12,
        max_length=12,
        help_text="12 digits, no spaces. We do not store this number — it's sent "
                   "directly to our verification provider and discarded.",
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
    )

    def clean_aadhaar_number(self):
        value = self.cleaned_data["aadhaar_number"]
        if not value.isdigit():
            raise forms.ValidationError("Aadhaar number must be 12 digits.")
        return value


class AadhaarOTPVerifyForm(forms.Form):
    """Step 2: enter the OTP sent to the Aadhaar-linked mobile number."""

    otp = forms.CharField(
        label="Enter OTP",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "one-time-code"}),
    )

    def clean_otp(self):
        value = self.cleaned_data["otp"]
        if not value.isdigit():
            raise forms.ValidationError("OTP must be 6 digits.")
        return value
