import logging
import os
import random
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class SendOTPResult:
    success: bool
    reference_id: str = ""
    error: str = ""

@dataclass
class VerifyOTPResult:
    success: bool
    name: Optional[str] = None  
    error: str = ""

class AadhaarOTPProvider:
    def send_otp(self, aadhaar_number: str) -> SendOTPResult:
        raise NotImplementedError

    def verify_otp(self, reference_id: str, otp: str) -> VerifyOTPResult:
        raise NotImplementedError

class MockAadhaarOTPProvider(AadhaarOTPProvider):
    """
    Local-dev stand-in. No real OTP is sent anywhere — it's logged so you
    can see it while testing. Use OTP "123456" to simulate success, any
    other 6-digit value to simulate a wrong-OTP failure.
    """

    def send_otp(self, aadhaar_number: str) -> SendOTPResult:
        if len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
            return SendOTPResult(success=False, error="Invalid Aadhaar number format.")

        reference_id = f"MOCK-{int(time.time())}-{random.randint(1000, 9999)}"
        logger.info(
            "MOCK Aadhaar OTP: pretending to text an OTP for reference %s "
            "(use 123456 to simulate success in dev)",
            reference_id,
        )
        return SendOTPResult(success=True, reference_id=reference_id)

    def verify_otp(self, reference_id: str, otp: str) -> VerifyOTPResult:
        if otp == "123456":
            return VerifyOTPResult(success=True, name="Test User")
        return VerifyOTPResult(success=False, error="Incorrect OTP.")


class RealAadhaarOTPProvider(AadhaarOTPProvider):
    """
    Fill this in once you've signed up with a licensed KYC provider
    (Digio, Signzy, Cashfree Verification, HyperVerge, IDfy, Karza, etc).
    Read their API docs for the actual endpoint, auth, and payload shape —
    this is a skeleton showing where that logic goes, not real code.
    """

    def __init__(self):
        self.api_key = os.environ.get("KYC_PROVIDER_API_KEY")
        self.base_url = os.environ.get("KYC_PROVIDER_BASE_URL")
        if not self.api_key or not self.base_url:
            raise RuntimeError(
                "Set KYC_PROVIDER_API_KEY and KYC_PROVIDER_BASE_URL to use "
                "the real Aadhaar OTP provider."
            )

    def send_otp(self, aadhaar_number: str) -> SendOTPResult:
        # Example shape only — replace with your provider's actual request:
        #
        # import requests
        # resp = requests.post(
        #     f"{self.base_url}/aadhaar/otp/send",
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     json={"aadhaar_number": aadhaar_number},
        #     timeout=10,
        # )
        # data = resp.json()
        # return SendOTPResult(success=data["success"], reference_id=data.get("ref_id", ""))
        raise NotImplementedError("Wire this up to your chosen KYC provider's send-OTP endpoint.")

    def verify_otp(self, reference_id: str, otp: str) -> VerifyOTPResult:
        # Example shape only — replace with your provider's actual request:
        #
        # import requests
        # resp = requests.post(
        #     f"{self.base_url}/aadhaar/otp/verify",
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     json={"ref_id": reference_id, "otp": otp},
        #     timeout=10,
        # )
        # data = resp.json()
        # return VerifyOTPResult(success=data["success"], name=data.get("name"))
        raise NotImplementedError("Wire this up to your chosen KYC provider's verify-OTP endpoint.")


def get_aadhaar_otp_provider() -> AadhaarOTPProvider:
    if os.environ.get("USE_REAL_KYC_PROVIDER") == "True":
        return RealAadhaarOTPProvider()

    return MockAadhaarOTPProvider()
