from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, LessonViewSet

router = DefaultRouter()
router.register(r"coursess", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")

urlpatterns = router.urls


