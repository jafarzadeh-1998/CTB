# token = "1314307251:AAFKpUau4FFXIAxBLh77qqvwgMIylnvVVyE"

import re
from flask import Flask, request
import telegram
from config import bot_token ,URL


global bot
global TOKEN
TOKEN = "1314307251:AAFKpUau4FFXIAxBLh77qqvwgMIylnvVVyE"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def respond():
   # retrieve the message in JSON and then transform it to Telegram object   
   update = telegram.Update.de_json(request.get_json(force=True), bot)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id   

   # Telegram understands UTF-8, so encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()

   # the first time you chat with the bot AKA the welcoming message
   if text == "/start":
       # print the welcoming message
       bot_welcome = """
       به بات تلگرامی جمران تیم خوش آمدید.
       """
       # send the welcoming message
       bot.sendMessage(chat_id=chat_id, text=bot_welcome)

   else:
       try:
           # clear the message we got from any non alphabets
           text = re.sub(r"\W", "_", text)
           url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
           # reply with a photo to the name the user sent,
           # note that you can send photos by url and telegram will fetch it for you
           bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
       except Exception:
           # if things went wrong
           bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)

   return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
   s = bot.setWebhook(url='{}'.format(URL))
   if s:
       return "webhook setup ok"
   else:
       return "webhook setup failed"

@app.route("/get_webhook_info", methods=["POST", 'GET'])
def get_WebhookInfo():
    g = bot.getWebhookInfo()
    if g:
        return g['url']
    else:
       return "webhook setup failed"

if __name__ == '__main__':
   app.run(threaded=True, debug=True)