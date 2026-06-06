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
        send_to_channel = False
        if (
            isinstance(request, dict)
            and 'entry' in request
            and isinstance(request['entry'], list)
            and len(request['entry']) > 0
        ):
            entry_data = request['entry'][0]
            if isinstance(entry_data, dict) and 'changes' in entry_data:
                changes = entry_data['changes']
                if isinstance(changes, list) and len(changes) > 0:
                    first_change = changes[0]
                    if isinstance(first_change, dict):
                        change_val = first_change.get('value', {})
                        if isinstance(change_val, dict) and ('statuses' in change_val or 'event' in change_val):
                            pass
                        else:
                            channel.queue_declare('sdi', durable=True)
                            channel.basic_publish(exchange='', routing_key='sdi', body=data)
                    

            

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