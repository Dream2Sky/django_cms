from django import forms

from apps.cms_auth.models import User
from apps.forms import FormMixin
from django.core.cache import cache


class LoginForm(forms.Form, FormMixin):
    telephone = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, min_length=6)
    remember = forms.BooleanField(required=False)


class RegisterForm(forms.Form, FormMixin):
    telephone = forms.CharField(max_length=50)
    username = forms.CharField(max_length=50, min_length=6)
    password = forms.CharField(max_length=50, min_length=6)
    confirm_password = forms.CharField(max_length=50, min_length=6)
    img_captcha = forms.CharField()

    def clean(self):
        clean_data = super(RegisterForm, self).clean()

        if clean_data.get("password") != clean_data.get("confirm_password"):
            raise forms.ValidationError("两次密码输入不一致")

        img_captcha = clean_data.get("img_captcha")
        img_captcha_cache = cache.get(img_captcha.lower())

        if not img_captcha_cache or img_captcha.lower() != img_captcha_cache.lower():
            raise forms.ValidationError("图形验证码输入错误")

        # 验证完了之后手动删掉缓存
        cache.delete(img_captcha.lower())

        if User.objects.filter(telephone=clean_data.get("telephone")).exists():
            raise forms.ValidationError("手机号已注册")

        return clean_data

