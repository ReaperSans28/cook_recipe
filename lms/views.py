from django.db.models import Q
from rest_framework import permissions, viewsets, renderers, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Бизнес-правило платформы: редактировать курс/урок может только его автор.
    DRF вызывает has_object_permission на каждую операцию записи.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            getattr(request.user, "is_teacher", False) or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "teacher"):
            return obj.teacher == request.user
        if hasattr(obj, "course"):
            return obj.course.teacher == request.user
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
        base_qs = Course.objects.select_related("teacher").prefetch_related("lessons")
        if not user.is_authenticated or not user.is_staff:
            # Анонимам и студентам показываем только опубликованные курсы
            filter_kwargs = {"is_published": True}
            if user.is_authenticated:
                # Инструктор видит свои черновики + общую витрину
                return base_qs.filter(Q(**filter_kwargs) | Q(teacher=user))
            return base_qs.filter(**filter_kwargs)
        return base_qs

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [permissions.IsAuthenticated(), IsTeacherOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if not self.request.user.is_teacher:
            raise PermissionDenied("Создавать курсы могут только инструкторы.")
        serializer.save(teacher=self.request.user)

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
    renderer_classes = [
        renderers.JSONRenderer,
        renderers.BrowsableAPIRenderer,
        renderers.TemplateHTMLRenderer,
    ]

    def get_queryset(self):
        user = self.request.user
        base_qs = Lesson.objects.select_related("course", "course__teacher")

        # Для HTML представления возвращаем только опубликованные
        if hasattr(self.request, 'accepted_renderer') and self.request.accepted_renderer.format == 'html':
            return base_qs.filter(is_published=True, course__is_published=True)

        if not user.is_authenticated:
            return base_qs.filter(is_published=True, course__is_published=True)
        if user.is_staff:
            return base_qs
        return base_qs.filter(
            Q(is_published=True, course__is_published=True) | Q(course__teacher=user)
        )

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [permissions.IsAuthenticated(), IsTeacherOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        if not self.request.user.is_teacher:
            raise PermissionDenied("Создавать уроки могут только инструкторы.")
        course = serializer.validated_data.get("course")
        if course.teacher != self.request.user:
            raise PermissionDenied("Добавлять уроки можно только в свои курсы.")
        serializer.save()

    def get_lesson_context(self, lesson):
        """Вспомогательный метод для получения контекста урока"""
        previous_lesson = Lesson.objects.filter(
            course=lesson.course,
            order__lt=lesson.order,
            is_published=True,
            course__is_published=True
        ).order_by('-order').first()

        next_lesson = Lesson.objects.filter(
            course=lesson.course,
            order__gt=lesson.order,
            is_published=True,
            course__is_published=True
        ).order_by('order').first()

        def lesson_to_simple_dict(obj):
            if not obj:
                return None
            return {
                'id': obj.id,
                'title': obj.title,
                'order': obj.order,
                'url': f'/api/lessons/{obj.id}/'
            }

        lesson_dict = {
            'id': lesson.id,
            'title': lesson.title,
            'content': lesson.content,
            'video_url': lesson.video_url,
            'duration_minutes': lesson.duration_minutes,
            'order': lesson.order,
            'is_published': lesson.is_published,
            'created_at': lesson.created_at,
            'updated_at': lesson.updated_at,
            'course': {
                'id': lesson.course.id,
                'title': lesson.course.title,
            }
        }

        return {
            'lesson': lesson_dict,
            'previous_lesson': lesson_to_simple_dict(previous_lesson),
            'next_lesson': lesson_to_simple_dict(next_lesson)
        }

    @action(detail=True, methods=['get'],
            renderer_classes=[renderers.TemplateHTMLRenderer],
            url_path='html')
    def lesson_html(self, request, *args, **kwargs):
        """Endpoint для получения HTML представления урока"""
        lesson = self.get_object()

        if not lesson.is_published or not lesson.course.is_published:
            if not request.user.is_authenticated:
                raise PermissionDenied("Урок не найден или не опубликован")
            if not (request.user.is_staff or request.user == lesson.course.teacher):
                raise PermissionDenied("Урок не найден или не опубликован")

        context = self.get_lesson_context(lesson)
        return Response(context, template_name='lms/lesson_detail.html')

    def retrieve(self, request, *args, **kwargs):
        """
        Переопределяем метод retrieve для определения формата ответа
        """
        instance = self.get_object()

        accept_header = request.META.get('HTTP_ACCEPT', '')
        is_html_request = (
                request.accepted_renderer.format == 'html' or
                'text/html' in accept_header or
                request.query_params.get('format') == 'html'
        )

        if is_html_request and 'application/json' not in accept_header:
            if not instance.is_published or not instance.course.is_published:
                if not request.user.is_authenticated:
                    return Response(
                        {"detail": "Урок не найден или не опубликован"},
                        status=status.HTTP_404_NOT_FOUND,
                        template_name='lms/lesson_not_found.html'
                    )
                if not (request.user.is_staff or request.user == instance.course.teacher):
                    return Response(
                        {"detail": "Урок не найден или не опубликован"},
                        status=status.HTTP_404_NOT_FOUND,
                        template_name='lms/lesson_not_found.html'
                    )

            context = self.get_lesson_context(instance)
            return Response(context, template_name='lms/lesson_detail.html')

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
