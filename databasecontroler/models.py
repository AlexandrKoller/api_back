from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
import os

class User(AbstractUser):
    UserStorage = models.CharField(max_length=300, default=str(uuid4()), verbose_name='Хранилище пользователя')
    SizeStorage = models.IntegerField(verbose_name='Размер хранилища', default=0,  blank=True,)
    FileCount = models.IntegerField(verbose_name='Количество файлов', default=0, blank=True,)
    
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

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
        if os.path.isfile(instance.File.path):
            os.remove(instance.File.path) 

@receiver(models.signals.post_save, sender=UserFile)
def auto_add_count_user_file(sender, instance, **kwargs):
    if instance.File:
        user = instance.FileOwner
        print(type(user.FileCount))
        user.FileCount = user.FileCount + 1
        user.SizeStorage = user.SizeStorage + instance.File.size
        user.save()
        
