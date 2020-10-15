from django.db import models

import uuid

class User(models.Model):
    username = models.EmailField(verbose_name="ایمیل", max_length=256 )
    fullname = models.CharField(max_length=128, verbose_name="نام و نام خانوادگی")
    photo_url = models.CharField(verbose_name="آدرس پروفایل", max_length=128, default="https://chamranteam.ir/static/img/profile.jpg")

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
    def __str__(self):
        return self.english_title

class Task(models.Model):
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    project = models.ForeignKey(Project, verbose_name="پروژه مرتبط", on_delete=models.CASCADE)
    involved_user = models.ManyToManyField(User, verbose_name="کاربران درگیر", related_name="involved_user")
    deadline = models.DateField(verbose_name="تاریخ پایان", auto_now=False, auto_now_add=False, null=True, blank=True)
    
    def __str__(self):
        return self.project + " - " + str(self.deadline)
# -1001234159843
class Card(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=256)
    deadline = models.DateField(verbose_name="تاریخ پایان", auto_now=False, auto_now_add=False)
    project = models.ForeignKey(Project,verbose_name="پروژه مرتبط",on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.project.str() + " - " + self.deadline
    

class NewGroupId(models.Model):
    group_id = models.CharField(verbose_name="Id گروه تلگرام", max_length=256)
    suggested_project = models.UUIDField(verbose_name="کد پروژه پیشنهادی", null=True, blank=True)

    def __str__(self):
        return self.group_id

class GroupId(models.Model):
    group_id = models.CharField(verbose_name="Id گروه تلگرام", max_length=256, null=True)
    project = models.ForeignKey(Project, verbose_name="پروژه مرتبط", on_delete=models.CASCADE)

    def __str__(self):
        return self.group_id + str(self.project)