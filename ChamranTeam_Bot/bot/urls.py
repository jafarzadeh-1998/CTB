from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.telegramHandler),
    path("set_webhook/", views.set_webhook, name="set-webhook"),
    path("get_webhook_info/", views.get_Webhook_info, name="set-webhook-info"),
    path("add_project/", views.addProject, name='add-project'),
    path("update_user/", views.updateUser, name="update_user"),
    path("add_task/", views.addTask, name="add-task"),
    path("add_card/", views.addCard, name="add-card"),
    path("sendMessage", views.sendMessage, name="send-message"),
]