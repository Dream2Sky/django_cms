from django.urls import path, re_path

from apps.news import views

app_name = "news"

urlpatterns = [
    path("", views.index, name="index"),
    path("<news_id>", views.details, name="news_detail"),
    path("list/", views.news_list, name="news_list"),
    re_path("comment/(?P<action>(add|edit|delete))", views.CommentCRUDView.as_view(), name="comment")
]
