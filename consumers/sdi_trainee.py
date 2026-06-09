import json
import requests
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from fastapi.encoders import jsonable_encoder
from pika.spec import Basic, BasicProperties
from pika.channel import Channel
from datetime import datetime

from core.db import SDI_DB
from models.profile import profile
from models.flowmaster import flow
from models.company import Company
from models.jobs_data import Jobs
from ulid import ULID
from sqlalchemy import func, or_
import uuid

import traceback

from utils.send_message import send_message

class SDI:

    def __init__(self, queue: str = "sdi", prefetch_count: int = 1) -> None:

        self.connection = BlockingConnection(ConnectionParameters(host="localhost"))
        self.queue_name = queue
        self.channel = self.connection.channel()
        self.prefetch_count = prefetch_count

        self.channel.queue_declare(self.queue_name, durable=True)

        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback
        )

        self.channel.start_consuming()

    def callback(
        self,
        ch: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        try:
            db = SDI_DB()
            chat = json.loads(body.decode())
            print(chat)
            chat_is = chat["entry"][0]["changes"][0]["value"]["messages"][0]
            sender: str = chat_is["from"]
            payload = None
            phone_number_id = chat["entry"][0]["changes"][0]["value"]["metadata"][
                "phone_number_id"
            ]
            sender_number = chat["entry"][0]["changes"][0]["value"]["metadata"][
                "display_phone_number"
            ]
            message_type = "text"
            message_body = ""
            button_params = None
            interactive_payload = None
            body_params = None
            message_header = None
            recipient_number = sender
            send_type = "MESSAGE"
            language = "en"
            audio = False

            # handle what message we have got
            if chat_is["type"] == "text":
                message = chat_is["text"]["body"]
            elif chat_is["type"] == "audio":
                message = chat_is["audio"]["id"]
                audio = True
            elif chat_is["type"].lower() == "document":
                message = "document uploaded"
            elif chat_is["type"].lower() == "image":
                message = "image uploaded"
            elif chat_is["type"].lower() == "location":
                message = "location"
                payload = "location"
            elif chat_is["type"].lower() == "button":
                message = chat_is["button"]["text"]
                payload = chat_is["button"]["payload"]
            elif chat_is["type"] == "interactive":
                if chat_is["interactive"]["type"] == "list_reply":
                    message = chat_is["interactive"]["list_reply"]["title"]
                    payload = chat_is["interactive"]["list_reply"]["id"]
                elif chat_is["interactive"]["type"] == "button_reply":
                    message = chat_is["interactive"]["button_reply"]["title"]
                    payload = chat_is["interactive"]["button_reply"]["id"]
                else:
                    message = (
                        json.loads(chat_is["interactive"]["nfm_reply"]["response_json"])
                        if isinstance(
                            chat_is["interactive"]["nfm_reply"]["response_json"], str
                        )
                        else chat_is["interactive"]["nfm_reply"]["response_json"]
                    )
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            user_state_instance = (
                db.query(flow)
                .filter(flow.number == recipient_number)
                .filter(flow.status.in_(["START", "ONGOING"]))
            )
            user_state_data = user_state_instance.first()

            if user_state_data:
                # ── ABORT ────────────────────────────────────────────────────
                if isinstance(message, str) and "abort" in message.lower():
                    user_state_instance.update({"status": "ABORTED"})
                    message_body = (
                        "✨ Your session has been completed successfully!\n\n"
                        "😊 You can start a new session anytime and continue availing our services seamlessly."
                    )
                    message_type = "text"

                # ── START state ──────────────────────────────────────────────
                elif user_state_data.status == "START":
                    if payload == "trainee":
                        exist = db.query(profile).filter(profile.number == recipient_number).first()
                        if exist:
                            message_type = "interactive"
                            message_body = "📋 Update, upload, or share feedback to keep your profile current."
                            interactive_payload = [
                                {
                                    "type": "flow",
                                    "flow_token": recipient_number,
                                    "flow_id": "2083093795942774",
                                    "flow_button": "Open Form",
                                    "flow_payload": {
                                        "screen": "otp_screen",
                                        "data": {"otp_verified": False}
                                    }
                                }
                            ]
                            user_state_instance.update({"status": "ONGOING"})
                        else:
                            message_type = "interactive"
                            message_body = "Please create your profile."
                            interactive_payload = [
                                {
                                    "type": "flow",
                                    "flow_token": "abcd_1234_en",
                                    "flow_id": "1643051456924315",
                                    "flow_button": "Open Form",
                                    "flow_payload": "navigate"
                                }
                            ]
                            user_state_instance.update({"status": "ONGOING"})

                    elif payload == "company":
                        exist_company = db.query(Company).filter(
                            or_(
                                Company.mobile_no == recipient_number,
                                Company.mobile_no == recipient_number[-10:],
                                Company.mobile_no == f"91{recipient_number[-10:]}"
                            )
                        ).first()
                        if exist_company:
                            message_type = "interactive"
                            message_body = "Please fill in the job posting details."
                            interactive_payload = [
                                {
                                    "type": "flow",
                                    "flow_token": "abcd_1234_en",
                                    "flow_id": "2182567079188693",
                                    "flow_button": "Post a Job",
                                    "flow_payload": "navigate"
                                }
                            ]
                            user_state_instance.update({"status": "ONGOING"})
                        else:
                            message_type = "interactive"
                            message_body = "Please register your company."
                            interactive_payload = [
                                {
                                    "type": "flow",
                                    "flow_token": "abcd_1234_en",
                                    "flow_id": "1349295737222034",
                                    "flow_button": "Register",
                                    "flow_payload": "navigate"
                                }
                            ]
                            user_state_instance.update({"status": "ONGOING"})

                    elif payload in ["sdi", "training_partner", "alumni"]:
                        message_body = f"Thank you for choosing {payload.replace('_', ' ').title()}. This service is under construction. Please try again later."
                        message_type = "text"
                        user_state_instance.update({"status": "COMPLETE"})

                    

                    else:
                        # ── FIX: plain text / unknown payload in START state ──

                        message_body = (
                            "📌 Please select any service from the menu above to continue 🌍✨\n\n"
                            "> If you wish to end the current session, please type 'ABORT'"
                        )
                        message_type = "text"

                # ── ONGOING state (flow responses arrive here) ────────────────
                else:
                    # ── FIX: catch-all for ONGOING state with no matching branch ──
                    if isinstance(message, dict):
                        if message["submit"]== "add_trainee":
                            trainee = profile(
                                id=str(uuid.uuid4()),
                                name=message.get("user_name", ""),
                                number=recipient_number,
                                email=message.get("email", ""),
                                gender=message.get("gender", ""),
                                age=int(message["user_age"]) if message.get("user_age") else None,
                                course=message.get("course", ""),
                                is_sponsored=bool(message.get("Govt", [])),
                                qualification=message.get("Qualification", ""),
                                branch=message.get("branch", ""),
                                twelveth_p=message.get("12th", ""),
                                tenth_p=message.get("10th", "")
                            )
                            db.add(trainee)
                            db.commit()

                            send_message(
                                "text",
                                "Thank you! Your profile has been created successfully. You can now update profile, upload pay slips, give feedback.",
                                None, None, None, None,
                                recipient_number, "MESSAGE", language, sender_number
                            )

                            message_type = "interactive"
                            message_body = "📋 Update, upload, or share feedback to keep your profile current."
                            interactive_payload = [
                                {
                                    "type": "flow",
                                    "flow_token": recipient_number,
                                    "flow_id": "2083093795942774",
                                    "flow_button": "Open Form",
                                    "flow_payload": {
                                        "screen": "otp_screen",
                                        "data": {"otp_verified": False}
                                    }
                                }
                            ]
                            user_state_instance.update({"status": "ONGOING"})

                        elif message.get("submit") == "update":

                            trainee = db.query(profile).filter(
                                profile.number == recipient_number
                            ).first()

                            if trainee:
                                trainee.name = message.get("user_name", trainee.name)
                                trainee.email = message.get("email", trainee.email)
                                trainee.gender = message.get("gender", trainee.gender)
                                trainee.age = int(message["user_age"]) if message.get("user_age") else trainee.age
                                trainee.course = message.get("course", trainee.course)
                                trainee.is_sponsored = bool(message.get("Govt", trainee.is_sponsored))
                                trainee.qualification = message.get("Qualification", trainee.qualification)
                                trainee.branch = message.get("branch", trainee.branch)
                                trainee.twelveth_p = message.get("12th", trainee.twelveth_p)
                                trainee.tenth_p = message.get("10th", trainee.tenth_p)
                                db.commit()
                            message_type = "text"
                            message_body = "Your details have been successfully submitted."
                            user_state_instance.update({"status": "COMPLETE"})

                        elif "industry_sector" in message:
                            company = Company(
                                id=uuid.uuid4(),
                                company_name=message.get("name"),
                                sector=message.get("industry_sector"),
                                osector=message.get("osector"),
                                city=message.get("city"),
                                state=message.get("state"),
                                tier=message.get("hub_tier"),
                                skills=message.get("skills_required"),
                                website=message.get("website"),
                                hr_contact=message.get("hr_contact"),
                                notes=message.get("notes"),
                                mobile_no=message.get("mobile_no"),
                                gstno=message.get("gstno")
                            )
                            db.add(company)
                            db.flush()

                            send_message(
                                "text",
                                "Thank you! Your company has been registered successfully. You can now post jobs.",
                                None, None, None, None,
                                recipient_number, "MESSAGE", language, sender_number
                            )

                            message_type = "interactive"
                            message_body = "Please fill in the job posting details."
                            interactive_payload = [
                                {
                                    "type": "flow",
                                    "flow_token": "abcd_1234_en",
                                    "flow_id": "2182567079188693",
                                    "flow_button": "Post a Job",
                                    "flow_payload": "navigate"
                                }
                            ]
                            user_state_instance.update({"status": "ONGOING"})

                        elif "job_type" in message:
                            comp = db.query(Company).filter(
                                or_(
                                    Company.mobile_no == recipient_number,
                                    Company.mobile_no == recipient_number[-10:],
                                    Company.mobile_no == f"91{recipient_number[-10:]}"
                                )
                            ).first()
                            if comp:
                                joining_date_val = None
                                if message.get("joining_date"):
                                    try:
                                        joining_date_val = datetime.strptime(message["joining_date"], "%Y-%m-%d").date()
                                    except Exception:
                                        pass
                                job = Jobs(
                                    id=uuid.uuid4(),
                                    job_type=message.get("job_type"),
                                    job_specialization=message.get("job_specialization"),
                                    job_description=message.get("job_description"),
                                    location=message.get("location"),
                                    custom_location=message.get("custom_location"),
                                    salary_min=int(message.get("salary_min")) if message.get("salary_min") else 0,
                                    salary_max=int(message.get("salary_max")) if message.get("salary_max") else 0,
                                    experience=message.get("experience"),
                                    qualification=message.get("qualification"),
                                    age=message.get("age"),
                                    joining_date_option=message.get("joining_date_option", "specific_date"),
                                    joining_date=joining_date_val,
                                    headcount=int(message.get("headcount")) if message.get("headcount") else 1,
                                    gender_preference=message.get("gender_preference"),
                                    additional_notes=message.get("additional_notes"),
                                    sdi_introduction_letter=message.get("sdi_introduction_letter"),
                                    shortlisted_profile=message.get("shortlisted_profile")
                                )
                                db.add(job)
                                message_body = "Thank you! Your job posting has been successfully registered."
                            else:
                                message_body = "Error: Registered company not found. Please register first."
                            message_type = "text"
                            user_state_instance.update({"status": "COMPLETE"})

                        else:
                            message_body = "Thank you! Your details have been submitted successfully."
                            message_type = "text"
                            user_state_instance.update({"status": "COMPLETE"})
                    
                   

            else:
                # ── No active session — show welcome menu ────────────────────
                if isinstance(message, str) and payload is None:
                    message_body = "Welcome to portal"
                    message_type = "interactive"
                    message_header = "Choose service"
                    interactive_payload = [
                        {
                            "type": "list",
                            "header": "Choose",
                            "options": [
                                {"id": "trainee",          "title": "Trainee"},
                                {"id": "sdi",              "title": "SDI"},
                                {"id": "company",          "title": "Company"},
                                {"id": "training_partner", "title": "Training Partner"},
                                {"id": "alumni",           "title": "Alumni"},
                            ]
                        }
                    ]
                    db.add(flow(**{
                        "id": ULID().hex,
                        "number": recipient_number,
                        "status": "START"
                    }))

            db.commit()

            # ── Guard: never send an empty body ─────────────────────────────
            if message_type == "text" and not message_body.strip():
                message_body = "📌 Please select a service from the menu to continue."

            res = send_message(
                message_type,
                message_body,
                button_params,
                interactive_payload,
                body_params,
                message_header,
                recipient_number,
                send_type,
                language,
                sender_number,
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print("here sent")
            return

        except Exception:
            db.rollback()
            traceback.print_exc()
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        finally:
            db.commit()
            db.close()