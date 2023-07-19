from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=150,
                                unique=True,
                                blank=False,
                                null=False,
                                verbose_name='Логин')
    email = models.EmailField(max_length=254,
                              unique=True,
                              blank=False,
                              null=False,
                              verbose_name='Email')
    first_name = models.CharField(max_length=150,
                                  blank=False,
                                  null=False,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150,
                                 blank=False,
                                 null=False,
                                 verbose_name='Фамилия')

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
