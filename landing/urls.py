from django.urls import path
from rest_framework.routers import SimpleRouter

from .apps import LandingConfig
from .views import CourseCreateView, HomeView, LessonCreateView, CourseViewSet

app_name = LandingConfig.name

router = SimpleRouter()
router.register("courses", CourseViewSet)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("courses/create/", CourseCreateView.as_view(), name="course_create"),
    path("lessons/create/", LessonCreateView.as_view(), name="lesson_create"),
]

urlpatterns += router.urls