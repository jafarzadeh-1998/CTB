from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date

from persiantools.jdatetime import JalaliDate

from . import models
from .config import bot_token, URL, SECURITY_CODE
import telegram
import re, uuid ,json

global bot
global TOKEN
TOKEN=bot_token
bot = telegram.Bot(token=TOKEN)

def gregorian_to_numeric_jalali(date):
    if date:
        j_date = JalaliDate(date)
        return str(j_date.year) + '/' + str(j_date.month) + '/' + str(j_date.day)
    else:
        return "نا مشخص"

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
    try:
        projectId = update.inline_query.query
    except:
        raise Exception()
    # response = requests.get("https://chamranteam.ir/api/project_name/{}".format(projectId))
    try:
        project = models.Project.objects.get(code=projectId)
    except:
        print("There isn't any project with this code : {}".format(projectId))
        return
    query = update.inline_query.query
    print("-----PROJECT----- : ",project)
    results = [
        telegram.InlineQueryResultArticle(
            id=uuid.uuid4(),
            title=str(project.industry_creator),
            description=project.persian_title,
            thumb_url=project.industry_creator.photo_url,
            input_message_content=telegram.InputTextMessageContent(
                project.persian_title)),]
    update.inline_query.answer(results, cache_time=15)
    return

def myColleagueHandler(chat_id):
    project = models.Project.objects.get(group_id=chat_id)
    context = ""
    context += "مرکز پژوهشی : \n\t{}\n".format(project.industry_creator.fullname)
    context += "اساتید : \n"
    for expert in project.expert_accepted.all():
        context += "\t{}\n".format(expert.fullname)
    context += "پژوهشگران : \n"
    for researcher in project.researcher_accepted.all():
        context += "\t{}\n".format(researcher.fullname)
    bot.sendMessage(chat_id=chat_id, text=context)


def allTaskHandler(chat_id):
    return

def startHandler(chat_id):
    bot_welcome = """
       به بات تلگرامی چمران تیم خوش آمدید.
       """
    bot.sendMessage(chat_id=chat_id, text=bot_welcome)
    return HttpResponse('ok')

@csrf_exempt
def telegramHandler(request):
   # retrieve the message in JSON and then transform it to Telegram object
    if request.method == "GET":
       return HttpResponse("GET Method is OK")
    update = telegram.Update.de_json(json.loads(request.body), bot)
    # print(update)
    try:
        inlineQuery(update)
        return HttpResponse('ok')
    except Exception as exc:
        pass
        # print("---------------------------------------+++++++++++++++++++++++++++++++++")
        # print(exc)
        # return HttpResponse('ok')
    try:
        chat_id = update.message.chat.id
        msg_id = update.message.message_id
    except:
        return HttpResponse("ok")

    # Telegram understands UTF-8, so encode text for unicode compatibility    
    text = update.message.text.encode('utf-8').decode()
    if update.message.entities:
        if update.message.entities[0].type == "bot_command":
            command = text[update.message.entities[0].offset:update.message.entities[0].offset+update.message.entities[0].length]
            if text == "/start":
                startHandler(chat_id=chat_id)
            elif text == "/all_task":
                allTaskHandler(chat_id=chat_id)
            elif text == "/my_colleague":
                myColleagueHandler(chat_id=chat_id)
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
        pass
        # try:
        #     # clear the message we got from any non alphabets
        #     text = re.sub(r"\W", "_", text)
        #     url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
        #     # reply with a photo to the name the user sent,
        #     # note that you can send photos by url and telegram will fetch it for you
        #     bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
        # except Exception:
        #     bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)

    return HttpResponse('ok')


@csrf_exempt
def sendMessage(request):
    inputData = json.loads(request.body)
    if inputData['securityCode'] == SECURITY_CODE:
        project = models.Project.objects.get(id=inputData['id'])
        bot.sendMessage(chat_id=project.group_id, text=inputData['message'])
        return HttpResponse("OK")
    else:
        return HttpResponse("FUCK U!:P")


def add_user(userInfo):
    return models.User.objects.get_or_create(username=userInfo['username'],
                                            fullname=userInfo['fullname'],
                                            photo_url=userInfo['photo_url'],
                                            )[0]
@csrf_exempt
def addProject(request):
    inputData = json.loads(request.body)
    industry = add_user(inputData["industry"])
    projectInfo = inputData['project']
    project = models.Project.objects.create(id=projectInfo["id"],
                                            persian_title=projectInfo["persian_title"],
                                            english_title=projectInfo["english_title"],
                                            code=projectInfo["code"],
                                            industry_creator=industry
                                            )
    for expertInfo in inputData['experts']:
        project.expert_accepted.add(add_user(expertInfo))

    for researcherInfo in inputData['researchers']:
        project.researcher_accepted.add(add_user(researcherInfo))

    return HttpResponse("OK")
    # return JsonResponse(data={'success': "success"})


@csrf_exempt
def updateUser(request):
    inputData = json.loads(request.body)
    user = add_user(inputData)
    project = models.Project.objects.get(id=inputData['projectId'])
    if inputData['typeUser'] == 'expert':
        project.expert_accepted.add(user)
    elif inputData['typeUser'] == 'researcher':
        project.researcher_accepted(user)

    return HttpResponse("OK")


@csrf_exempt
def addTask(request):
    try:
        inputData = json.loads(request.body)
        print("----------------------ADD TASK-------------------------")
        print(inputData)
        project = models.Project.objects.get(id=inputData["id"])
        newTask = models.Task.objects.create(description=inputData['description'],
                                            project=project,
                                            deadline=parse_date(inputData['deadline']))
        involved_user = ""
        for username in inputData['involved_user']:
            user = models.User.objects.get(username=username)
            newTask.involved_user.add(user)
            involved_user += user.fullname + "\n"

        text = """وظیفه {title} به {involved_user} محول شده و لازم است تا تاریخ {deadline} انجام شود.
برای اطلاعات بیشتر می‌توانید دکمه «مشاهده پروژه» در زیر این پیام را بزنید. """.\
                format({"title":newTask.description,
                        "involved_user":involved_user,
                        "deadline": gregorian_to_numeric_jalali(newTask.deadline)})
        bot.sendMessage(chat_id=project.group_id, text=text)
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR HAPPEND", status=503)

@csrf_exempt
def addCard(request):
    try:
        inputData = json.loads(request.body)
        print("----------------------ADD CARD-------------------------")
        print(inputData)
        project = models.Project.objects.get(id=inputData['id'])
        newCard = models.Card.objects.create(title=inputData['title'],
                                            project=project,
                                            deadline=gregorian_to_numeric_jalali(inputData['deadline']),)
        text = "فاز {title} به پروژه اضافه شده است و لازم است تا تاریخ {deadline} انجام شود.".\
            format({"title": newCard.title, "deadline": newCard.deadline})
        bot.sendMessage(chat_id=project.group_id, text=text)
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR HAPPEND", status=503)


# {'update_id': 743953184,
#  'message': {
#      'message_id': 208,
#      'date': 1602089767,
#      'chat': {
#          'id': -408071125,
#          'type': 'group',
#          'title': 'Test',
#          'all_members_are_administrators': True
#          },
#      'text': 'خهه',
#      'entities': [],
#      'caption_entities': [], 
#      'photo': [], 
#      'new_chat_members': [], 
#      'new_chat_photo': [], 
#      'from': {
#          'id': 271373138, 
#          'first_name': 'Ali', 
#          'is_bot': False, 
#          'last_name': 'Jafarzadeh', 'username': 'ali_jafarzadeh1998', 'language_code':'en'}}}


# {'update_id': 743953185,
#  'message': {
#      'message_id': 209,
#      'date': 1602089796, 
#      'chat': {
#          'id': -408071125, 
#          'type': 'group', 
#          'title': 'Test', 
#          'all_members_are_administrators': True
#          },
#      'text': '/aloooooooooo',
#      'entities': [{'type': 'bot_command', 'offset': 0, 'length': 13}], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'from': {'id': 271373138, 'first_name': 'Ali', 'is_bot': False, 'last_name': 'Jafarzadeh', 'username': 'ali_jafarzadeh1998', 'language_code': 'en'}}}