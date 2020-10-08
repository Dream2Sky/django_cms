from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from shortuuidfield import ShortUUIDField


class UserManager(BaseUserManager):

    def _create_user(self, telephone, username, password, **kwargs):
        if not telephone or not username or not password:
            raise ValueError("请正确传递参数")

        user = self.model(telephone=telephone, username=username, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, telephone, username, password, **kwargs):
        kwargs["is_superuser"] = False
        return self._create_user(telephone, username, password, **kwargs)

    def create_superuser(self, telephone, username, password, **kwargs):
        kwargs["is_superuser"] = True
        return self._create_user(telephone, username, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    uid = ShortUUIDField(primary_key=True)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=False)
    telephone = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 被定义为username_field的字段必须设置为唯一
    USERNAME_FIELD = "telephone"
    REQUIRED_FIELDS = ["username"]
    EMAIL_FIELD = "email"

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
