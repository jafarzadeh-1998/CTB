from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.telegramHandler),
    path("set_webhook/", views.set_webhook, name="set-webhook"),
    path("get_webhook_info/", views.get_Webhook_info, name="set-webhook-info"),
    path("add_project/", views.addProject, name='add-project'),
    path("sendMessage", views.sendMessage, name="send-message"),
]