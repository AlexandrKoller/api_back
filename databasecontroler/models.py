from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
import os
import shutil

class User(AbstractUser):
    UserStorage = models.CharField(max_length=300, blank=True, verbose_name='Хранилище пользователя')
    SizeStorage = models.IntegerField(verbose_name='Размер хранилища', default=0,  blank=True,)
    FileCount = models.IntegerField(verbose_name='Количество файлов', default=0, blank=True,)
    
@receiver(post_save, sender=User)
def post_create_preparation(sender, instance=None, created=False, **kwargs):
    if created:
        instance.UserStorage = str(uuid4())
        instance.save()
        Token.objects.create(user=instance)

@receiver(pre_delete, sender=User)
def delete_user_storage(sender, instance=None, **kwargs):
    if os.path.isdir(f'{settings.MEDIA_ROOT}/documents/{instance.UserStorage}'):
        shutil.rmtree(f'{settings.MEDIA_ROOT}/documents/{instance.UserStorage}')

def user_directory_path(instance, filename):   
    return 'documents/{0}/{1}'.format(instance.FileOwner.UserStorage, str(uuid4())+'.'+filename.split('.')[1])  


class UserFile(models.Model):
    File = models.FileField(max_length=300, upload_to=user_directory_path)
    FileDescription = models.TextField(max_length=200, blank=True, verbose_name='Описание файла')
    DateUpload = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата загрузки файла')
    FileOwner = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец файла')
    DateLastDownLoad = models.DateTimeField(default=None, null=True, verbose_name='Дата последнего скачивания')
    Name = models.CharField(max_length=300, verbose_name='Имя файла')
    loadcode = models.CharField(blank=True, default=str(uuid4()), null=True, verbose_name='Код загрузки')
    def __str__(self) -> str:
        return f'{self.Name}'
    
@receiver(models.signals.post_delete, sender=UserFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.File:
        instance.FileOwner.FileCount = instance.FileOwner.FileCount - 1
        instance.FileOwner.SizeStorage = instance.FileOwner.SizeStorage - instance.File.size
        instance.FileOwner.save()
        if os.path.isfile(instance.File.path):
            os.remove(instance.File.path) 

@receiver(models.signals.post_save, sender=UserFile)
def auto_add_count_user_file(sender, instance, created, **kwargs):
    if created:
        user = instance.FileOwner
        user.FileCount = user.FileCount + 1
        user.SizeStorage = user.SizeStorage + instance.File.size
        user.save()
        
