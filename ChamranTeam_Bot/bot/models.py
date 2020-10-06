from django.db import models

import uuid

class User(models.Model):
    username = models.EmailField(verbose_name="ایمیل", )
    fullname = models.CharField(max_length=128, verbose_name="نام و نام خانوادگی")
    photo_url = models.CharField(verbose_name="آدرس پروفایل", max_length=128, default="None")

    def __str__(self):
        return self.username


class Project(models.Model):
    id = models.IntegerField(verbose_name="شناسه", primary_key=True)
    persian_title = models.CharField(max_length=256, verbose_name="عنوان فارسی پروژه")
    english_title = models.CharField(max_length=256, verbose_name="عنوان انگلیسی پروژه")
    code = models.UUIDField(verbose_name="کد پروژه", default=uuid.uuid4, unique=True)
    researcher_accepted = models.ManyToManyField(User, verbose_name="پژوهشگران پذبرفته شده",
                                            related_name="researchers_accepted", blank=True)
    expert_accepted = models.ManyToManyField(User, verbose_name="استاد پذیرفته شده",
                                        related_name="expert_accepted", blank=True)
    industry_creator = models.ForeignKey(User, on_delete=models.CASCADE,
                                         null=True, blank=True, verbose_name='شرکت '
                                                                             'صاحب '
                                                                             'پروژه')
    group_id = models.IntegerField(verbose_name="آیدی گروه", null=True, blank=True)
    def __str__(self):
        return self.english_title


{'update_id': 743952968,
  'message': {
        'message_id': 7871,
        'date': 1601872075,
        'chat': {
            'id': -1001430882225,
            'type': 'supergroup',
            'title': 'ChamranTeam™ Coders'
        },
        'text': 'لیست فیلدهایی که علی آقا می\u200cگیره کارت رو راه می\u200cاندازه؟',
        'entities': [],
        'caption_entities': [],
        'photo': [],
        'new_chat_members': [],
        'new_chat_photo': [],
        'delete_chat_photo': False,
        'group_chat_created': False,
        'supergroup_chat_created': False,
        'channel_chat_created': False,
        'from': {
            'id': 84588426,
            'first_name': 'Sepehr',
            'is_bot': False,
            'last_name': 'Metanat',
            'username': 'SepehrMetanat',
            'language_code': 'en'
        }
    }
}
{'update_id': 743952969, 'message': {'message_id': 7872, 'date': 1601872147, 'chat': {'id': -1001430882225, 'type': 'supergroup', 'title': 'ChamranTeam™ Coders'}, 'text': 'هم اون رو می خوام', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'from': {'id': 348489271, 'first_name': 'Reza', 'is_bot': False, 'last_name': 'Basereh', 'username': 'rezabasereh'}}}