from django.db import models


class NewsCategory(models.Model):
    """
    新闻分类
    """
    name = models.CharField(max_length=50)

    class Meta(object):
        db_table = "news_category"


class News(models.Model):
    title = models.CharField(max_length=200)
    desc = models.CharField(max_length=200)
    thumbnail = models.URLField()
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey('NewsCategory', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey('cms_auth.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-pub_time']


class Comment(models.Model):
    content = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    news = models.ForeignKey("News", on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey("cms_auth.User", on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pub_time']
