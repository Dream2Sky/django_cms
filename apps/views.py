import json
import os
import copy

from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.base import View
from django.db import models
from django.forms import forms
from django.core import serializers

from apps import result


class CRUDView(View):
    def __init__(self, **kwargs):
        super(CRUDView, self).__init__(**kwargs)
        self.model = models.Model
        self.request_data = dict()
        self.forms = {
            "add": None,
            "edit": None
        }
        self.uniqueness_check_fields = []

        """
        url访问范例
        get:
            (list接口支持分页)
            app_name/model_name/list?page_index=1&page_size=100其他查询条件
            (all接口不支持分页)
            app_name/model_name/all
            app_name/model_name/count
        post:
            app_name/model_name/add
            app_name/model_name/edit
            app_name/model_name/delete
        """
        self.allow_action_names = {
            "get": [],
            "post": ["add", "edit", "delete","list", "all", "count"]
        }
        self.template_actions = []
        self.serializer = None
        self.default_page_size = 20
        self.default_page_index = 1
        self.relation_fields = []

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            if request.method.lower() not in self.allow_action_names:
                handler = self.http_method_not_allowed
            else:
                handler = self.action_dispatch(request)
        else:
            handler = self.http_method_not_allowed

        return handler(request, *args, **kwargs)

    def action_dispatch(self, request):
        self.handle_request_params(request)
        allow_actions = self.allow_action_names[request.method.lower()]
        if isinstance(allow_actions, str):
            allow_actions = [allow_actions]
        action = str(request.path.split("/")[-1])

        if action:
            action = action.lower()
            actions = allow_actions + self.template_actions
            if action not in actions:
                action = "get"

        return getattr(self, action, self.http_method_not_allowed)

    def handle_request_params(self, request):
        if request.method == "POST":
            if "application/json" in request.content_type:
                self.request_data = json.loads(request.body)
            elif "form-data" in request.content_type:
                self.request_data = request.POST.dict()
        elif request.method == "GET":
            self.request_data = request.GET.dict()

    def add(self, request, *args, **kwargs):
        filters = self.check_form_and_return_filters(request, "add")
        if "pk" in filters:
            del filters["pk"]
        if "id" in filters:
            del filters["id"]

        error_msg = ""
        obj = None

        if not self.check_uniqueness(filters):
            try:
                obj = self.model.objects.create(**filters)

                if self.serializer and callable(self.serializer):
                    obj = self.serializer(obj).data

            except Exception as ex:
                error_msg = str(ex)
        else:
            return result.invalid_param.description(f"数据重复，请勿重复创建")

        if error_msg:
            return result.unknown.description(f"创建{self.model.__name__}失败， {error_msg}")

        return result.success.set_data(obj)

    def edit(self, request, *args, **kwargs):
        filters = self.check_form_and_return_filters(request, "edit")
        pk = self.check_pk(filters)
        obj = None
        if self.model.objects.filter(pk=pk).exists():
            error_msg = None
            try:
                obj = self.model.objects.filter(pk=pk).update(**filters)
                if self.serializer and callable(self.serializer):
                    obj = self.serializer(obj).data
            except Exception as ex:
                error_msg = str(ex)

            if error_msg:
                return result.unknown.description(f"更新分类失败，{error_msg}")

            return result.success.set_data(obj)
        else:
            result.invalid_param.description(f"传递的分类id不存在")

    def delete(self, request, *args, **kwargs):
        filters = self.check_form_and_return_filters(request, "delete")
        pk = self.check_pk(filters)

        if self.model.objects.filter(pk=pk).exists():
            error_msg = None
            try:
                self.model.objects.filter(pk=pk).delete()
            except Exception as ex:
                error_msg = str(ex)

            if error_msg:
                return result.unknown.description(f"删除分类失败, {error_msg}")

            return result.success
        else:
            return result.invalid_param.description(f"不存在id为{pk}的分类，请重新输入")

    def _list(self, request, *args, **kwargs):
        page_index = int(self.request_data.pop("page_index", self.default_page_index))
        page_size = int(self.request_data.pop("page_size", self.default_page_size))

        if self.relation_fields:
            data_list = self.model.objects.select_related(*self.relation_fields).filter(**self.request_data).all()
        else:
            data_list = self.model.objects.filter(**self.request_data).all()
        paginator = Paginator(data_list, page_size, allow_empty_first_page=True)
        if page_index in paginator.page_range:
            page_obj = paginator.page(page_index)
            data_list = page_obj.object_list
        else:
            data_list = list()

        if self.serializer and callable(self.serializer):
            data_list = self.serializer(data_list, many=True).data

        return data_list

    def list(self, request, *args, **kwargs):
        data_list = self._list(request, *args, **kwargs)
        return result.success.set_data(data_list)

    def _count(self, request, *args, **kwargs):
        if self.relation_fields:
            data_count = self.model.objects.select_related(*self.relation_fields).filter(**self.request_data).count()
        else:
            data_count = self.model.objects.filter(**self.request_data).count()

        return data_count

    def count(self, request, *args, **kwargs):
        data_count = self._count(request, *args, **kwargs)
        return result.success.set_data(data_count)

    def all(self, request, *args, **kwargs):
        page_size = self._count(request, *args, **kwargs)
        self.request_data.update({
            "page_size": page_size,
            "page_index": 1
        })
        return result.success.set_data(self._list(request, *args, **kwargs))

    @staticmethod
    def check_pk(filters):
        if "pk" in filters:
            pk = filters.pop("pk")
        elif "id" in filters:
            pk = filters.pop("id")
        else:
            return result.invalid_param.description("参数id不能为空")

        return pk

    def check_form_and_return_filters(self, request, action):
        params = None
        if action in self.forms and self.forms[action] and isinstance(self.forms[action], forms.Form):
            form = self.forms[action]
            if callable(form):
                form = form(self.request_data)
                if not form.is_valid():
                    return result.invalid_param.description(form.get_errors())
                params = form.clean_data

        if params is None:
            if self.request_data is None:
                return result.invalid_param.description("传递的参数为空")
            params = dict()
            for k, v in self.request_data.items():
                params[k] = v

        kwargs = dict()
        for key, value in params.items():
            kwargs[key] = value

        return kwargs

    def check_uniqueness(self, filters):
        filters = copy.deepcopy(filters)
        if self.uniqueness_check_fields:
            filters = {k: v for k, v in filters.items() if k in self.uniqueness_check_fields}
            return self.model.objects.filter(**filters).exists()
        else:
            return False
