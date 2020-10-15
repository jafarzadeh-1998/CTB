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
    try:
        project = models.Project.objects.get(code=projectId)
    except:
        print("There isn't any project with this code : {}".format(projectId))
        return
    query = update.inline_query.query
    print("-----PROJECT----- : ",project)
    keyboard = [[telegram.InlineKeyboardButton("تایید", callback_data=str(project.code))],]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    results = [
        telegram.InlineQueryResultArticle(
            id=uuid.uuid4(),
            title=str(project.industry_creator),
            description=project.persian_title,
            thumb_url=project.industry_creator.photo_url,
            reply_markup=reply_markup,
            input_message_content=telegram.InputTextMessageContent(
                "آیا مایل به متصل کردن گروه به پروژه {} هستید؟".format(project.persian_title))),]
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

def addNewGroup(newMemberList, chat_id):
    for newMember in newMemberList:
        if newMember.username == "avatar_name_bot":
            models.NewGroupId.objects.create(group_id=str(chat_id))

def removeGroupHandler(removedMember, chat_id):
    if removedMember.username == "avatar_name_bot":
        try:
            group = models.NewGroupId.objects.get(group_id=str(chat_id))
            group.delete()
        except:
            try:
                group = models.GroupId.objects.get(group_id=str(chat_id))
                group.delete()
            except:
                pass

def stageGroupAndProject(message):
    for keyboardList in message.reply_markup.inline_keyboard:
        for keyboard in keyboardList:
            text = keyboard.text
            if text == "تایید":
                try:
                    gp = models.NewGroupId.objects.get(group_id=message.chat.id)
                    if gp.suggested_project is None:
                        gp.suggested_project = keyboard.callback_data
                        gp.save()
                except:
                    bot.send_message(chat_id=message.chat_id,
                                     text="لطفا در ابتدا ربات چمران تیم را به گروه مرتبط به پروژه اضافه کنید.")
            return HttpResponse("ok")

def addGroupToProject(callBack):
    code = callBack['data']
    gp = models.NewGroupId.objects.get(suggested_project=code)
    project = models.Project.objects.get(code=code)
    group = models.GroupId.objects.create(group_id=gp.group_id, project=project)
    gp.delete()
    bot.send_message(chat_id=group.group_id,
                        text="این گروه به پروژه {} متصل شد.".format(project.persian_title))
    return HttpResponse("ok")

def allTaskHandler(chat_id):
    return

def startHandler(chat_id):
    bot_welcome = """
       به ربات تلگرامی چمران تیم خوش آمدید.
       """
    bot.sendMessage(chat_id=chat_id, text=bot_welcome)
    return HttpResponse('ok')

@csrf_exempt
def telegramHandler(request):
    if request.method == "GET":
       return HttpResponse("GET Method is OK")
    update = telegram.Update.de_json(json.loads(request.body), bot)
    message = update.effective_message
    # print(update)
    # print("+++++++++++++=")
    if message is None:
        try:
            inlineQuery(update)
            return HttpResponse('ok')
        except Exception as exc:
            addGroupToProject(update.callback_query)
            return HttpResponse("ok")

    if message.reply_markup is not None:
        stageGroupAndProject(message)

    if len(message.new_chat_members):        
        addNewGroup(newMemberList=message.new_chat_members, chat_id=message.chat_id)
        return HttpResponse('ok')
    if message.left_chat_member is not None:
        removeGroupHandler(removedMember=message.left_chat_member, chat_id=message.chat_id)
        return HttpResponse("ok")
    try:
        chat_id = message.chat.id
        msg_id = message.message_id
    except:
        return HttpResponse("ok")

    text = message.text.encode('utf-8').decode()
    if message.entities:
        if message.entities[0].type == "bot_command":
            command = text[message.entities[0].offset:message.entities[0].offset+message.entities[0].length]
            if text == "/start":
                startHandler(chat_id=chat_id)
            elif text == "/all_task":
                allTaskHandler(chat_id=chat_id)
            elif text == "/my_colleague":
                myColleagueHandler(chat_id=chat_id)

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
        # print("----------------------ADD TASK-------------------------")
        # print(inputData)
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
        # print("----------------------ADD CARD-------------------------")
        # print(inputData)
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
