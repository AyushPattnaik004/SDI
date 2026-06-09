import traceback
import json
from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from utils.fb_utils import decrypt_request, encrypt_response
from core.keys import PHONE_NUMBER_PRIVATE_KEY
import uuid
from core.db import SDI_DB
from models.jobs_data import Jobs

job_posting_router = APIRouter()


@job_posting_router.post("/")
async def post_job(body: dict = Body()):
    decrypted_data = {}
    aes_key, iv = None, None
    response = None

    try:
        encrypted_flow_data = body.get("encrypted_flow_data")
        encrypted_aes_key = body.get("encrypted_aes_key")
        initial_vector = body.get("initial_vector")

        if not (encrypted_flow_data and encrypted_aes_key and initial_vector):
            return PlainTextResponse(
                content='{"error": true, "error_message": "Missing encryption fields"}',
                media_type="text/plain",
            )

        decrypted_data, aes_key, iv = decrypt_request(
            encrypted_flow_data,
            encrypted_aes_key,
            initial_vector,
            PHONE_NUMBER_PRIVATE_KEY,
        )

        data = decrypted_data.get("data", {})
        screen = decrypted_data.get("screen", "WELCOME")

        print("Decrypted Data:", decrypted_data)

        # --------------------------------------------------
        # 1️⃣ PING HANDLING
        # --------------------------------------------------
        if decrypted_data.get("action") == "ping":
            response = {"data": {"status": "active"}}

        # --------------------------------------------------
        # 2️⃣ INIT / FIRST LOAD
        # --------------------------------------------------
        elif not data:
            response = {
                "screen": "WELCOME",
                "data": {"message": "success"},
            }

        # --------------------------------------------------
        # 3️⃣ TRIGGER HANDLING
        # --------------------------------------------------
        elif "trigger" in data:
            trigger_type = data.get("trigger")

            if trigger_type == "jobs_selected":
                if "jobs" in data:
                    selected_job_id = data.get("jobs")
                    db = SDI_DB()
                    try:
                        jobs = db.query(Jobs).all()
                        jobss_list = [
                            {
                                "id": str(j.id),
                                "title": f"{j.job_specialization} - {j.location}"
                            }
                            for j in jobs
                        ]
                        try:
                            job_uuid = uuid.UUID(selected_job_id)
                        except ValueError:
                            job_uuid = None
                        
                        selected_job = db.query(Jobs).filter(Jobs.id == job_uuid).first() if job_uuid else None
                        if selected_job:
                            details = (
                                f"**Job Specialization**: {selected_job.job_specialization}\n"
                                f"**Job Description**: {selected_job.job_description}\n"
                                f"**Location**: {selected_job.location}\n"
                                f"**Salary Range**: Rs. {selected_job.salary_min} - Rs. {selected_job.salary_max}\n"
                                f"**Experience**: {selected_job.experience or 'N/A'}\n"
                                f"**Qualification**: {selected_job.qualification or 'N/A'}\n"
                                f"**Joining Date**: {selected_job.joining_date or 'N/A'}\n"
                                f"**Headcount**: {selected_job.headcount or 1}\n"
                                f"**Gender Preference**: {selected_job.gender_preference or 'N/A'}\n"
                                f"**Additional Notes**: {selected_job.additional_notes or 'N/A'}"
                            )
                        else:
                            details = "Selected job details could not be found."
                    finally:
                        db.close()
                    
                    response = {
                        "screen": "INTRODUCTION_LETTER",
                        "data": {
                            "jobss": jobss_list,
                            "text1": details,
                            "visible_1": True
                        }
                    }
                else:
                    response = {
                        "screen": "JOB_POSTING_FORM",
                        "data": {
                            "job_types": data.get("job_types", []),
                            "locations": data.get("locations", []),
                            "joining_date_options": data.get("joining_date_options", []),
                            "gender_preferences": data.get("gender_preferences", []),
                            "message": "success",
                        },
                    }

            elif trigger_type == "user_Selected":
                response = {
                    "screen": "USER_PROFILE",
                    "data": {"message": "User profile screen"},
                }
            elif trigger_type =="introduction_selected":
                db = SDI_DB()
                try:
                    jobs = db.query(Jobs).all()
                    jobss_list = [
                        {
                            "id": str(job.id),
                            "title": f"{job.job_specialization} - {job.location}"
                        }
                        for job in jobs
                    ]
                finally:
                    db.close()
                response={
                    "screen":"INTRODUCTION_LETTER",
                    "data": {
                        "jobss": jobss_list,
                        "text1": "",
                        "visible_1": False
                    }
                }
            elif trigger_type == "job_posting_completed":
                job_data = {
                    "job_type": data.get("job_type"),
                    "job_specialization": data.get("job_specialization"),
                    "job_description": data.get("job_description"),
                    "location": data.get("location"),
                    "custom_location": data.get("custom_location"),
                    "salary_min": data.get("salary_min"),
                    "salary_max": data.get("salary_max"),
                    "joining_date_option": data.get("joining_date_option"),
                    "joining_date": data.get("joining_date"),
                    "headcount": data.get("headcount", 1),
                    "gender_preference": data.get("gender_preference"),
                    "additional_notes": data.get("additional_notes"),
                    "communication": data.get("communication"),
                }

                required_fields = [
                    "job_type",
                    "job_specialization",
                    "job_description",
                    "location",
                    "salary_min",
                    "salary_max",
                    "joining_date_option",
                ]

                missing = [f for f in required_fields if not job_data.get(f)]

                if missing:
                    response = {
                        "screen": "JOB_POSTING_FORM",
                        "data": {
                            "error": True,
                            "error_message": f"Missing required fields: {', '.join(missing)}",
                        },
                    }
                elif job_data["joining_date_option"] == "specific_date" and not job_data.get("joining_date"):
                    response = {
                        "screen": "JOB_POSTING_FORM",
                        "data": {
                            "error": True,
                            "error_message": "Specific joining date is required",
                        },
                    }
                elif int(job_data["salary_min"]) >= int(job_data["salary_max"]):
                    response = {
                        "screen": "JOB_POSTING_FORM",
                        "data": {
                            "error": True,
                            "error_message": "Maximum salary must be greater than minimum salary",
                        },
                    }
                else:
                    response = {
                        "screen": "SUCCESS",
                        "data": {
                            "message": "Job posted successfully",
                            "job_data": job_data,
                        },
                    }

            else:
                response = {
                    "screen": "WELCOME",
                    "data": {"error": True, "error_message": f"Unknown trigger: {trigger_type}"},
                }

        # --------------------------------------------------
        # 4️⃣ FALLBACK
        # --------------------------------------------------
        else:
            response = {
                "screen": "WELCOME",
                "data": {"error": True, "error_message": "Invalid request"},
            }

        # --------------------------------------------------
        # ENCRYPT & RETURN
        # --------------------------------------------------
        if response:
            encrypted_response = encrypt_response(response, aes_key, iv)
            return PlainTextResponse(
                content=encrypted_response,
                media_type="text/plain",
            )

    except Exception as e:
        traceback.print_exc()

        if not aes_key or not iv:
            return PlainTextResponse(
                content='{"error": true, "error_message": "Decryption failed"}',
                media_type="text/plain",
            )

        response = {
            "screen": decrypted_data.get("screen", "WELCOME"),
            "data": {"error": True, "error_message": str(e)},
        }

        encrypted_response = encrypt_response(response, aes_key, iv)
        return PlainTextResponse(
            content=encrypted_response,
            media_type="text/plain",
        )