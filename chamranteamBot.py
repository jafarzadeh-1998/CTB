# token = "1314307251:AAFKpUau4FFXIAxBLh77qqvwgMIylnvVVyE"

import re
from flask import Flask, request
import telegram
from config import bot_token ,URL
import requests


global bot
global TOKEN
global COMMANDS
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

# URL = "https://chamranteam.pythonanywhere.com/"
app = Flask(__name__)

def startHandler(chat_id):
    bot_welcome = """
       به بات تلگرامی چمران تیم خوش آمدید.
       """
    bot.sendMessage(chat_id=chat_id, text=bot_welcome)
    return 'ok'

def projectNameHandler(chat_id, projectId):
    # response = requests.get("", params={"project_id": projectId})
    response = requests.get("https://chamranteam.ir/api/project_name/{}".format(projectId))
    if response.status_code == 200:
        projectInfo = response.json()
        bot.sendMessage(chat_id=chat_id, text=projectInfo['project_name'])
        return 'ok'
    bot.sendMessage(chat_id=chat_id, text="لطفا مجدداٌ تلاش کنید.")
    return "went wrong"

def searchUsernameHandler(chat_id, keyword):
    # response = requests.get("https://chamranteam.ir/api/", params={"keyword": keyword})
    response = requests.get("https://chamranteam.ir/api/search_username/{}".format(keyword))
    print(response.content)
    if response.status_code == 200:
        userInfo = response.json()
        print(userInfo)
        bot.sendMessage(chat_id=chat_id, text=userInfo['fullname'])
        return 'ok'
    bot.sendMessage(chat_id=chat_id, text="لطفا مجدداٌ تلاش کنید.")
    return "went wrong"


COMMANDS = {
    "/start": startHandler,
    "/project_name": projectNameHandler,
    "/search_username": searchUsernameHandler,
}

@app.route('/', methods=['POST', 'GET'])
def respond():
   # retrieve the message in JSON and then transform it to Telegram object   
   update = telegram.Update.de_json(request.get_json(force=True), bot)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id   

   # Telegram understands UTF-8, so encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()
   if "کد پروژه" in text:
       projectId = text[text.find(":")+2:]
       projectNameHandler(chat_id=chat_id, projectId=projectId)
   elif "شناسه" in text:
      keyword = text[text.find(":")+2:]
      searchUsernameHandler(chat_id=chat_id, keyword=keyword)

   # the first time you chat with the bot AKA the welcoming message
   elif text == "/start":
       startHandler(chat_id=chat_id)

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