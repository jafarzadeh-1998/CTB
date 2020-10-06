from django.shortcuts import render
from django.http import HttpResponse

import flask

from . import models
from .config import bot_token, URL
import telegram
import re, uuid

global bot
global TOKEN
TOKEN=bot_token
bot = telegram.Bot(token=TOKEN)

def set_webhook(request):
   s = bot.setWebhook(url='{}'.format(URL))
   if s:
       return HttpResponse("<h3>webhook setup ok</h3>")
   else:
       return HttpResponse("<h3>webhook setup failed</h3>")

def get_Webhook_info(request):
    g = bot.getWebhookInfo()
    if g:
        return HttpResponse("<h3>webhook url : {}</h3>".format(g['url']))
    else:
       return HttpResponse("<h3>get webhook Information failed</h3>")

def inlineQuery(update):
    projectId = update.inline_query.query
    print(projectId)
    response = requests.get("https://chamranteam.ir/api/project_name/{}".format(projectId))
    if response.status_code == 200:
        projectInfo = response.json()
        if projectInfo['creator_photo'] is not "None":
            projectInfo['creator_photo'] = "https://chamranteam.ir" + projectInfo['creator_photo']
        query = update.inline_query.query
        results = [
            telegram.InlineQueryResultArticle(
                id=uuid.uuid4(),
                title=projectInfo['creator'],
                description=projectInfo['project_name'],
                thumb_url=projectInfo['creator_photo'],
                input_message_content=telegram.InputTextMessageContent(
                    projectInfo['project_name'])),]
        update.inline_query.answer(results, cache_time=15)
    else:
        print(response.json())
    return

def startHandler(chat_id):
    bot_welcome = """
       به بات تلگرامی چمران تیم خوش آمدید.
       """
    bot.sendMessage(chat_id=chat_id, text=bot_welcome)
    return 'ok'


def telegramHandler():
   # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(flask.request.get_json(force=True), bot)
    try:
        inlineQuery(update)
        return 'ok'
    except:
        pass
        # print(update)
        # return 'ok'
    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    if "کد پروژه" in text:
        projectId = text[text.find(":")+2:]
        # projectNameHandler(chat_id=chat_id, projectId=projectId)
    elif "شناسه" in text:
        keyword = text[text.find(":")+2:]
        # searchUsernameHandler(chat_id=chat_id, keyword=keyword)

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
            bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)

    return 'ok'


def add_user(userInfo):
    return models.User.objects.get_or_create(username=userInfo['username'],
                                            fullname=userInfo['fullname'],
                                            photo_url=userInfo['photo_url'],
                                            )[0]

def addProject(request):
    industry = add_user(request.POST["industry"])
    projectInfo = request.POST['project']
    project = models.Project.object.create(id=projectInfo["id"],
                                            persian_title=projectInfo["persian_title"],
                                            english_title=projectInfo["english_title"],
                                            code=projectInfo["code"],
                                            industry_creator=industry
                                            )
    for expertInfo in request.POST['experts']:
        project.expert_accepted.add(add_user(expertInfo))

    for researcherInfo in request.POST['researchers']:
        project.researcher_accepted.add(add_user(researcherInfo))
        
    return HttpResponse("OK")
    # return JsonResponse(data={'success': "success"})

def sendMessage(request):
    if request['code'] == "":
        project = models.Project.objects.get(id=request.POST['id'])
        bot.sendMessage(chat_id=project.group_id, text=request.POST['message'])
        return HttpResponse("OK")
    else:
        return HttpResponse("FUCK U!:P")
