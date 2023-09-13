from flask import Flask, request, jsonify, make_response
from whatsapp_client import WhatsappClient
import os
from urban_dictionary import UrbanDictionary
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
whatsapp_client = WhatsappClient(BASE_URL=os.environ['WHATSAPP_BASE_URL'], AUTHORIZATION_TOKEN=os.environ['WHATSAPP_AUTHORIZATION_TOKEN'])

@app.route("/webhook", methods=['POST', 'GET'])
def webhook_whatsapp():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == os.environ['FB_VERIFY_TOKEN']:
            return request.args.get('hub.challenge')
        return "Wrong Verify Token"
    elif request.method == 'POST':
        data = request.get_json()
        print("Webhook")
        print(data)

        if(data.get('entry')[0].get('changes')[0].get('value').get('messages')):
            message = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get('body')
            id = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('from')
            
            if('hello' in message.lower()):
                whatsapp_client.send_message(user_wa_id=id, message="Hi!")
            elif('menu' in message.lower()):
                whatsapp_client.options_menu(user_wa_id=id)
            elif('definition' in message.lower()):
                word = message.split(' ')[1:]
                word = ' '.join(word)
                whatsapp_client.send_message(user_wa_id=id, message=f"Buscando la definición de {word}...")
                try:
                    urban_dictionary = UrbanDictionary()
                    response = urban_dictionary.get_word(word)
                    whatsapp_client.send_message(user_wa_id=id, message=f"Urban definition: {response.get('list')[0].get('definition')}")
                except:
                    whatsapp_client.send_message(user_wa_id=id, message=f"Error al buscar la definición de {word}")
            else:
                whatsapp_client.send_message(user_wa_id=id, message="Welcome to the chatbot! Write 'definition <word>' to get the urban dictionary definition of a word.")
        
        return make_response(jsonify({'status': 'Ok'}), 200)

@app.route("/")
def hello_world():
    return "<h1 style='color:red'>Hello World!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)