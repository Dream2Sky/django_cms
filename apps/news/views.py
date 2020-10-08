from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from apps import result
from apps.cms_auth.models import User
from apps.news.forms import PublishCommentForm
from apps.news.models import News, NewsCategory, Comment
from apps.news.serializers import NewsSerializer, CommentSerializer
from apps.views import CRUDView


def index(request):
    newses = News.objects.select_related("author", "category").all()[0: settings.NEWS_PAGE_SIZE]
    categories = NewsCategory.objects.all()
    context = {
        "newses": newses,
        "categories": categories
    }
    return render(request, 'news/index.html', context=context)


def details(request, news_id):
    news = News.objects.select_related("author", "category").get(pk=news_id)
    context = {
        "news": news
    }
    return render(request, "news/news_detail.html", context=context)


def news_list(request):
    page = int(request.GET.get("page", 1))
    category_id = int(request.GET.get("category_id"), 0)

    start = (page - 1) * settings.NEWS_PAGE_SIZE
    end = start + settings.NEWS_PAGE_SIZE

    if category_id != 0:
        newses = News.objects.select_related("category", "author").filter(category=category_id)[start: end]
    else:
        newses = News.objects.select_related("category", "author").all()[start: end]
    serializer = NewsSerializer(newses, many=True)

    newses = serializer.data
    return result.success.set_data(newses)


def publish_comment(request):
    form = PublishCommentForm(request)
    if form.is_valid():
        content = form.cleaned_data.get("content")
        news_id = form.cleaned_data.get("news_id")
        news_info = News.objects.get(pk=news_id)
        Comment.objects.create(content=content, news=news_info, author=request.user)
        return result.success.set_data(content)
    else:
        return result.invalid_param.description("表单验证失败")


class CommentCRUDView(CRUDView):

    def __init__(self, **kwargs):
        super(CommentCRUDView, self).__init__(**kwargs)
        self.model = Comment
        self.forms = {
            "add": PublishCommentForm
        }
        self.serializer = CommentSerializer

    def check_form_and_return_filters(self, request, action):
        kwargs = super(CommentCRUDView, self).check_form_and_return_filters(request, action)
        default_fields = {
            "author": request.user,
            "news": News.objects.get(pk=kwargs.get("news_id"))
        }
        default_fields.update(kwargs)
        return default_fields
