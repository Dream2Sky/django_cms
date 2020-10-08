from io import BytesIO

from django.contrib.auth import login, logout, authenticate
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .forms import LoginForm, RegisterForm
from apps import result
from django.shortcuts import redirect, reverse
from apps.utils.captcha.cms_captcha import Captcha
from .models import User


@require_POST
def login_view(request):
    form = LoginForm(request.POST)

    if form.is_valid():
        telephone = form.cleaned_data.get("telephone")
        password = form.cleaned_data.get("password")
        remember = form.cleaned_data.get("remember")

        # 使用authenticate 来验证用户名密码
        user = authenticate(request, username=telephone, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if remember:
                    # 设置session过期时间为两周
                    request.session.set_expiry(None)
                else:
                    # 不保存session，浏览器关闭立即清掉session
                    request.session.set_expiry(0)
                return result.success
            else:
                return result.un_auth.description("当前用户被冻结")
        else:
            return result.un_auth.description("用户名密码错误")
    else:
        return result.invalid_param.description(form.get_errors())


def logout_view(request):
    logout(request)
    return redirect(reverse("index"))

@require_POST
def register_view(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get("telephone")
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = User.objects.create_user(telephone=telephone, username=username, password=password)
        login(request, user)
        return result.success
    else:
        return result.unknown.description(form.get_errors())


def img_captcha(request):
    text, image = Captcha.gene_code()
    # BytesIO：相当于一个管道，用来存储图片的流数据
    out = BytesIO()
    # 调用image的save方法，将这个image对象保存到BytesIO中
    image.save(out, 'png')
    # 将BytesIO的文件指针移动到最开始的位置
    out.seek(0)

    response = HttpResponse(content_type='image/png')
    # 从BytesIO的管道中，读取出图片数据，保存到response对象上
    response.write(out.read())
    # out.tell()方法返回流中当前指针位置
    response['Content-length'] = out.tell()

    # 12Df：12Df.lower()
    cache.set(text.lower(), text.lower(), 5 * 60)

    return response
