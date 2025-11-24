from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Бизнес-правило платформы: редактировать курс/урок может только его автор.
    DRF вызывает has_object_permission на каждую операцию записи.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            getattr(request.user, "is_instructor", False) or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "instructor"):
            return obj.instructor == request.user
        if hasattr(obj, "course"):
            return obj.course.instructor == request.user
        return False


class CourseViewSet(viewsets.ModelViewSet):
    """
    Полноценный CRUD для курсов.

    Основные моменты:
    - queryset динамически фильтруется в get_queryset
    - permissions зависят от action
    - дополнительный action lessons возвращает вложенные уроки
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = Course.objects.select_related("instructor").prefetch_related("lessons")
        if not user.is_authenticated or not user.is_staff:
            # Анонимам и студентам показываем только опубликованные курсы
            filter_kwargs = {"is_published": True}
            if user.is_authenticated:
                # Инструктор видит свои черновики + общую витрину
                return base_qs.filter(Q(**filter_kwargs) | Q(instructor=user))
            return base_qs.filter(**filter_kwargs)
        return base_qs

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [permissions.IsAuthenticated(), IsInstructorOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if not self.request.user.is_instructor:
            raise PermissionDenied("Создавать курсы могут только инструкторы.")
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def lessons(self, request, pk=None):
        """
        Nested-эндпоинт /courses/<id>/lessons/ показывает уроки конкретного курса.
        """

        course = self.get_object()
        lessons = course.lessons.filter(is_published=True)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    """
    CRUD для уроков. Мы переопределяем get_queryset, чтобы скрыть неопубликованные
    данные от анонимных пользователей, и perform_create, чтобы проверять автора курса.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        base_qs = Lesson.objects.select_related("course", "course__instructor")
        if not user.is_authenticated:
            return base_qs.filter(is_published=True, course__is_published=True)
        if user.is_staff:
            return base_qs
        # Инструктор видит все свои уроки вне зависимости от публикации
        return base_qs.filter(
            Q(is_published=True, course__is_published=True) | Q(course__instructor=user)
        )

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [permissions.IsAuthenticated(), IsInstructorOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if not self.request.user.is_instructor:
            raise PermissionDenied("Создавать уроки могут только инструкторы.")
        course = serializer.validated_data.get("course")
        if course.instructor != self.request.user:
            raise PermissionDenied("Добавлять уроки можно только в свои курсы.")
        serializer.save()
