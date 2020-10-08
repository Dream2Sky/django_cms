from django.urls import path
from apps.cms_auth.views import login_view, logout_view, img_captcha, register_view

app_name = "cms_auth"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("get_captcha/", img_captcha, name="get_captcha")
]
