from django.contrib.auth import models as model
from django.db import models


class User(model.AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username
