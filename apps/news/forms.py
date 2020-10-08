from django import forms
from apps.forms import FormMixin
from apps.news.models import Comment


class PublishCommentForm(FormMixin, forms.ModelForm):
    news_id = forms.IntegerField()

    class Meta:
        model = Comment
        exclude = ["author", "news", "pub_time"]
