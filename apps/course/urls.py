from django.urls import path

from apps.course import views

app_name = "course"

urlpatterns = [
    path("", views.index, name="index"),
    path("<course_id>", views.details, name="details")
]
