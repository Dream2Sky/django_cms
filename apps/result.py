import json
from collections import namedtuple

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

HttpCode = namedtuple("HttpCode", ("success", "invalid_params", "unauth", "unknown"))
http_code = HttpCode(200, 400, 401, 500)


class JsonResult(JsonResponse):
    def __init__(self, code=http_code.success, message="", data=None, **kwargs):
        self.code = code
        self.message = message
        self.data = data
        super(JsonResult, self).__init__(dict(code=self.code, message=self.message, data=self.data))

    def set_data(self, data):
        self.data = data
        old_data = json.loads(self.content)
        old_data.update({
            "data": self.data
        })
        self.content = json.dumps(old_data, cls=DjangoJSONEncoder, ensure_ascii=False)
        # 修改content之后，需要重新计算Content-Length, 否则会被截取返回内容
        self["Content-Length"] = len(self.content)
        return self

    def description(self, message):
        self.message = message
        old_data = json.loads(self.content)
        old_data.update({
            "message": self.message
        })
        self.content = json.dumps(old_data, cls=DjangoJSONEncoder, ensure_ascii=False)
        self["Content-Length"] = len(self.content)
        return self


# class BaseResult(object):
#
#     def __init__(self, code=http_code.success, message="", data=None, **kwargs):
#         self.code = code
#         self.message = message
#         self.data = data
#
#     def get_response(self):
#         return JsonResponse(dict(code=self.code, message=self.message, data=self.data))
#
#
# class Success(BaseResult):
#
#     def __init__(self):
#         super(Success, self).__init__()
#
#
# class Error(BaseResult):
#
#     def __init__(self, error_code):
#         super(Error, self).__init__(error_code)
#
#     def description(self, message):
#         self.message = message
#         return self.get_response()


success = JsonResult()
un_auth = JsonResult(code=http_code.unauth)
unknown = JsonResult(code=http_code.unknown)
invalid_param = JsonResult(code=http_code.invalid_params)
