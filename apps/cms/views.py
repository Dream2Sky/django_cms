import json
import os
import random
import uuid
from datetime import datetime

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.base import View

from django.core import serializers
from django.conf import settings

from apps import result
from apps.cms.forms import NewsCreateForm, NewsCategoryEditForm
from apps.news.models import NewsCategory, News
from apps.news.serializers import NewsSerializer
from apps.views import CRUDView


@staff_member_required(login_url="index")
def index(request):
    return render(request, "cms/index.html")


class NewsCategoryListView(ListView):
    model = NewsCategory
    template_name = "cms/news_category.html"
    context_object_name = "categories"


class NewsCategoryListView2(View):

    def get(self, request, *args, **kwargs):
        context = dict(categories=NewsCategory.objects.all())
        print(serializers.serialize("json", list(context)))
        return render(request, template_name="cms/news_category.html", context=context)


class NewsCategoryAddView(View):

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        if NewsCategory.objects.filter(name=name).exists():
            return result.invalid_param.description("分类已存在，请重新输入")

        error_msg = None
        try:
            NewsCategory.objects.create(name=name)
        except Exception as ex:
            error_msg = str(ex)

        if error_msg:
            return result.unknown.description(f"添加分类失败：{error_msg}")
        return result.success


class NewsCategoryEditView(View):

    def post(self, request, *args, **kwargs):
        form = NewsCategoryEditForm(request.POST)
        if form.is_valid():
            pk = form.cleaned_data.get("pk")
            name = form.cleaned_data.get("name")

            if NewsCategory.objects.filter(pk=pk).exists():
                error_msg = None
                try:
                    pk_obj = NewsCategory.objects.filter(pk=pk).update(name=name)
                except Exception as ex:
                    error_msg = str(ex)

                if error_msg:
                    return result.unknown.description(f"更新分类失败，{error_msg}")

                return result.success
            else:
                result.invalid_param.description(f"传递的分类id不存在")
        else:
            return result.invalid_param.description(form.get_errors())


class NewsCategoryDeleteView(View):

    def post(self, request, *args, **kwargs):
        pk = request.POST.get("pk")
        if NewsCategory.objects.filter(pk=pk).exists():
            error_msg = None
            try:
                NewsCategory.objects.filter(pk=pk).delete()
            except Exception as ex:
                error_msg = str(ex)

            if error_msg:
                return result.unknown.description(f"删除分类失败, {error_msg}")

            return result.success

        else:
            return result.invalid_param.description(f"不存在id为{pk}的分类，请重新输入")


class NewsCategoryCURDView(CRUDView):
    model = NewsCategory
    forms = {
        "edit": NewsCategoryEditForm
    }
    #
    # def add(self, request, *args, **kwargs):
    #     name = request.POST.get("name")
    #     if NewsCategory.objects.filter(name=name).exists():
    #         return result.invalid_param.description("分类已存在，请重新输入")
    #
    #     error_msg = None
    #     try:
    #         NewsCategory.objects.create(name=name)
    #     except Exception as ex:
    #         error_msg = str(ex)
    #
    #     if error_msg:
    #         return result.unknown.description(f"添加分类失败：{error_msg}")
    #     return result.success
    #
    # def edit(self, request, *args, **kwargs):
    #     form = NewsCategoryEditForm(request.POST)
    #     if form.is_valid():
    #         pk = form.cleaned_data.get("pk")
    #         name = form.cleaned_data.get("name")
    #
    #         if NewsCategory.objects.filter(pk=pk).exists():
    #             error_msg = None
    #             try:
    #                 pk_obj = NewsCategory.objects.filter(pk=pk).update(name=name)
    #             except Exception as ex:
    #                 error_msg = str(ex)
    #
    #             if error_msg:
    #                 return result.unknown.description(f"更新分类失败，{error_msg}")
    #
    #             return result.success
    #         else:
    #             result.invalid_param.description(f"传递的分类id不存在")
    #     else:
    #         return result.invalid_param.description(form.get_errors())
    #
    # def delete(self, request, *args, **kwargs):
    #     pk = request.POST.get("pk")
    #     if NewsCategory.objects.filter(pk=pk).exists():
    #         error_msg = None
    #         try:
    #             NewsCategory.objects.filter(pk=pk).delete()
    #         except Exception as ex:
    #             error_msg = str(ex)
    #
    #         if error_msg:
    #             return result.unknown.description(f"删除分类失败, {error_msg}")
    #
    #         return result.success
    #
    #     else:
    #         return result.invalid_param.description(f"不存在id为{pk}的分类，请重新输入")


class NewsCURDView(CRUDView):
    
    def __init__(self, **kwargs):
        super(NewsCURDView, self).__init__(**kwargs)
        self.model = News
        self.template_actions = ["init_new"]

        self.forms = {
            "add": NewsCreateForm
        }
        self.serializer = NewsSerializer
        self.relation_fields = ["category", "author"]

    def init_new(self, request, *args, **kwargs):
        context = dict(categories=NewsCategory.objects.all())
        return render(request, template_name="cms/write_news.html", context=context)

    def add(self, request, *args, **kwargs):
        filters = self.check_form_and_return_filters(request, "add")
        category_id = filters.get("category")
        category = NewsCategory.objects.get(pk=category_id)
        filters["category"] = category
        filters["author"] = request.user

        if "pk" in filters:
            del filters["pk"]
        if "id" in filters:
            del filters["id"]

        error_msg = ""
        obj = None
        if not self.model.objects.filter(**filters).exists():
            try:
                obj = self.model.objects.create(**filters)
            except Exception as ex:
                error_msg = str(ex)
        else:
            return result.invalid_param.description(f"数据重复，请勿重复创建")

        if error_msg:
            return result.unknown.description(f"创建{self.model.__name__}失败， {error_msg}")

        return result.success.set_data(dict(id=obj.id))


@require_POST
def upload_file(request):
    file = request.FILES.get("file")
    name = f"{str(uuid.uuid3(uuid.NAMESPACE_DNS, file.name))}{os.path.splitext(file.name)[1]}"
    with open(os.path.join(settings.MEDIA_ROOT, name), "wb") as fp:
        for chunk in file.chunks():
            fp.write(chunk)

    url = request.build_absolute_uri(f"{settings.MEDIA_URL}{name}")
    return result.success.set_data(dict(url=url))
