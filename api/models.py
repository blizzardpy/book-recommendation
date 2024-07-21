from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username, password=None):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    class Meta:
        db_table = 'users'

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_admin(self):
        return self.is_superuser


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=50)

    class Meta:
        db_table = 'books'
        unique_together = ('title', 'author', 'genre')

    def __str__(self):
        return f'{self.title} by {self.author}'
