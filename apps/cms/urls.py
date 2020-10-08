from django.urls import path, re_path
from apps.cms.views import index, NewsCategoryListView, NewsCategoryListView2, NewsCategoryAddView, \
    NewsCategoryEditView, NewsCategoryDeleteView, NewsCategoryCURDView, NewsCURDView, upload_file

app_name = "cms"

urlpatterns = [
    path("", index, name="index"),
    path("news_category/", NewsCategoryListView.as_view(), name="new_category_list"),
    path("news_category2/", NewsCategoryListView2.as_view(), name="new_category_list2"),
    path("add_news_category/", NewsCategoryAddView.as_view(), name="add_news_category"),
    path("edit_news_category/", NewsCategoryEditView.as_view(), name="edit_news_category"),
    path("delete_news_category/", NewsCategoryDeleteView.as_view(), name="delete_news_category"),
    re_path(r"news_category/(?P<action>(add|edit|delete))", NewsCategoryCURDView.as_view(), name="new_category_crud"),
    re_path(r"news/(?P<action>(all|list|count|add|edit|delete|init_new))", NewsCURDView.as_view(), name="news"),
    path("upload_file/", upload_file, name="upload_file")
]
