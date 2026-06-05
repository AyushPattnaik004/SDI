
import json
import requests
import traceback



tokens={
    "919668972561":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhc3Npc3RhbnRJZCI6IjZhMDQyM2E5ZDI4YTRjMzNkMTIxOWQ2ZSIsImNsaWVudElkIjoiNjg5YjczNmEwYWJmZTYyNmRkMDQwMmQwIiwiaWF0IjoxNzc4NjU3Njk3fQ.K03wN3Tg_qBPh8YGJ8AxNwhjaWMkP7FCf8DZyUmIiv8",
    "919937566906":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhc3Npc3RhbnRJZCI6IjY2NjJkYmY5NjI4ODU1NzEwMzAwMzJlYiIsImNsaWVudElkIjoiNjY2MmRiYTgyZTg4Mjk3MTZlNDg4M2YwIiwiaWF0IjoxNzI0OTM1NDQ4fQ.jyTTs0eo57uCvzkGt7SDhelxvS4LpTexHBHhcl3B2c0"
}



def send_message( message_type,message_body,button_params,interactive_payload,body_params,message_header,recipient_number,send_type,language,sender_number) :
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, application/xml",
        "Authorization": f"Bearer {tokens[sender_number]}"
    }
    try:

        url = "https://backend.aisensy.com/direct-apis/t1/messages"
        if send_type=='MESSAGE':                    # TO SEND MESSAGE
            request_body= {"to":recipient_number, 'type': message_type}
            if message_type=="text":
                params_obj= {'body': message_body}
            elif message_type =="image" or message_type=="video" or message_type=="document":
                if isinstance(message_header,dict):
                    params_obj= {"link": message_header['link'], 'caption': message_body}
                    if message_type=='document':
                        params_obj['filename']= message_header['filename']
                else:
                    params_obj= {"link": message_header, 'caption': message_body}
                    if message_type=='document':
                        params_obj['filename']= message_header.split("/")[-1]
            elif message_type=='audio':
                params_obj= {"link": message_header}
            else:
                flow_type='list' if 'type' not in interactive_payload[0] or interactive_payload[0]['type']== 'list' else  "button" if interactive_payload[0]['type']=='button' else 'flow' if interactive_payload[0]['type']=='flow' else 'order_details' if  interactive_payload[0]['type']=='order_details' else 'order_status' if  interactive_payload[0]['type']=='order_status' else  'location_request_message'
                if 'type' not in interactive_payload[0] or interactive_payload[0]['type']== 'list' :
                    flow_action= {
                        "button": message_header,
                        "sections":[ {"title":i['header'],"rows":i['options']} for i in interactive_payload]

                    }

                    # [{
                    #        "type":'list',
                    #         "header":"Dikhega Nahi",
                    #         "options": [
                    #             {
                    #                 "id": "new",
                    #                 "title": "New Patient"
                    #             },
                    #             {
                    #                 "id": "revisiting",
                    #                 "title": "Revisiting"
                    #             }
                    #         ]}]
                elif interactive_payload[0]['type']=='order_status':
                    flow_action={
                        "name": "review_order",
                        "parameters": {
                            "reference_id": interactive_payload[0]['reference_id'],
                            "order": {
                            "status": interactive_payload[0]['order_status'],
                            "description":interactive_payload[0]['order_description']
                            }
                        }
                    }
            #     [
            #     {
            #         "type": "order_status",
            #         "reference_id": 183476,
            #         "order_status":"completed",
            #         "order_description":"Payment done"
                            
            #     }
            # ]
                    
                elif interactive_payload[0]['type']== 'order_details':
                    payment_settings=[]
                    if interactive_payload[0]['upi_intent_link']:
                         payment_settings.append({
                            "type": "upi_intent_link",
                            "upi_intent_link": {
                                "link": interactive_payload[0]['upi_intent_link']
                            }
                        })  
                    if interactive_payload[0]['payment_link']:
                        payment_settings.append({
                            "type": "payment_link",
                            "payment_link":{
                                "uri":interactive_payload[0]['payment_link'],
                                "success_url":"https://api.whatsapp.com/send/?phone=919937566906"
                            }
                        })
                    flow_action= {
                        "name": "review_and_pay",
                        "parameters": {
                            "reference_id": interactive_payload[0]['reference_id'],
                            "type": "digital-goods",   
                            "payment_type":"upi",
                            "payment_settings": payment_settings,
                            "currency": "INR",
                            "total_amount": {
                                "value": interactive_payload[0]['total_amount']* interactive_payload[0]['quntity'],
                                "offset": 100
                            },
                            "order": {
                                "status": "pending",
                                "items": [
                                    {
                                        "name":interactive_payload[0]['product_name'],
                                        "amount": {
                                            "value": interactive_payload[0]['total_amount'],
                                            "offset": 100
                                        },
                                        "quantity": interactive_payload[0]['quntity'],
                                        "country_of_origin": "INDIA",
                                        "importer_name": interactive_payload[0]['importer_name'],
                                        "importer_address": interactive_payload[0]['importer_address']
                                    }
                                ],
                                "subtotal": {
                                    "value": interactive_payload[0]['total_amount']* interactive_payload[0]['quntity'],
                                    "offset": 100
                                }
                            }
                        }
                    }
                elif interactive_payload[0]['type']=='location_request_message':
                    flow_action= {
                        "name": interactive_payload[0]['location_type']
                    }
                elif interactive_payload[0]['type']== 'button':
                    flow_action={
                        "buttons": [{
                            "type":"reply",
                            "reply": {
                                "id" :x['id'],
                                "title":x['title']
                            }
                        } for x in interactive_payload[0]['options']]
                            
                    }
                    
                    # __example__
                    # [
                    #     {
                    #        "type":'button',
                    #         "options": [
                    #               {
                    #                   "id":"1",
                    #                   "title":"button1",
                    #               },
                    #               { 
                    #                   "id":"2",
                    #                    "title":"button2", 
                    #                 }
                    # ]
                    # }
                    # ]
                else:
                    flow_action= {
                        "name": "flow",
                        "parameters":{
                            "flow_message_version": "3",
                            "flow_token": interactive_payload[0]['flow_token'],
                            "flow_id": interactive_payload[0]['flow_id'],
                            "flow_cta": interactive_payload[0]['flow_button'],
                            "flow_action": "navigate" if interactive_payload[0]['flow_payload'] else "data_exchange",
                            "flow_action_payload": interactive_payload[0]['flow_payload'] if isinstance(interactive_payload[0]['flow_payload'],dict) else None
                        }

                    }
                    #__example__
                        # [{
                        #     "type":"flow",
                        #     "flow_token":"darshanam",
                        #     "flow_id":"8438872685453",
                        #     "flow_button":"Open",
                        #     "flow_payload": {
                        #         "screen": "FIRSTPAGE",
                        #         "data": { # optional
                        #             "heading":"SELECT_OPTIONS",
                        #             "options": [
                        #                 {
                        #                     "id": "endowment",
                        #                     "title": "Endowment",
                        #                     "description":"ఎండోమెంట్ శాఖ"
                        #                 },
                        #                 {
                        #                     "id": "revenue",
                        #                     "title": "Revenue",
                        #                     "description":"రెవెన్యూ శాఖ"
                        #                 }
                        #             ]
                        #         }
                        #     }
                        # }]


                params_obj= {
                    "type":flow_type,
                    "body":{"text":message_body},
                    "action":flow_action
                }
                if 'header_image' in interactive_payload[0]:
                     params_obj['header']= {"type": "image", "image": {"link": interactive_payload[0]['header_image']}}

            request_body[message_type]= params_obj
        else:                                       # TO SEND TEMPLATE
            request_body= {"to":recipient_number, "type":"template", "template":{
                "name":message_body,
                "language": {
                    "policy":"deterministic",
                    "code": language
                },
            }}
            components=[]
            if message_type=='image' or message_type=="video" or message_type=="document":
                if isinstance(message_header,dict):
                    components.append({"type": "header", "parameters": [{'type':message_type, f"{message_type}":{"link": message_header['link'],"filename":message_header['filename']}}]})
                else:
                    components.append({"type": "header", "parameters": [{'type':message_type, f"{message_type}":{"link": message_header}}]})
                
            
            if body_params and len(body_params) > 0:
                components.append(
                    {"type": "body",
                        "parameters": [{"type": "text", "text": p} for p in body_params]
                    })
                
            if button_params and len(button_params)>0:
                if message_type== 'carousel':
                    cards_components=[]
                    for k in button_params:
                        if k['body_params'] and len(k['body_params']) > 0:
                            cards_components.append(
                                {"type": "body",
                                    "parameters": [{"type": "text", "text": p} for p in k['body_params']]
                                })
                        if k['message_type']=='image' or k['message_type']== "video" or message_type=="document":
                            cards_components.append({"type": "header", "parameters": [{"link": k['message_header']}]})
                        if k['button_params'] and len(k['button_params'])>0:
                            cards_components.extend([
                                {
                                    "type": "button",
                                    "sub_type": "quick_reply",
                                    "index": f"{i}",
                                    "parameters": [
                                        {
                                            "type": "payload",
                                            "payload": f"{kk}"
                                        }
                                    ]
                                } for i, kk in enumerate(k['button_params'])]
                            ) 
                        # cards.append(card_obj)
                    components.append({
                        "type":"CAROUSEL",
                        "cards":[{"card_index":i, "components": k} for i, k in enumerate(cards_components)]
                    })
                elif message_type=='order_status':
                    components.extend([
                        {
                         "type": "order_status",
                         "parameters": [json.loads(x) for x in button_params]
                     }
                ])
                elif message_type=='flow':
                    components.extend([
                        {
                            "type": "button",
                            "sub_type": "flow",
                            "index": f"{i}",
                            "parameters": [
                                {
                                    "type": "action",
                                    "action":{"flow_token": f"{k}"}
                                }
                            ]
                        } for i, k in enumerate(button_params)]
                    ) 
                else:
                    components.extend([
                        {
                            "type": "button",
                            "sub_type": "quick_reply" if 'url' not in k else "url",
                            "index": f"{i}",
                            "parameters": [
                                {
                                    "type": "payload",
                                    "payload": f"{k}".replace("url_","")
                                }
                            ]
                        } for i, k in enumerate(button_params)]
                    )

            request_body['template']['components']= components
        print(request_body)
        payload = json.dumps(request_body)
        if request_body['to']=='918112148070':
            print("payload",payload)
        print('hit')
        response = requests.post(url, headers=headers, data=payload)
        print(response.text)

        response_json = response.json()
        return response_json
    except:
        traceback.print_exc()
        return None









