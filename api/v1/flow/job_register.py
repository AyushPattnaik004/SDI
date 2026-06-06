from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from utils.fb_utils import decrypt_request, encrypt_response
from core.keys import PHONE_NUMBER_PRIVATE_KEY
import json

company_registration_router = APIRouter()


@company_registration_router.post("/")
async def register_company(body: dict = Body()):
    encrypted_flow_data_b64 = body["encrypted_flow_data"]
    encrypted_aes_key_b64 = body["encrypted_aes_key"]
    initial_vector_b64 = body["initial_vector"]

    decrypted_data, aes_key, iv = decrypt_request(
        encrypted_flow_data_b64,
        encrypted_aes_key_b64,
        initial_vector_b64,
        PHONE_NUMBER_PRIVATE_KEY,
    )

    print(decrypted_data)

    if decrypted_data["action"] == "ping":
        response = {"data": {"status": "active"}}

    elif decrypted_data["action"] == "INIT":
        response = {
            "screen": "COMPANY_REGISTRATION",
            "data": {
                "visible_otp_input": False,
                "visible_verify_btn": False,
                "send_visible": True,
            },
        }

    elif decrypted_data["data"]["trigger"] == "otp_selected":
        mobile_no = decrypted_data["data"]["mobile_no"]

        # Show OTP input field
        response = {
            "screen": "COMPANY_REGISTRATION",
            "data": {
                "visible_otp_input": True,
                "visible_verify_btn": True,
                "error_message": "OTP sent to your mobile",
            },
        }

    elif decrypted_data["data"]["trigger"] == "verified_otp":
        mobile_no = decrypted_data["data"]["mobile_no"]
        otp = decrypted_data["data"]["otp"]

        # Static OTP for testing
        STATIC_OTP = "123456"

        if otp == STATIC_OTP:
            response = {
                "screen": "COMPANY_REGISTRATION",
                "data": {
                    "visible_otp_input": False,
                    "visible_verify_btn": False,
                    "otp_verified": True,
                    "send_visible": False,
                    "error_message": "OTP verified successfully",
                },
            }
        else:
            response = {
                "screen": "COMPANY_REGISTRATION",
                "data": {
                    "visible_otp_input": True,
                    "visible_verify_btn": True,
                    "error_message": f"Invalid OTP. Use: {STATIC_OTP}",
                },
            }

    elif decrypted_data["data"]["trigger"] == "company_registration_completed":
        # Extract company data
        company_data = {
            "name": decrypted_data["data"].get("name"),
            "industry_sector": decrypted_data["data"].get("industry_sector"),
            "city": decrypted_data["data"].get("city"),
            "state": decrypted_data["data"].get("state"),
            "hub_tier": decrypted_data["data"].get("hub_tier"),
            "website": decrypted_data["data"].get("website"),
            "hr_contact": decrypted_data["data"].get("hr_contact"),
            "mobile_no": decrypted_data["data"].get("mobile_no"),
            "skills_required": decrypted_data["data"].get("skills_required"),
            "notes": decrypted_data["data"].get("notes"),
        }

        # Return success response
        response = {
            "screen": "COMPANY_REGISTRATION",
            "data": {
                "status": "success",
                "message": "Company registered successfully",
                "company_data": company_data,
            },
        }

    else:
        response = {
            "screen": "COMPANY_REGISTRATION",
            "data": {"error_message": "Invalid request"},
        }

    encrypted_response = encrypt_response(response, aes_key, iv)
    return PlainTextResponse(content=encrypted_response, media_type="text/plain")
