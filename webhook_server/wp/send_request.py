from requests import put
from json import dumps

from core.env import FB_TOKEN


def send_seen(message_id: str, phone_number_id: str):
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"

    payload = dumps({
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {FB_TOKEN}'
    }

    response = put(url, headers=headers, data=payload)

    print(response.text)
