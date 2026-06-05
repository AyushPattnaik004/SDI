import json
import requests
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from fastapi.encoders import jsonable_encoder
from pika.spec import Basic, BasicProperties
from pika.channel import Channel
from ulid import ULID
from datetime import datetime

from core.db import BLS_DB
from models.bls_data_flow import BLSDataFlow
from models.master_data import MasterData


from utils.send_message import send_message


import traceback

import random

from datetime import date, timedelta
import base64
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


class BLSFLOW:

    def __init__(self, queue: str = "bls", prefetch_count: int = 1) -> None:

        self.connection = BlockingConnection(ConnectionParameters(host="localhost"))
        # self.connection = BlockingConnection(ConnectionParameters("localhost"))
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
            db = BLS_DB()
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
            message_type = "text"  # if the message will be normal(values expected text,document,image,video, audio)
            message_body = ""  # the actual message that will be sent to usera
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
                # message = handle_audio(chat_is['audio']['id'])
                message = chat_is["audio"]["id"]
                audio = True
            elif chat_is["type"].lower() == "document":
                message = "document uploaded"
            elif chat_is["type"].lower() == "image":
                message = "image uploaded"
            elif chat_is["type"].lower() == "location":
                # message = chat_is['location']
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
                db.query(BLSDataFlow)
                .filter(BLSDataFlow.number == recipient_number)
                .filter(BLSDataFlow.status.in_(["START", "ONGOING"]))
            )  # this is the main table that maintain state step and everything
            user_state_data = user_state_instance.first()

            if user_state_data:
                if isinstance(message, str) and "abort" in message.lower():
                    user_state_instance.update({"status": "ABORTED"})
                    message_body = """
✨ Your session has been completed successfully!

😊 You can start a new session anytime and continue availing our services seamlessly.

🌍 Thank you for choosing BLS International!
"""
                    message_type = "interactive"
                    interactive_payload = [
                        {
                            "type": "button",
                            "options": [
                                {"id": "about", "title": "About BLS"},
                                {"id": "main", "title": "Main Menu"},
                            ],
                        }
                    ]

                else:

                    if user_state_data.status == "START":
                        if user_state_data.step == "choose_service":
                            if isinstance(message, dict):
                                if (
                                    "submit" in message
                                    and message["submit"] == "service"
                                ):
                                    if message["service"] == "visa_type":
                                        if message["visa_type"] == "schengen":
                                            message_type = "interactive"
                                            message_body = """
✨ *Spain Short Term Schengen Visa Services* ✨

Planning a short trip to Spain or other Schengen countries?
We’re here to help you with everything you need for your visa journey 🌍✈️

📄 Documents Required
💳 Visa Fees
📸 Photo Specifications
⏳ Processing Time
⬇️ Download Application Form

Please explore the information below and select the section you would like to know more about 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_schengen_visa_type.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "1867415153946936",
                                                    "flow_button": "Open",
                                                    "flow_payload": "navigate",
                                                }
                                            ]
                                        elif message["visa_type"] == "national":
                                            message_type = "interactive"
                                            message_body = """
✨ *Spain National Visa Services* ✨

Planning to stay in Spain for work, study, family reunion, or long-term residence?
We’re here to guide you through your National Visa journey smoothly and efficiently 🌍✈️

📄 Documents Required
💳 Visa Fees
📸 Photo Specifications
⏳ Processing Time
⬇️ Download Application Form

Please explore the information below and choose the section you would like assistance with 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_national_visa_type.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "1350839970249320",
                                                    "flow_button": "Open",
                                                    "flow_payload": "navigate",
                                                }
                                            ]

                                    elif message["service"] == "book_appointment":
                                        if (
                                            message["appointment_service"]
                                            == "book_appointment"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
📅✨ *Book New Appointment* ✨📅

Ready to begin your visa journey?
Book your appointment easily with BLS International and choose your preferred date, time, and application center 🌍✈️

🛂 Quick & Easy Scheduling
⏰ Convenient Time Slots
🏢 Multiple Visa Application Centres
✅ Instant Appointment Confirmation

Please continue below to book your appointment 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_book_appointment.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "1292374219162975",
                                                    "flow_button": "Book",
                                                    "flow_payload": None,
                                                }
                                            ]

                                        elif (
                                            message["appointment_service"]
                                            == "reprint_appointment_letter"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
🖨️✨ *Reprint Appointment Letter* ✨🖨️

Need another copy of your appointment confirmation?
You can quickly reprint your appointment letter for visa submission or future reference 📄📅

📂 Retrieve Existing Appointment
🖨️ Download & Reprint Instantly
✅ Easy & Secure Access

Please continue below to reprint your appointment letter 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_reprint_application_form.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "2586198861820882",
                                                    "flow_button": "Reprint",
                                                    "flow_payload": None,
                                                }
                                            ]
                                        elif (
                                            message["appointment_service"]
                                            == "cancel_appointment"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
❌✨ *Cancel Appointment* ✨❌

Need to cancel your existing visa appointment?
You can easily submit a cancellation request using your appointment details 📅🛂

📂 Retrieve Existing Appointment
⚡ Quick Cancellation Process
📧 Instant Confirmation Updates

Please continue below to cancel your appointment 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_cancel_appointment.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "1685223739562708",
                                                    "flow_button": "Cancel",
                                                    "flow_payload": None,
                                                }
                                            ]

                                    elif message["service"] == "general_information":
                                        if (
                                            message["general_information_service"]
                                            == "customer_experience"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
💬✨ *Customer Feedback* ✨💬

Your feedback helps us improve and serve you better 🤝🌍

We would love to hear about your experience with BLS International services 🛂✈️

⭐ Share Your Experience
😊 Rate Our Services
📝 Suggest Improvements
💡 Help Us Enhance Customer Experience

Please continue below to share your valuable feedback 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_customer_feedback.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "4720884261478088",
                                                    "flow_button": "Open",
                                                    "flow_payload": "navigate",
                                                }
                                            ]

                                        elif (
                                            message["general_information_service"]
                                            == "public_holidays"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
🎉✨ *Public Holidays & Closures* ✨🎉

Stay informed about upcoming public holidays and visa application centre closures before planning your visit 📅🌍

📌 Check Holiday Dates
🏢 Visa Centre Closure Information
⏰ Plan Your Appointment Better
✈️ Avoid Last-Minute Delays

Please explore the holiday information below 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_public_holidays.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "1904730013551246",
                                                    "flow_button": "Open",
                                                    "flow_payload": "navigate",
                                                }
                                            ]
                                        elif (
                                            message["general_information_service"]
                                            == "additional_services"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
⭐✨ *Additional Services* ✨⭐

Enhance your visa application experience with our convenient value-added services designed for comfort, support, and faster assistance 🌍🛂

🛋️ Premium Lounge
📦 Courier Service
📲 SMS Alerts
📸 Photo Booth
✍️ Form Filling Assistance
⏰ Prime Time Appointment
📱 SIM Card Services
💱 Forex Services
🛡️ Travel Insurance & More

Please explore the additional services below and choose the service you would like assistance with 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_additional_services.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "1507066370885056",
                                                    "flow_button": "Open",
                                                    "flow_payload": "navigate",
                                                }
                                            ]

                                    elif (
                                        message["service"] == "travel_health_insurance"
                                    ):
                                        if (
                                            message["insurance_service_type"]
                                            == "insurance_national_visa"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
🛡️✨ *Travel Insurance for National Visa* ✨🛡️

Secure your long-term stay abroad with reliable travel and medical insurance coverage 🌍✈️

Our insurance plans are designed to support applicants applying for National Visas, including work, study, residence, and family reunion purposes 🏠📘

✅ Comprehensive Medical Coverage
🌐 International Assistance Support
📄 Visa-Compliant Insurance Plans
⚡ Quick & Hassle-Free Process

Please continue below to explore available insurance options 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_travel_insurance_national.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "2370614323349262",
                                                    "flow_button": "Book",
                                                    "flow_payload": None,
                                                }
                                            ]

                                        elif (
                                            message["appointment_service"]
                                            == "travel_insurance_schengen"
                                        ):
                                            message_type = "interactive"
                                            message_body = """
🛡️✨ *Travel Insurance for Schengen Visa* ✨🛡️

Travel confidently across Schengen countries with visa-compliant travel insurance coverage 🌍✈️

Our insurance plans are specially designed for Schengen Visa applicants and help meet mandatory embassy requirements 📄🛂

✅ Minimum €30,000 Medical Coverage
🌐 Valid Across Schengen Countries
🏥 Emergency Medical Assistance
⚡ Quick & Easy Insurance Support

Please continue below to explore available travel insurance options 👇
"""

                                            interactive_payload = [
                                                {
                                                    "header_image": "https://citylyticsmain.in:11116/assets/bls_travel_insurance_schengen.png",
                                                    "type": "flow",
                                                    "flow_token": f"{recipient_number[2:]}",
                                                    "flow_id": "2370614323349262",
                                                    "flow_button": "Book",
                                                    "flow_payload": None,
                                                }
                                            ]

                                    user_state_instance.update(
                                        {
                                            "status": "ONGOING",
                                            "service": message["service"],
                                            "step": "service_selected",
                                        }
                                    )

                            else:
                                message_body = """
📌 Please select any service from the menu above to continue 🌍✨

> If you wish to end the current session, please type 'ABORT'
"""

                        elif user_state_data.step == "main":
                            if "about" in message.lower():
                                message_type = "interactive"
                                interactive_payload = [
                                    {
                                        "header_image": "https://citylyticsmain.in:11116/assets/about_bls.png",
                                        "type": "button",
                                        "options": [
                                            {"id": "main", "title": "Main Menu"}
                                        ],
                                    }
                                ]
                                message_body = """
🌍 *About BLS International*

BLS International is a trusted global partner for visa, passport, consular, and travel-related services, serving customers across 70+ countries worldwide.

We provide seamless assistance for:

🛂 Visa & Passport Services
✈️ Flight & Hotel Bookings
🛡️ Travel Insurance & Forex
📱 International SIM Cards
⭐ Premium Travel Assistance Services

Our mission is to make your travel and documentation journey smooth, secure, and hassle-free with reliable customer support and global expertise.

Ready to get started with BLS services? 👇                    
"""
                                user_state_instance.update({"status": "COMPLETE"})
                            elif payload == "main":
                                # service selection flow
                                ##changes
                                message_type = "interactive"
                                message_body = """
🌍✨ *Welcome to BLS International Services!* ✨🌍

Your trusted partner for seamless visa, passport, travel, and consular assistance across the globe 🌐✈️

We’re here to make your journey simple, smooth, and stress-free 🤝

🛂 Visa & Passport Services
📅 Appointment Booking
📂 Application Tracking
🛡️ Travel Insurance
🏠 Doorstep Services
⭐ Premium Assistance & More

Please explore the *Main Menu* below and choose the service you would like assistance with 👇
"""

                                interactive_payload = [
                                    {
                                        "header_image": "https://citylyticsmain.in:11116/assets/bls_main_menu.png",
                                        "type": "flow",
                                        "flow_token": f"{recipient_number[2:]}",
                                        "flow_id": "827431630226502",
                                        "flow_button": "Open",
                                        "flow_payload": "navigate",
                                    }
                                ]
                                user_state_instance.update({"step": "choose_service"})

                            else:
                                message_body = """
📌 Please select any service from the menu above to continue 🌍✨

> If you wish to end the current session, please type 'ABORT'
"""
                    elif user_state_data.status == "ONGOING":
                        if isinstance(message, dict) and "submit" in message:
                            if message["submit"] in [
                                "book_appointment",
                                "premium_lounge",
                                "national_visa",
                            ]:
                                message_type = "interactive"
                                message_body = (
                                    "Please select your preferred payment method"
                                )
                                interactive_payload = [
                                    {
                                        "type": "button",
                                        "options": [
                                            {
                                                "id": f"pay_upi_{user_state_data.id}",
                                                "title": "UPI Payment",
                                            },
                                            {
                                                "id": f"pay_other_{user_state_data.id}",
                                                "title": "Other Methods",
                                            },
                                        ],
                                    }
                                ]
                            elif message["submit"] == "cancel":
                                message_body = "❌ Appointment Cancelled Successfully\n\n🆔 Appointment Reference Number: BLS8964316"
                            elif message["submit"] == "reprint":
                                message_type = "document"
                                message_header = "https://citylyticsmain.in:11116/assets/appointment_letter.pdf"
                                message_body = """
Please find attached your appointment confirmation letter for your upcoming visa application appointment 📄🛂

📅 Kindly verify all appointment details carefully before visiting the visa application centre.

⚠️ Important Reminders:
• Carry a printed copy of the appointment letter
• Bring your original passport and supporting documents
• Arrive at the centre at least 15 minutes before your appointment time

We wish you a smooth and hassle-free application experience 🌍✨
"""

                            else:
                                message_type = "interactive"
                                interactive_payload = [
                                    {
                                        "type": "button",
                                        "options": [
                                            {"id": "about", "title": "About BLS"},
                                            {"id": "main", "title": "Main Menu"},
                                        ],
                                    }
                                ]

                                message_body = """
🙏✨ *Thank You for Using Our Services* ✨🙏

Dear Applicant,

Thank you for choosing *BLS International Services* 🌍🛂

We truly appreciate the opportunity to assist you with your visa and travel requirements. Your trust means a lot to us 🤝✨

📄 Your request has been successfully processed.
📬 You will receive further updates through SMS or Email, wherever applicable.

We wish you a smooth, successful, and pleasant journey ahead ✈️🌎

Thank you once again for being a valued customer 💙
"""
                                user_state_instance.update({"status": "COMPLETE"})
                                # handle submits

                        elif (
                            isinstance(message, str)
                            and isinstance(payload, str)
                            and "pay" in payload
                        ):
                            pay, payment_method, id = payload.split("_")
                            amount = 1000
                            ref_num = f'BLS{str(ULID().timestamp).replace(".", "")}'
                            receipt_number = ref_num
                            message_type = "interactive"
                            send_type = "MESSAGE"
                            message_body = "Please make the payment to confirm your booking.\n\n> Type 'Abort' to end your session."
                            number_of_people = 1
                            ticket_price = float(amount) * 100 / number_of_people
                            # print(ticket_price,'ticket priceeeee')
                            interactive_payload = [
                                {
                                    "type": "order_details",
                                    "reference_id": receipt_number,
                                    "upi_intent_link": None,
                                    "payment_link": f"https://citylyticsmain.in:11116/api/v1/payment/bls/?id={id}&ref={receipt_number}&mobile={recipient_number}",
                                    "total_amount": ticket_price,
                                    "quntity": number_of_people,
                                    "product_name": "BLS INTERNATIONAL",
                                    "importer_name": "sinch",
                                    "importer_address": {
                                        "address_line1": "B8/733 nand nagri",
                                        "address_line2": "police station",
                                        "city": "East Delhi",
                                        "zone_code": "DL",
                                        "postal_code": "110093",
                                        "country_code": "IN",
                                    },
                                }
                            ]
                        else:
                            message_type = "interactive"
                            interactive_payload = [
                                {
                                    "type": "button",
                                    "options": [
                                        {"id": "about", "title": "About BLS"},
                                        {"id": "main", "title": "Main Menu"},
                                    ],
                                }
                            ]
                            message_body = """
🙏✨ *Thank You for Using Our Services* ✨🙏

Dear Applicant,

Thank you for choosing *BLS International Services* 🌍🛂

We truly appreciate the opportunity to assist you with your visa and travel requirements. Your trust means a lot to us 🤝✨

📄 Your request has been successfully processed.
📬 You will receive further updates through SMS or Email, wherever applicable.

We wish you a smooth, successful, and pleasant journey ahead ✈️🌎

Thank you once again for being a valued customer 💙
"""

                            user_state_instance.update({"status": "COMPLETE"})
            else:

                if isinstance(message, str) and payload is None:
                    message_body = """
🌟 *Welcome to BLS International!*

Your trusted partner for:

🛂 Visa & Passport Services
✈️ Flights & Hotels
🛡️ Travel Insurance & Forex
📱 International SIM Cards
⭐ Premium Travel Assistance

We’re here to make your travel journey smooth and hassle-free 🌍

Please choose an option below to continue 👇
"""
                    message_type = "interactive"
                    interactive_payload = [
                        {
                            "header_image": "https://citylyticsmain.in:11116/assets/bls_welcome.png",
                            "type": "button",
                            "options": [
                                {"id": "about", "title": "About BLS"},
                                {"id": "main", "title": "Main Menu"},
                            ],
                        }
                    ]
                    db.add(
                        BLSDataFlow(
                            **{
                                "id": ULID().hex,
                                "number": recipient_number,
                                "service": "main",
                                "status": "START",
                                "step": "main",
                                "user_data": {},
                            }
                        )
                    )

                elif isinstance(message, str) and payload == "main":
                    # main menu flow
                    ##changes
                    message_type = "interactive"
                    message_body = """
🌍✨ *Welcome to BLS International Services!* ✨🌍

Your trusted partner for seamless visa, passport, travel, and consular assistance across the globe 🌐✈️

We’re here to make your journey simple, smooth, and stress-free 🤝

🛂 Visa & Passport Services
📅 Appointment Booking
📂 Application Tracking
🛡️ Travel Insurance
🏠 Doorstep Services
⭐ Premium Assistance & More

Please explore the *Main Menu* below and choose the service you would like assistance with 👇
"""

                    interactive_payload = [
                        {
                            "header_image": "https://citylyticsmain.in:11116/assets/bls_main_menu.png",
                            "type": "flow",
                            "flow_token": f"{recipient_number[2:]}",
                            "flow_id": "827431630226502",
                            "flow_button": "Open",
                            "flow_payload": "navigate",
                        }
                    ]

                    db.add(
                        BLSDataFlow(
                            **{
                                "id": ULID().hex,
                                "number": recipient_number,
                                "service": "main",
                                "status": "START",
                                "step": "choose_service",
                                "user_data": {},
                            }
                        )
                    )

                elif isinstance(message, str) and payload == "about":
                    # main menu flow
                    ##changes
                    message_type = "interactive"
                    interactive_payload = [
                        {
                            "header_image": "https://citylyticsmain.in:11116/assets/about_bls.png",
                            "type": "button",
                            "options": [{"id": "main", "title": "Main Menu"}],
                        }
                    ]
                    message_body = """
🌍 *About BLS International*

BLS International is a trusted global partner for visa, passport, consular, and travel-related services, serving customers across 70+ countries worldwide.

We provide seamless assistance for:

🛂 Visa & Passport Services
✈️ Flight & Hotel Bookings
🛡️ Travel Insurance & Forex
📱 International SIM Cards
⭐ Premium Travel Assistance Services

Our mission is to make your travel and documentation journey smooth, secure, and hassle-free with reliable customer support and global expertise.

Ready to get started with BLS services? 👇                    
"""

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

        except:
            traceback.print_exc()
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return ()

        finally:
            db.commit()
            db.close()
