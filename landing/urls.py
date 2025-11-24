from django.urls import path

from .views import CourseCreateView, HomeView, LessonCreateView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("courses/create/", CourseCreateView.as_view(), name="course_create"),
    path("lessons/create/", LessonCreateView.as_view(), name="lesson_create"),
]