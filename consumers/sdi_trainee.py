import json
import requests
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from fastapi.encoders import jsonable_encoder
from pika.spec import Basic, BasicProperties
from pika.channel import Channel
from ulid import ulid
from datetime import datetime

from core.db import SDI_DB
from models.profile import profile
from models.flowmaster import flow

import traceback

from utils.send_message import send_message

class SDI:

    def __init__(self, queue: str = "sdi", prefetch_count: int = 1) -> None:

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
                db.query(flow)
                .filter(flow.number == recipient_number)
                .filter(flow.status.in_(["START", "ONGOING","COMPLETE"]))
            )  # this is the main table that maintain state step and everything
            user_state_data = user_state_instance.first()  
            
            if user_state_data:
                if isinstance(message,str) and "abort" in message.lower():
                    user_state_instance.update({"status":"COMPLETE"})
                    message_body ="""
✨ Your session has been completed successfully!

😊 You can start a new session anytime and continue availing our services seamlessly.                        
"""            
                    message_type = "text",
                else:
                    ...
            else:
                
                if isinstance(message,str) and payload is None:
                    message_body ="""
Welcome to portal
"""
                    message_type = "list"
                    message_header ="Choose service"                   
                    interactive_payload = [
                        {
                            "type":"list",
                            "header":"Choose",
                            "options":[
                            {
                            "id": "trainee",
                            "title": "Trainee"
                            },
                            {
                            "id": "sdi",
                            "title": "SDI"
                            },
                            {
                            "id": "company",
                            "title": "Company"
                            },
                            {
                            "id": "training_partner",
                            "title": "Training Partner"
                            },
                            {
                            "id": "alumni",
                            "title": "Alumni"
                            }
                            ]
                        }
                    ]



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
