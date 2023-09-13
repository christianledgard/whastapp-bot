from requests import post
import json
class WhatsappClient:
    def __init__(self, BASE_URL, AUTHORIZATION_TOKEN):
        self.BASE_URL = BASE_URL
        self.AUTHORIZATION_TOKEN = AUTHORIZATION_TOKEN
        self.HEADERS = {
            "Authorization": f"Bearer {self.AUTHORIZATION_TOKEN}",
            "Content-Type": "application/json"
        }

    def send_message(self, user_wa_id, message):
        #https://developers.facebook.com/docs/whatsapp/api/messages/text
        data = {
                "messaging_product": "whatsapp",
                "to": user_wa_id,
                "type": "text",
                "text": {
                    "body": message
                    }
                }
        response = post(f"{self.BASE_URL}/messages", json=data, headers=self.HEADERS)
        print(response.text)

    def send_interactive_messages(self, user_wa_id, action_id, message, footer):
        data = {
            "messaging_product":"whatsapp",
            "recipient_type": "individual",
            "to" :user_wa_id,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": message
                },
                "footer": {
                    "text": footer
                },
                "action": {
                "buttons": [
                    {
                    "type": "reply",
                        "reply": {
                            "id": json.dumps(action_id),
                            "title": "next definition" 
                        }
                    }
                ] 
                }
            }
        }
        response = post(f"{self.BASE_URL}/messages", json=data, headers=self.HEADERS)
        print(response.text)

    def options_menu(self, user_wa_id):
        #https://developers.facebook.com/docs/whatsapp/guides/interactive-messages/
        data = {
                "messaging_product":"whatsapp",
                "recipient_type":"individual",
                "to":user_wa_id,
                "type":"interactive",
                "interactive":{
                    "type":"list",
                    "body":{
                        "text":"¿Te puedo ayudar con alguna de estas opciones?"
                    },
                    "action":{
                        "button":"Menu",
                        "sections":[
                            {
                            "title":"Finanzas",
                            "rows":[
                                {
                                    "id":"gatos-mes-categoria",
                                    "title":"Gastos por categoría",
                                    "description":"Muestra los gastos por categoría"
                                },
                                {
                                    "id":"porcentaje-gastos",
                                    "title":"Porcentaje de gastos",
                                    "description":"Muestra el porcentaje de gastos"
                                }
                            ]
                            },
                            {
                            "title":"Datos Personales",
                            "rows":[
                                {
                                    "id":"mi-informacion",
                                    "title":"Obtener mi información",
                                    "description":"Muestra tu información personal"
                                }
                            ]
                            }
                        ]
                    }
                }
        }
        response = post(f"{self.BASE_URL}/messages", json=data, headers=self.HEADERS)
        print(response.text)

    def send_image(self, user_wa_id, image_url):
        #https://developers.facebook.com/docs/whatsapp/on-premises/reference/messages#section-object
        #https://developers.facebook.com/docs/whatsapp/on-premises/reference/media/media-id
        #https://developers.facebook.com/docs/whatsapp/on-premises/reference/media
        data = {
                "messaging_product": "whatsapp",
                "to": user_wa_id,
                "type": "image",
                "image": {
                    "link": image_url
                    }
                }
        response = post(f"{self.BASE_URL}/messages", json=data, headers=self.HEADERS)
        print(response.text)
