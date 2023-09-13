from flask import Flask, request, jsonify, make_response
from whatsapp_client import WhatsappClient
import os
from urban_dictionary import UrbanDictionary
from dotenv import load_dotenv
import sqlite3
import json
import operator


app = Flask(__name__)
load_dotenv()
whatsapp_client = WhatsappClient(BASE_URL=os.environ['WHATSAPP_BASE_URL'], AUTHORIZATION_TOKEN=os.environ['WHATSAPP_AUTHORIZATION_TOKEN'])
con = sqlite3.connect('botdb.db', check_same_thread=False)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS definitions(user_wa_id, word, last_definition_number int, PRIMARY KEY (user_wa_id, word))")

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
        messages = data.get('entry')[0].get('changes')[0].get('value').get('messages')

        #Click on action button
        if(messages and len(messages)>0 and messages[0].get('context')):
            context = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('interactive').get('button_reply').get('id')
            context = json.loads(context)
            
            id = context.get('user_wa_id')
            word = context.get('word')

            res = cur.execute("SELECT last_definition_number FROM definitions WHERE user_wa_id=? AND word=?", (id, word)).fetchone()

            if res:
                word, definition, thumbs_up, thumbs_down = get_word_and_definition(word, res[0])
                whatsapp_client.send_interactive_messages(
                    user_wa_id=id,
                    message=f"📖 {res[0]+1}º definition:\n{definition}\n",
                    footer=f"👍 ({thumbs_up}) / 👎 ({thumbs_down})",
                    action_id={"user_wa_id": id, "word": word}
                )
                db_data = (res[0]+1, id, word)
                cur.execute("UPDATE definitions SET last_definition_number=? WHERE user_wa_id=? AND word=?", db_data)
                con.commit()
            else:
                whatsapp_client.send_message(user_wa_id=id, message=f"There is no more definitions of the word.")
                 

        #Listen to messages
        elif(messages):
            message = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get('body')
            id = data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('from')
            
            if('hello' in message.lower()):
                whatsapp_client.send_message(user_wa_id=id, message="Hi!")
            elif('menu' in message.lower()):
                whatsapp_client.options_menu(user_wa_id=id)
            elif('definition' in message.lower()):
                word = message.split(' ')[1:]
                word = ' '.join(word)
                whatsapp_client.send_message(user_wa_id=id, message=f"Searching {word} 🔍...")
                try:
                    word, definition, thumbs_up, thumbs_down = get_word_and_definition(word)
                    whatsapp_client.send_interactive_messages(
                        user_wa_id=id,
                        message=f"{word} 👀\n\n📖 Definition:\n{definition[:900]}\n",
                        footer=f"👍 ({thumbs_up}) / 👎 ({thumbs_down})",
                        action_id={"user_wa_id": id, "word": word}
                    )
                    db_data = (id, word, 1)
                    cur.execute("REPLACE INTO definitions VALUES(?, ?, ?)", db_data)
                    con.commit()
                except IndexError as e:
                    whatsapp_client.send_message(user_wa_id=id, message=f"There was no coincidences of the word {word} 🥲")
                except Exception as e:
                    print("ERROR: ", e)
                    whatsapp_client.send_message(user_wa_id=id, message=f"Error al buscar la definición de {word}")
            else:
                whatsapp_client.send_message(user_wa_id=id, message="Welcome to the chatbot! Write 'definition <word>' to get the urban dictionary definition of a word.")
        
        return make_response(jsonify({'status': 'Ok'}), 200)


def get_word_and_definition(word, definitionNumber = 0):
    urban_dictionary = UrbanDictionary()
    response = urban_dictionary.get_word(word)
    response = response.get('list')
    response.sort(key=operator.itemgetter('thumbs_up'), reverse=True)
    
    word = response[definitionNumber].get('word')
    definition = response[definitionNumber].get('definition')
    thumbs_up = response[definitionNumber].get('thumbs_up')
    thumbs_down = response[definitionNumber].get('thumbs_down')
    
    return (word, definition, thumbs_up, thumbs_down)

@app.route("/")
def hello_world():
    return "<h1 style='color:red'>Hello World!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)