from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "course/course_index.html")


def details(request, course_id):
    return render(request, "course/course_detail.html")
