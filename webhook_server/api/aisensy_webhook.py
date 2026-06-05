from fastapi import APIRouter, Body, Request, status
from typing import Any
from pika import BlockingConnection, ConnectionParameters, BasicProperties,PlainCredentials
import traceback
from datetime import datetime
import json


webhook_router = APIRouter()





@webhook_router.post('/sdi')
async def poc_webhook(req: Request, request: dict = Body()):

    connection = None
    channel = None
    
    
    try:
        data = json.dumps(request)
        print(request)

    
        connection = BlockingConnection(ConnectionParameters(host="localhost"))


        channel = connection.channel()
        send_to_channel= False
        if 'changes' in request['entry'][0]:
            if 'statuses' in request['entry'][0]['changes'][0]['value'] or 'event' in request['entry'][0]['changes'][0]['value']:
                ...
            else:
                channel.queue_declare('sdi',durable=True)
                channel.basic_publish(exchange='',routing_key='sdi',body=data)
                    

            

        return 200

    except Exception as e:
        print(e)
        traceback.print_exc()
        
        return -1
    
    finally:
        if channel:
            channel.close()

        if connection:
            connection.close()